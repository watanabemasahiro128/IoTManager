#!/bin/bash

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
rm get-docker.sh

# Install pigpio
apt install -y pigpio
pip3 install pigpio

# Enable i2c
sudo sed -i -e "s/#dtparam=i2c_arm=on/dtparam=i2c_arm=on/" /boot/config.txt
echo "i2c-dev" >> /etc/modules

echo -e "Reboot after 30 seconds.\nPlease wait.\nPress Ctrl+C to cancel the reboot."
sleep 30s
reboot
