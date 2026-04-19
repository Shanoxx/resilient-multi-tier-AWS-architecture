#!/bin/bash
set -xe
exec > >(tee /var/log/user-data.log | logger -t user-data -s 2>/dev/console) 2>&1

# Update system
dnf update -y

# Install dependencies
dnf install -y git python3 python3-pip

# Clone repository
cd /home/ec2-user
rm -rf app-repo
git clone https://github.com/Shanoxx/resilient-multi-tier-AWS-architecture.git app-repo

# Install Python packages
cd /home/ec2-user/app-repo/app
pip3 install --ignore-installed -r requirements.txt

# Create systemd service
cat > /etc/systemd/system/demoapp.service <<EOF
[Unit]
Description=EC2 Demo Flask App
After=network-online.target
Wants=network-online.target

[Service]
User=root
WorkingDirectory=/home/ec2-user/app-repo/app
ExecStart=/usr/bin/python3 /home/ec2-user/app-repo/app/app.py
Restart=always
RestartSec=20
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable demoapp
systemctl start demoapp
systemctl status demoapp --no-pager || true
curl -v http://127.0.0.1:5000/health || true

echo "=== User Data done. Flask app running on port 5000 ==="