#!/bin/bash
# =======================================================
#  NEXUS GOLD — VPS Deploy Script
#  ใช้เมื่อพร้อมย้ายไป VPS
#  รัน: bash deploy_vps.sh
# =======================================================

echo "╔══════════════════════════════════════╗"
echo "║   NEXUS GOLD — VPS Deploy Script     ║"
echo "╚══════════════════════════════════════╝"
echo ""

# ── Step 1: Update system
echo "📦 Step 1: อัปเดต System..."
sudo apt update -y && sudo apt upgrade -y

# ── Step 2: Install Python
echo "🐍 Step 2: ติดตั้ง Python..."
sudo apt install python3 python3-pip python3-venv -y

# ── Step 3: Install dependencies
echo "📚 Step 3: ติดตั้ง Library..."
cd ~/nexus-gold-bot
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# ── Step 4: Create systemd service
echo "⚙️ Step 4: สร้าง Service..."
sudo tee /etc/systemd/system/nexusgold.service > /dev/null << EOF
[Unit]
Description=NEXUS GOLD Trading Bot
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=/home/$USER/nexus-gold-bot
ExecStart=/home/$USER/nexus-gold-bot/venv/bin/python bot.py
Restart=always
RestartSec=15
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# ── Step 5: Enable & start service
echo "🚀 Step 5: เปิดใช้งาน Service..."
sudo systemctl daemon-reload
sudo systemctl enable nexusgold
sudo systemctl start nexusgold

# ── Step 6: Open firewall port
echo "🔓 Step 6: เปิด Port 5000..."
sudo ufw allow 5000/tcp
sudo ufw allow ssh
sudo ufw --force enable

# ── Done
echo ""
echo "╔══════════════════════════════════════╗"
echo "║   ✅ Deploy สำเร็จ!                  ║"
echo "╠══════════════════════════════════════╣"
VPS_IP=$(curl -s ifconfig.me 2>/dev/null || echo "YOUR_VPS_IP")
echo "║   Dashboard: http://$VPS_IP:5000"
echo "║   ตรวจสถานะ: systemctl status nexusgold"
echo "║   ดู Log:    journalctl -u nexusgold -f"
echo "╚══════════════════════════════════════╝"
