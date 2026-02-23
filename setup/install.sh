#!/usr/bin/env bash
# ============================================================
# Clab AI Orchestrator - Setup Script for Ubuntu 24.04
# ============================================================
# Usage:
#   sudo bash setup/install.sh          # Full setup
#   sudo bash setup/install.sh --skip-vrnetlab  # Skip vJunos build
# ============================================================
set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

info()  { echo -e "${GREEN}[✓]${NC} $*"; }
warn()  { echo -e "${YELLOW}[!]${NC} $*"; }
error() { echo -e "${RED}[✗]${NC} $*" >&2; }
step()  { echo -e "\n${BLUE}━━━ $* ━━━${NC}"; }

SKIP_VRNETLAB=false
for arg in "$@"; do
    case "$arg" in
        --skip-vrnetlab) SKIP_VRNETLAB=true ;;
    esac
done

# ---- Resolve project root ----
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# ---- Check root ----
if [[ $EUID -ne 0 ]]; then
    error "This script must be run with sudo"
    echo "  sudo bash $0"
    exit 1
fi

# ---- Check OS ----
if ! grep -q "24.04" /etc/os-release 2>/dev/null; then
    warn "This script is designed for Ubuntu 24.04. Your OS may differ."
fi

SUDO_USER_NAME="${SUDO_USER:-$USER}"

echo ""
echo "╔══════════════════════════════════════════════════╗"
echo "║   Clab AI Orchestrator - Environment Setup      ║"
echo "╠══════════════════════════════════════════════════╣"
echo "║  Target: Ubuntu 24.04                           ║"
echo "║  User:   $SUDO_USER_NAME"
echo "║  Root:   $PROJECT_ROOT"
echo "╚══════════════════════════════════════════════════╝"
echo ""

# ============================================================
# 1. Docker
# ============================================================
step "Step 1/5: Docker"

if command -v docker &>/dev/null; then
    info "Docker already installed: $(docker --version)"
else
    info "Installing Docker..."
    apt-get update -qq
    apt-get install -y -qq docker.io docker-compose-v2 > /dev/null
    systemctl enable --now docker
    info "Docker installed: $(docker --version)"
fi

# Ensure user is in docker group
if ! groups "$SUDO_USER_NAME" 2>/dev/null | grep -q docker; then
    usermod -aG docker "$SUDO_USER_NAME"
    info "Added $SUDO_USER_NAME to docker group (re-login required)"
else
    info "User $SUDO_USER_NAME is already in docker group"
fi

# ============================================================
# 2. Containerlab
# ============================================================
step "Step 2/5: Containerlab"

if command -v clab &>/dev/null; then
    CLAB_VER=$(clab version 2>/dev/null | grep -oP 'version:\s*\K\S+' || echo "unknown")
    info "Containerlab already installed: $CLAB_VER"
else
    info "Installing containerlab..."
    bash -c "$(curl -sL https://get.containerlab.dev)" > /dev/null 2>&1
    info "Containerlab installed: $(clab version 2>/dev/null | grep -oP 'version:\s*\K\S+' || echo 'done')"
fi

# ============================================================
# 3. FRR Image
# ============================================================
step "Step 3/5: FRR Container Image"

FRR_IMAGE="${FRR_IMAGE:-quay.io/frrouting/frr:10.3.1}"

if docker image inspect "$FRR_IMAGE" &>/dev/null; then
    info "FRR image already exists: $FRR_IMAGE"
else
    info "Pulling $FRR_IMAGE ..."
    docker pull "$FRR_IMAGE"
    info "FRR image pulled"
fi

# ============================================================
# 4. vrnetlab (vJunos-router)
# ============================================================
step "Step 4/5: vrnetlab / vJunos-router"

VRNETLAB_DIR="/opt/vrnetlab"

if [[ "$SKIP_VRNETLAB" == "true" ]]; then
    warn "Skipping vrnetlab (--skip-vrnetlab flag)"
else
    # Install build dependencies
    apt-get install -y -qq make git qemu-system-x86 > /dev/null 2>&1
    info "Build dependencies installed"

    # Clone or update vrnetlab
    if [[ -d "$VRNETLAB_DIR/.git" ]]; then
        info "vrnetlab already cloned at $VRNETLAB_DIR"
        cd "$VRNETLAB_DIR" && git pull --quiet
    else
        info "Cloning vrnetlab..."
        git clone --quiet https://github.com/hellt/vrnetlab.git "$VRNETLAB_DIR"
    fi
    info "vrnetlab ready at $VRNETLAB_DIR"

    # vrnetlab path: juniper/vjunosrouter (no hyphens)
    VJUNOS_BUILD_DIR="$VRNETLAB_DIR/juniper/vjunosrouter"

    # Look for vJunos QCOW2
    IMAGES_DIR="${PROJECT_ROOT}/images"
    VJUNOS_QCOW=$(find "$IMAGES_DIR" -name "vJunos-router-*.qcow2" 2>/dev/null | head -1)

    if docker images --format '{{.Repository}}' | grep -q "vrnetlab/juniper_vjunos-router"; then
        info "vJunos Docker image already exists"
    elif [[ -n "$VJUNOS_QCOW" ]]; then
        info "Found QCOW2: $(basename "$VJUNOS_QCOW")"
        info "Building Docker image (this takes 5-10 minutes)..."
        cp "$VJUNOS_QCOW" "$VJUNOS_BUILD_DIR/"
        cd "$VJUNOS_BUILD_DIR"
        make 2>&1 | tail -10
        info "vJunos Docker image built successfully"
    else
        warn "No vJunos-router QCOW2 found in $IMAGES_DIR"
        warn "Download from https://support.juniper.net/ and place in:"
        warn "  $IMAGES_DIR/vJunos-router-<version>.qcow2"
        warn "Then re-run this script."
    fi
fi

# ============================================================
# 5. uv & mcp-bridge
# ============================================================
step "Step 5/5: uv & mcp-bridge"

if command -v uv &>/dev/null; then
    info "uv already installed: $(uv --version)"
else
    info "Installing uv via curl..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    # Ensure uv is in the path for the rest of the script if installing as root
    export PATH="$HOME/.local/bin:$PATH"
    info "uv installed"
fi

MCP_DIR="${PROJECT_ROOT}/mcp-bridge"

info "Setting up mcp-bridge with uv..."
sudo -i -u "$SUDO_USER_NAME" bash -c "cd \"$MCP_DIR\" && uv venv && uv pip install --quiet -e \".[dev]\""
info "mcp-bridge installed via uv"

# ============================================================
# Summary
# ============================================================
echo ""
echo "╔══════════════════════════════════════════════════╗"
echo "║   ✅ Setup Complete!                            ║"
echo "╠══════════════════════════════════════════════════╣"
echo "║                                                 ║"
echo "║  Docker:       $(docker --version | grep -oP 'Docker version \K[^,]+')"
echo "║  Containerlab: $(clab version 2>/dev/null | grep -oP 'version:\s*\K\S+' || echo 'installed')"
echo "║  FRR:          $FRR_IMAGE"
echo "║  Python:       uv managed"
echo "║  mcp-bridge:   $MCP_DIR/.venv"

if docker images --format '{{.Repository}}' | grep -q "vrnetlab/juniper_vjunos-router"; then
    echo "║  vJunos:       ✅ Docker image ready"
else
    echo "║  vJunos:       ⚠️  QCOW2 image needed"
fi

echo "║                                                 ║"
echo "╠══════════════════════════════════════════════════╣"
echo "║  Next steps:                                    ║"
echo "║  1. Log out & back in (docker group)            ║"
echo "║  2. sudo clab deploy -t \\                      ║"
echo "║       labs/basic-bgp/topology.clab.yml          ║"
echo "╚══════════════════════════════════════════════════╝"
echo ""
