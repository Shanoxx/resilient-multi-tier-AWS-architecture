from flask import Flask, jsonify
import socket
import requests
import os

app = Flask(__name__)

def get_imds(path):
    """Fetch value from EC2 Instance Metadata Service v2."""
    try:
        # Step 1: get token (IMDSv2)
        token_resp = requests.put(
            "http://169.254.169.254/latest/api/token",
            headers={"X-aws-ec2-metadata-token-ttl-seconds": "21600"},
            timeout=2
        )
        token = token_resp.text

        # Step 2: fetch metadata
        resp = requests.get(
            f"http://169.254.169.254/latest/meta-data/{path}",
            headers={"X-aws-ec2-metadata-token": token},
            timeout=2
        )
        return resp.text
    except Exception:
        return "unavailable"

@app.route("/")
def index():
    hostname    = socket.gethostname()
    instance_id = get_imds("instance-id")
    az          = get_imds("placement/availability-zone")
    local_ip    = get_imds("local-ipv4")

    html = f"""<!DOCTYPE html>
<html lang="pl">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>EC2 Instance Info</title>
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: 'Courier New', monospace;
      background: #0d1117;
      color: #e6edf3;
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 2rem;
    }}
    .card {{
      background: #161b22;
      border: 1px solid #30363d;
      border-radius: 12px;
      padding: 2rem 2.5rem;
      max-width: 480px;
      width: 100%;
    }}
    .header {{
      display: flex;
      align-items: center;
      gap: 10px;
      margin-bottom: 1.5rem;
      padding-bottom: 1rem;
      border-bottom: 1px solid #30363d;
    }}
    .dot {{
      width: 10px; height: 10px;
      border-radius: 50%;
      background: #3fb950;
      box-shadow: 0 0 6px #3fb950;
    }}
    .header h1 {{ font-size: 1rem; color: #7d8590; letter-spacing: 0.05em; text-transform: uppercase; }}
    .row {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 0.6rem 0;
      border-bottom: 1px solid #21262d;
      gap: 1rem;
    }}
    .row:last-child {{ border-bottom: none; }}
    .label {{ color: #7d8590; font-size: 0.85rem; }}
    .value {{ color: #58a6ff; font-size: 0.9rem; font-weight: bold; text-align: right; }}
    .value.green {{ color: #3fb950; }}
    .value.orange {{ color: #d29922; }}
  </style>
</head>
<body>
  <div class="card">
    <div class="header">
      <div class="dot"></div>
      <h1>EC2 Instance</h1>
    </div>
    <div class="row">
      <span class="label">Hostname</span>
      <span class="value">{hostname}</span>
    </div>
    <div class="row">
      <span class="label">Instance ID</span>
      <span class="value">{instance_id}</span>
    </div>
    <div class="row">
      <span class="label">Availability Zone</span>
      <span class="value orange">{az}</span>
    </div>
    <div class="row">
      <span class="label">Private IP</span>
      <span class="value">{local_ip}</span>
    </div>
    <div class="row">
      <span class="label">Status</span>
      <span class="value green">healthy</span>
    </div>
  </div>
</body>
</html>"""
    return html

@app.route("/health")
def health():
    return jsonify({
        "status": "healthy",
        "hostname": socket.gethostname(),
        "instance_id": get_imds("instance-id"),
        "az": get_imds("placement/availability-zone"),
    }), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
