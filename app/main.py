import os
import socket
import httpx
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

async def get_az():
    try:
        async with httpx.AsyncClient(timeout=1.0) as client:
            resp = await client.get(
                "http://169.254.169.254/latest/meta-data/placement/availability-zone"
            )
            return resp.text
    except Exception:
        return os.getenv("AZ_OVERRIDE", "unknown")

@app.get("/", response_class=HTMLResponse)
async def root():
    az = await get_az()
    pod_ip = socket.gethostbyname(socket.gethostname())
    pod_name = os.getenv("POD_NAME", socket.gethostname())

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>tf-multi-account · Pod Info</title>
  <style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: #0f172a;
      color: #f1f5f9;
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
    }}
    .container {{ text-align: center; padding: 2rem; }}
    .badge {{
      display: inline-block;
      background: #1e293b;
      border: 1px solid #334155;
      border-radius: 9999px;
      padding: 0.25rem 1rem;
      font-size: 0.75rem;
      color: #94a3b8;
      margin-bottom: 1.5rem;
      letter-spacing: 0.1em;
      text-transform: uppercase;
    }}
    h1 {{ font-size: 2.5rem; font-weight: 700; margin-bottom: 2rem; }}
    h1 span {{ color: #6366f1; }}
    .cards {{
      display: flex;
      gap: 1.5rem;
      justify-content: center;
      flex-wrap: wrap;
      margin-bottom: 2rem;
    }}
    .card {{
      background: #1e293b;
      border: 1px solid #334155;
      border-radius: 0.75rem;
      padding: 1.5rem 2rem;
      min-width: 200px;
    }}
    .card-label {{
      font-size: 0.75rem;
      color: #64748b;
      text-transform: uppercase;
      letter-spacing: 0.1em;
      margin-bottom: 0.5rem;
    }}
    .card-value {{
      font-size: 1.25rem;
      font-weight: 600;
      color: #6366f1;
    }}
    .footer {{ color: #475569; font-size: 0.875rem; }}
  </style>
</head>
<body>
  <div class="container">
    <div class="badge">EKS · AWS · tf-multi-account</div>
    <h1>Hello from <span>dev</span></h1>
    <div class="cards">
      <div class="card">
        <div class="card-label">Availability Zone</div>
        <div class="card-value">{az}</div>
      </div>
      <div class="card">
        <div class="card-label">Pod IP</div>
        <div class="card-value">{pod_ip}</div>
      </div>
      <div class="card">
        <div class="card-label">Pod Name</div>
        <div class="card-value" style="font-size:0.95rem">{pod_name}</div>
      </div>
    </div>
    <p class="footer">Refresh to hit a different pod &amp; availability zone</p>
    <p class="footer" style="margin-top:0.5rem">Created by Maor Last</p>
  </div>
</body>
</html>"""

@app.get("/health")
async def health():
    return {"status": "ok"}
