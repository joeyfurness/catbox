#!/usr/bin/env bash
# deploy.sh — Deploy Schrödinger's Catbox to the Raspberry Pi
#
# Target: schrodinger@catbox.local
# Requires SSH key access to the Pi.
#
# Usage:
#   ./deploy.sh [--port PORT] [--half-life SECONDS]

set -euo pipefail

TARGET="schrodinger@catbox.local"
REMOTE_DIR="~/catbox"
SERVICE_NAME="cat"
SERVICE_FILE="systemd/cat.service"
REMOTE_SERVICE_PATH="/etc/systemd/system/${SERVICE_NAME}.service"

echo "==> Deploying Schrödinger's Catbox to ${TARGET}"

# 1. Copy src/ to the Pi
echo "==> Copying src/ to ${TARGET}:${REMOTE_DIR}/"
scp -r src/ "${TARGET}:${REMOTE_DIR}/"

# 2. Copy the systemd unit file to the Pi (needs sudo on the Pi)
echo "==> Installing systemd unit file at ${REMOTE_SERVICE_PATH}"
scp "${SERVICE_FILE}" "${TARGET}:/tmp/${SERVICE_NAME}.service"
ssh "${TARGET}" "sudo mv /tmp/${SERVICE_NAME}.service ${REMOTE_SERVICE_PATH} && sudo chown root:root ${REMOTE_SERVICE_PATH}"

# 3. Reload the systemd daemon so it picks up the new/updated unit
echo "==> Reloading systemd daemon"
ssh "${TARGET}" "sudo systemctl daemon-reload"

# 4. Enable the service so it starts on boot
echo "==> Enabling ${SERVICE_NAME} service"
ssh "${TARGET}" "sudo systemctl enable ${SERVICE_NAME}"

# 5. Restart the service
echo "==> Restarting ${SERVICE_NAME} service"
ssh "${TARGET}" "sudo systemctl restart ${SERVICE_NAME}"

# 6. Show service status
echo ""
echo "==> Service status:"
ssh "${TARGET}" "systemctl status ${SERVICE_NAME} --no-pager"
