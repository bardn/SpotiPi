#!/bin/bash

# Update package list and install required packages
sudo apt-get update
sudo apt-get install -y python3-pip python3-dev fbi python3-pillow

# Install Python packages from requirements.txt
pip3 install -r requirements.txt

# Get the current user and group
USER=$(whoami)
GROUP=$(id -gn)

# Download and run the rgb-matrix.sh script
curl -sSL https://raw.githubusercontent.com/adafruit/Raspberry-Pi-Installer-Scripts/master/rgb-matrix.sh -o rgb-matrix.sh
chmod +x rgb-matrix.sh
sudo ./rgb-matrix.sh

# Create systemd service file for SpotiPi
cat <<EOF | sudo tee /etc/systemd/system/spotipi.service
[Unit]
Description=SpotiPi Display Script
After=network.target

[Service]
ExecStart=/usr/bin/python3 /home/pi/SpotiPi/SpotiPi.py
WorkingDirectory=/home/pi/SpotiPi
StandardOutput=inherit
StandardError=inherit
Restart=always
User=$USER
Group=$GROUP

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd, enable and start the SpotiPi service
sudo systemctl daemon-reload
sudo systemctl enable spotipi.service
sudo systemctl start spotipi.service

echo "SpotiPi service setup complete."
echo "Do you want to reboot the system now to apply changes? (y/n)"
read -r REBOOT

if [ "$REBOOT" = "y" ] || [ "$REBOOT" = "Y" ]; then
    echo "Rebooting the system..."
    sudo reboot
else
    echo "You can manually reboot the system later to apply changes."
fi
