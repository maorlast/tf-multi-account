import socket
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
def root():
    pod_ip = socket.gethostbyname(socket.gethostname())
    return f"<h1>Pod IP: {pod_ip}</h1>"

@app.get("/health")
def health():
    return {"status": "ok"}
