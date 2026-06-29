#!/bin/bash
# install_service.sh
# Installs tank.py as a systemd service that starts automatically on boot.
#
# Run this once from the folder where tank.py lives:
#   chmod +x install_service.sh
#   sudo ./install_service.sh

set -e  # stop immediately if any command fails

# ---------------------------------------------------------------------------
# CONFIG -- adjust these if your setup is different
# ---------------------------------------------------------------------------
SCRIPT_NAME="tank.py"
SERVICE_NAME="tank"
INSTALL_DIR="/home/pi/tank"
RUN_AS_USER="pi"
# ---------------------------------------------------------------------------

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SERVICE_FILE="${SERVICE_NAME}.service"

echo "=== Tank service installer ==="

# 1. Check we're running as root (needed to write to /etc/systemd/system)
if [ "$EUID" -ne 0 ]; then
    echo "ERROR: Please run this script with sudo:"
    echo "  sudo ./install_service.sh"
    exit 1
fi

# 2. Check python3 is installed, install it if not
if command -v python3 &>/dev/null; then
    echo "Python3 found: $(python3 --version)"
else
    echo "Python3 not found, installing..."
    apt-get update -qq
    apt-get install -y python3 python3-pip
    echo "Python3 installed: $(python3 --version)"
fi

# 3. Check the user exists, create it if not
if id "$RUN_AS_USER" &>/dev/null; then
    echo "User '$RUN_AS_USER' already exists, skipping creation."
else
    echo "User '$RUN_AS_USER' not found, creating..."
    useradd \
        --create-home \
        --shell /bin/bash \
        --groups gpio,input \
        "$RUN_AS_USER"
    echo "User '$RUN_AS_USER' created."
    echo "NOTE: no password has been set for this user."
    echo "      If you need to log in as '$RUN_AS_USER', run: sudo passwd $RUN_AS_USER"
fi

# 4. Install Python dependencies
echo "Installing Python dependencies ..."
pip3 install -r "$SCRIPT_DIR/requirements.txt" --break-system-packages
echo "Dependencies installed."

# 5. Create install directory if it doesn't exist
if [ ! -d "$INSTALL_DIR" ]; then
    echo "Creating $INSTALL_DIR ..."
    mkdir -p "$INSTALL_DIR"
    chown "$RUN_AS_USER":"$RUN_AS_USER" "$INSTALL_DIR"
fi

# 6. Copy tank.py to the install directory (skip if already there)
if [ "$SCRIPT_DIR/$SCRIPT_NAME" != "$INSTALL_DIR/$SCRIPT_NAME" ]; then
    echo "Copying $SCRIPT_NAME to $INSTALL_DIR ..."
    cp "$SCRIPT_DIR/$SCRIPT_NAME" "$INSTALL_DIR/$SCRIPT_NAME"
    chown "$RUN_AS_USER":"$RUN_AS_USER" "$INSTALL_DIR/$SCRIPT_NAME"
fi
chmod +x "$INSTALL_DIR/$SCRIPT_NAME"

# 7. Copy the service file to systemd
echo "Installing $SERVICE_FILE ..."
cp "$SCRIPT_DIR/$SERVICE_FILE" "/etc/systemd/system/$SERVICE_FILE"
chmod 644 "/etc/systemd/system/$SERVICE_FILE"

# 8. Reload systemd so it picks up the new file
echo "Reloading systemd daemon ..."
systemctl daemon-reload

# 9. Enable the service (makes it start on boot)
echo "Enabling $SERVICE_NAME service ..."
systemctl enable "$SERVICE_NAME"

# 10. Start it right now too
echo "Starting $SERVICE_NAME service ..."
systemctl start "$SERVICE_NAME"

# 11. Show status
echo ""
echo "=== Done! Current service status ==="
systemctl status "$SERVICE_NAME" --no-pager

echo ""
echo "Useful commands:"
echo "  sudo systemctl status $SERVICE_NAME     # check if it's running"
echo "  sudo systemctl stop $SERVICE_NAME       # stop it"
echo "  sudo systemctl start $SERVICE_NAME      # start it"
echo "  sudo systemctl restart $SERVICE_NAME    # restart it"
echo "  sudo journalctl -u $SERVICE_NAME -f     # watch live logs"
echo "  sudo systemctl disable $SERVICE_NAME    # stop it from running at boot"
