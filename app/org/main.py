import os
import socket
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/{full_path:path}")
def root(full_path: str):
    return JSONResponse({
        "service": "organization",
        "pod_ip": socket.gethostbyname(socket.gethostname()),
        "node_ip": os.getenv("NODE_IP", "unknown"),
    })
