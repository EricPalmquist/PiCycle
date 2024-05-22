#!/usr/bin/env bash

# Automatic Installation Script
# Many thanks to the PiVPN project (pivpn.io) for much of the inspiration for this script
# Run from https://raw.githubusercontent.com/EricPalmquist/picycle/master/auto-install/install.sh
#
# Install with this command (from your Pi):
#
# curl https://raw.githubusercontent.com/EricPalmquist/picycle/master/auto-install/install.sh | bash
#
# NOTE: Pre-Requisites to run Raspi-Config first.  See README.md.

# Must be root to install
if [[ $EUID -eq 0 ]];then
    echo "You are root."
else
    echo "SUDO will be used for the install."
    # Check if it is actually installed
    # If it isn't, exit because the install cannot complete
    if [[ $(dpkg-query -s sudo) ]];then
        export SUDO="sudo"
        export SUDOE="sudo -E"
    else
        echo "Please install sudo."
        exit 1
    fi
fi

# Find the rows and columns. Will default to 80x24 if it can not be detected.
screen_size=$(stty size 2>/dev/null || echo 24 80)
rows=$(echo $screen_size | awk '{print $1}')
columns=$(echo $screen_size | awk '{print $2}')

# Divide by two so the dialogs take up half of the screen.
r=$(( rows / 2 ))
c=$(( columns / 2 ))
# If the screen is small, modify defaults
r=$(( r < 20 ? 20 : r ))
c=$(( c < 70 ? 70 : c ))

# Display the welcome dialog
whiptail --msgbox --backtitle "Welcome" --title "picycle Automated Installer" "This installer will transform your Single Board Computer into a connected cycle computer.  NOTE: This installer is intended to be run on a fresh install of Raspberry Pi OS Lite 32-Bit Bullseye or later." ${r} ${c}

# Starting actual steps for installation
clear
echo "*************************************************************************"
echo "**                                                                     **"
echo "**      Setting /tmp to RAM based storage in /etc/fstab                **"
echo "**                                                                     **"
echo "*************************************************************************"
echo "tmpfs /tmp  tmpfs defaults,noatime 0 0" | sudo tee -a /etc/fstab > /dev/null
clear
echo "*************************************************************************"
echo "**                                                                     **"
echo "**      Running Apt Update... (This could take several minutes)        **"
echo "**                                                                     **"
echo "*************************************************************************"
$SUDO apt update
clear
echo "*************************************************************************"
echo "**                                                                     **"
echo "**      Running Apt Upgrade... (This could take several minutes)       **"
echo "**                                                                     **"
echo "*************************************************************************"
$SUDO apt upgrade -y

# Install APT dependencies
clear
echo "*************************************************************************"
echo "**                                                                     **"
echo "**      Installing Dependencies... (This could take several minutes)   **"
echo "**                                                                     **"
echo "*************************************************************************"
$SUDO apt install python3-dev python3-pip python3-venv python3-rpi.gpio python3-scipy nginx git supervisor ttf-mscorefonts-installer redis-server libatlas-base-dev libopenjp2-7 -y

# Grab project files
# clear
# echo "*************************************************************************"
# echo "**                                                                     **"
# echo "**      Cloning picycle from GitHub...                                  **"
# echo "**                                                                     **"
# echo "*************************************************************************"
# cd /usr/local/bin
# Use a shallow clone to reduce download size
#$SUDO git clone --depth 1 https://github.com/EricPalmquist/picycle
# Replace the below command to fetch development branch
$SUDO git clone --depth 1 --branch development https://github.com/EricPalmquist/picycle

# Setup Python VENV & Install Python dependencies
clear
echo "*************************************************************************"
echo "**                                                                     **"
echo "**      Setting up Python VENV and Installing Modules...               **"
echo "**            (This could take several minutes)                        **"
echo "**                                                                     **"
echo "*************************************************************************"
echo ""
echo " - Setting Up picycle Group"
cd /usr/local/bin
$SUDO groupadd picycle 
$SUDO usermod -a -G picycle $USER 
$SUDO usermod -a -G picycle root 
# Change ownership to group=picycle for all files/directories in picycle 
$SUDO chown -R $USER:picycle picycle 
# Change ability for picycle group to read/write/execute 
$SUDO chmod -R 775 picycle/

echo " - Setting up VENV"
# Setup VENV
python -m venv --system-site-packages picycle
cd /usr/local/bin/picycle
source bin/activate 

echo " - Installing module dependencies... "
#Install module dependencies 
python -m pip install "flask==2.3.3" 
python -m pip install flask-mobility
python -m pip install flask-qrcode
python -m pip install flask-socketio
if ! python -c "import sys; assert sys.version_info[:2] >= (3,11)" > /dev/null; then
    echo "System is running a python version lower than 3.11, installing eventlet==0.30.2";
    python -m pip install "eventlet==0.30.2"
else
    echo "System is running a python version 3.11 or greater, installing latest eventlet"
    python -m pip install eventlet
fi      
python -m pip install gunicorn
python -m pip install gpiozero
python -m pip install redis
#python -m pip install uuid
#python -m pip install influxdb-client[ciso]
python -m pip install ratelimitingfilter
#python -m pip install "pillow>=9.2.0"
#python -m pip install psutil
#pip install adafruit-blinka adafruit-circuitpython-st7789
#pip install adafruit-circuitpython-display-text
python -m pip install luma.lcd
python -m pip install luma.core
#python -m pip install windows-curses
python -m pip install pynput
python -m pip install opencv-python

# Setup config.txt to enable busses 
clear
echo "*************************************************************************"
echo "**                                                                     **"
echo "**      Configuring config.txt                                         **"
echo "**                                                                     **"
echo "*************************************************************************"

Enable SPI - Needed for some displays
echo "dtparam=spi=on" | $SUDO tee -a /boot/config.txt > /dev/null
#Enable I2C - Needed for some displays, ADCs, distance sensors
#echo "dtparam=i2c_arm=on" | $SUDO tee -a /boot/config.txt > /dev/null
#echo "i2c-dev" | $SUDO tee -a /etc/modules > /dev/null

Setup backlight / power permissions if a DSI screen is installed  
clear
echo "*************************************************************************"
echo "**                                                                     **"
echo "**      Configuring Backlight UDEV Rules                               **"
echo "**                                                                     **"
echo "*************************************************************************"
echo 'SUBSYSTEM=="backlight",RUN+="/bin/chmod 666 /sys/class/backlight/%k/brightness /sys/class/backlight/%k/bl_power"' | $SUDO tee -a /etc/udev/rules.d/backlight-permissions.rules > /dev/null

## Setup nginx to proxy to gunicorn
clear
echo "*************************************************************************"
echo "**                                                                     **"
echo "**      Configuring nginx...                                           **"
echo "**                                                                     **"
echo "*************************************************************************"
# Move into install directory
cd /usr/local/bin/picycle/auto-install/nginx

# Delete default configuration
$SUDO rm /etc/nginx/sites-enabled/default

# Copy configuration file to nginx
$SUDO cp picycle.nginx /etc/nginx/sites-available/picycle

# Create link in sites-enabled
$SUDO ln -s /etc/nginx/sites-available/picycle /etc/nginx/sites-enabled

# Restart nginx
$SUDO service nginx restart

### Setup Supervisor to Start Apps on Boot / Restart on Failures
clear
echo "*************************************************************************"
echo "**                                                                     **"
echo "**      Configuring Supervisord...                                     **"
echo "**                                                                     **"
echo "*************************************************************************"

# Copy configuration files (control.conf, webapp.conf) to supervisor config directory
cd /usr/local/bin/picycle/auto-install/supervisor
# Add the current username to the configuration files 
echo "user=" $USER | tee -a control.conf > /dev/null
echo "user=" $USER | tee -a webapp.conf > /dev/null

$SUDO cp *.conf /etc/supervisor/conf.d/

SVISOR=$(whiptail --title "Would you like to enable the supervisor WebUI?" --radiolist "This allows you to check the status of the supervised processes via a web browser, and also allows those processes to be restarted directly from this interface. (Recommended)" 20 78 2 "ENABLE_SVISOR" "Enable the WebUI" ON "DISABLE_SVISOR" "Disable the WebUI" OFF 3>&1 1>&2 2>&3)

if [[ $SVISOR = "ENABLE_SVISOR" ]];then
   echo " " | sudo tee -a /etc/supervisor/supervisord.conf > /dev/null
   echo "[inet_http_server]" | sudo tee -a /etc/supervisor/supervisord.conf > /dev/null
   echo "port = 9001" | sudo tee -a /etc/supervisor/supervisord.conf > /dev/null
   USERNAME=$(whiptail --inputbox "Choose a username [default: user]" 8 78 user --title "Choose Username" 3>&1 1>&2 2>&3)
   echo "username = " $USERNAME | sudo tee -a /etc/supervisor/supervisord.conf > /dev/null
   PASSWORD=$(whiptail --passwordbox "Enter your password" 8 78 --title "Choose Password" 3>&1 1>&2 2>&3)
   echo "password = " $PASSWORD | sudo tee -a /etc/supervisor/supervisord.conf > /dev/null
   whiptail --msgbox --backtitle "Supervisor WebUI Setup" --title "Setup Completed" "You now should be able to access the Supervisor WebUI at http://your.ip.address.here:9001 with the username and password you have chosen." ${r} ${c}
else
   echo "No WebUI Setup."
fi

# If supervisor isn't already running, startup Supervisor
$SUDO service supervisor start

# Rebooting
whiptail --msgbox --backtitle "Install Complete / Reboot Required" --title "Installation Completed - Rebooting" "Congratulations, the installation is complete.  At this time, we will perform a reboot and your application should be ready.  On first boot, the wizard will guide you through the remaining setup steps.  You should be able to access your application by opening a browser on your PC or other device and using the IP address (or http://[hostname].local) for this device.  Enjoy!" ${r} ${c}
clear
$SUDO reboot
