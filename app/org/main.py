import os
import socket
import time
import psycopg2
from psycopg2.pool import SimpleConnectionPool
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
)

REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status_code"],
)
REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["endpoint"],
)

SERVICE_NAME = "org-service"
db_pool = None


@app.on_event("startup")
def startup():
    global db_pool
    for attempt in range(10):
        try:
            db_pool = SimpleConnectionPool(
                minconn=1, maxconn=5,
                host=os.getenv("POSTGRES_HOST", "postgres"),
                database=os.getenv("POSTGRES_DB", "clickdb"),
                user=os.getenv("POSTGRES_USER", "postgres"),
                password=os.getenv("POSTGRES_PASSWORD"),
            )
            break
        except psycopg2.OperationalError:
            if attempt == 9:
                raise
            time.sleep(3)
    conn = db_pool.getconn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS clicks (
                    id SERIAL PRIMARY KEY,
                    service VARCHAR(50) NOT NULL,
                    clicked_at TIMESTAMP DEFAULT NOW()
                )
            """)
        conn.commit()
    finally:
        db_pool.putconn(conn)


@app.middleware("http")
async def track_requests(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = time.time() - start
    REQUEST_COUNT.labels(request.method, request.url.path, response.status_code).inc()
    REQUEST_LATENCY.labels(request.url.path).observe(duration)
    return response


@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/org/click")
def click():
    conn = db_pool.getconn()
    try:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO clicks (service) VALUES (%s)", (SERVICE_NAME,))
            cur.execute("SELECT COUNT(*) FROM clicks WHERE service = %s", (SERVICE_NAME,))
            count = cur.fetchone()[0]
        conn.commit()
        return {"service": SERVICE_NAME, "clicks": count}
    finally:
        db_pool.putconn(conn)


@app.get("/org/clicks")
def get_clicks():
    conn = db_pool.getconn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM clicks WHERE service = %s", (SERVICE_NAME,))
            count = cur.fetchone()[0]
        return {"service": SERVICE_NAME, "clicks": count}
    finally:
        db_pool.putconn(conn)


@app.get("/{full_path:path}")
def root(full_path: str):
    return JSONResponse({
        "service": "organization",
        "pod_ip": socket.gethostbyname(socket.gethostname()),
        "node_ip": os.getenv("NODE_IP", "unknown"),
    })
