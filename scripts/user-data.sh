#!/bin/bash
set -e
exec > /var/log/user-data.log 2>&1

# Update system
yum update -y

# Install dependencies
yum install -y git python3 python3-pip

# Clone repository
cd /home/ec2-user
git clone https://github.com/Shanoxx/resilient-multi-tier-AWS-architecture.git app-repo

# Install Python packages
cd /home/ec2-user/app-repo/app
pip3 install -r requirements.txt

# Create systemd service
cat > /etc/systemd/system/demoapp.service <<EOF
[Unit]
Description=EC2 Demo Flask App
After=network.target

[Service]
User=root
WorkingDirectory=/home/ec2-user/app-repo/app
ExecStart=/usr/bin/python3 /home/ec2-user/app-repo/app/app.py
Restart=always
RestartSec=5
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
EOF

# Start service
systemctl daemon-reload
systemctl enable demoapp
systemctl start demoapp

echo "=== User Data done. Flask app running on port 5000 ==="