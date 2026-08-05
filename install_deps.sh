#!/usr/bin/env bash
set -euo pipefail

# install_deps.sh - Multi-distro installer for CityLab Phase1 PoC
# Supports: Nobara/Fedora, Ubuntu/Debian, Arch/Manjaro (partial AUR helper)
# Runs package manager operations and installs system-wide Python packages so
# Mininet processes (run under sudo) can import required modules.

if [[ -f /etc/os-release ]]; then
  . /etc/os-release
  id=${ID,,}
else
  echo "Cannot detect distro (no /etc/os-release). Install mininet and openvswitch manually." >&2
  exit 1
fi

echo "Detected distro: $NAME (ID=$id)"

install_pip_pkgs() {
  echo "[+] Installing Python packages system-wide (pymodbus, python-dotenv, scapy, helics)"
  python3 -m pip install --upgrade pip || true
  python3 -m pip install pymodbus==3.6.4 python-dotenv==1.1.0 scapy==2.6.1 helics==3.4.0 || true
}

if [[ $id =~ (fedora|nobara|rhel) ]]; then
  echo "[+] Using dnf for Fedora/Nobara/RHEL"
  dnf install -y epel-release || true
  dnf install -y git python3-pip openvswitch mininet || {
    echo "dnf install failed; attempting Mininet install from source"
    git clone https://github.com/mininet/mininet.git /tmp/mininet
    /tmp/mininet/util/install.sh -a
  }
  systemctl enable --now openvswitch || true
  install_pip_pkgs
  echo "[+] Done. Verify with: sudo ovs-vsctl show"

elif [[ $id =~ (ubuntu|debian|linuxmint) ]]; then
  echo "[+] Using apt for Debian/Ubuntu/Mint"
  apt update
  apt install -y git python3-pip mininet openvswitch-switch || {
    echo "apt install failed for mininet/openvswitch; please install manually" >&2
  }
  systemctl enable --now openvswitch || true
  install_pip_pkgs
  echo "[+] Done. Verify with: sudo ovs-vsctl show"

elif [[ $id =~ (arch|manjaro) ]]; then
  echo "[+] Using pacman for Arch/Manjaro"
  pacman -Syu --needed --noconfirm base-devel git python-pip openvswitch || true
  # Try to install mininet via AUR helper if present
  if command -v yay >/dev/null 2>&1; then
    yay -S --noconfirm mininet || true
  elif command -v paru >/dev/null 2>&1; then
    paru -S --noconfirm mininet || true
  else
    echo "No AUR helper found. To install mininet run as your user:
  git clone https://github.com/mininet/mininet.git /tmp/mininet && /tmp/mininet/util/install.sh -a" >&2
  fi
  systemctl enable --now openvswitch || true
  install_pip_pkgs
  echo "[+] Done. Verify with: sudo ovs-vsctl show"

else
  echo "Unsupported distro: $id. Please install mininet and openvswitch manually." >&2
  exit 1
fi

cat <<'EOF'

Installation finished.
Next steps:
  1) Verify Open vSwitch: sudo ovs-vsctl show
  2) Run the topology tests: sudo python3 network/topology.py --test
  3) Start Mininet interactively: sudo python3 network/topology.py

If Python packages fail to be importable under sudo, run:
  sudo python3 -m pip install pymodbus==3.6.4 python-dotenv==1.1.0 scapy==2.6.1 helics==3.4.0
or use the script again as root.

EOF
