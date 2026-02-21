#!/usr/bin/env bash
# ============================================================
# Clab AI Orchestrator - Ubuntu 24.04 Setup Script
# ============================================================
# Usage: sudo bash setup/install.sh
# ============================================================
set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

info()  { echo -e "${GREEN}[INFO]${NC} $*"; }
warn()  { echo -e "${YELLOW}[WARN]${NC} $*"; }
error() { echo -e "${RED}[ERROR]${NC} $*" >&2; }

# ---- Check root ----
if [[ $EUID -ne 0 ]]; then
    error "This script must be run as root (sudo)"
    exit 1
fi

# ---- Check Ubuntu 24.04 ----
if ! grep -q "24.04" /etc/os-release 2>/dev/null; then
    warn "This script is tested on Ubuntu 24.04. Your OS may differ."
fi

# ============================================================
# 1. Docker
# ============================================================
info "=== Step 1: Installing Docker ==="
if command -v docker &>/dev/null; then
    info "Docker is already installed: $(docker --version)"
else
    apt-get update
    apt-get install -y ca-certificates curl gnupg
    install -m 0755 -d /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    chmod a+r /etc/apt/keyrings/docker.gpg
    echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
      https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
      tee /etc/apt/sources.list.d/docker.list > /dev/null
    apt-get update
    apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
    info "Docker installed successfully."
fi

# Add current user to docker group
SUDO_USER_NAME="${SUDO_USER:-$USER}"
if ! groups "$SUDO_USER_NAME" | grep -q docker; then
    usermod -aG docker "$SUDO_USER_NAME"
    info "Added $SUDO_USER_NAME to docker group (re-login required for effect)."
fi

# ============================================================
# 2. Containerlab
# ============================================================
info "=== Step 2: Installing Containerlab ==="
if command -v clab &>/dev/null; then
    info "Containerlab is already installed: $(clab version | head -1)"
else
    bash -c "$(curl -sL https://get.containerlab.dev)"
    info "Containerlab installed successfully."
fi

# ============================================================
# 3. FRR Container Image
# ============================================================
FRR_IMAGE="${FRR_IMAGE:-quay.io/frrouting/frr:10.3.1}"
info "=== Step 3: Pulling FRR image ($FRR_IMAGE) ==="
docker pull "$FRR_IMAGE"
info "FRR image pulled successfully."

# ============================================================
# 4. vrnetlab (for vJunos-router)
# ============================================================
VRNETLAB_DIR="/opt/vrnetlab"
info "=== Step 4: Setting up vrnetlab for vJunos-router ==="
apt-get install -y make git qemu-system-x86

if [[ -d "$VRNETLAB_DIR" ]]; then
    info "vrnetlab directory already exists at $VRNETLAB_DIR"
    cd "$VRNETLAB_DIR" && git pull
else
    git clone https://github.com/hellt/vrnetlab.git "$VRNETLAB_DIR"
fi

# Check for vJunos image in images/ directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
IMAGES_DIR="${SCRIPT_DIR}/images"
VJUNOS_QCOW=$(find "$IMAGES_DIR" -name "vJunos-router-*.qcow2" 2>/dev/null | head -1)

if [[ -n "$VJUNOS_QCOW" ]]; then
    info "Found vJunos image: $VJUNOS_QCOW"
    cp "$VJUNOS_QCOW" "$VRNETLAB_DIR/vjunos-router/"
    cd "$VRNETLAB_DIR/vjunos-router"
    make
    info "vJunos-router Docker image built successfully."
else
    warn "No vJunos-router QCOW2 image found in $IMAGES_DIR"
    warn "Please download vJunos-router-*.qcow2 from Juniper and place it in $IMAGES_DIR"
    warn "Then re-run this script or manually build:"
    warn "  cp <image>.qcow2 $VRNETLAB_DIR/vjunos-router/"
    warn "  cd $VRNETLAB_DIR/vjunos-router && make"
fi

# ============================================================
# 5. Python environment
# ============================================================
info "=== Step 5: Setting up Python environment ==="
apt-get install -y python3 python3-pip python3-venv

info ""
info "============================================"
info "  Setup complete!"
info "============================================"
info ""
info "Next steps:"
info "  1. Log out and back in (for docker group)"
info "  2. Place vJunos QCOW2 in images/ if not done"
info "  3. Deploy lab: sudo clab deploy -t labs/basic-bgp/topology.clab.yml"
info ""
