#!/bin/bash
# Vérifie (et avec --install, installe) les dépendances de construction. Debian/Ubuntu uniquement.
set -euo pipefail
PKGS=(live-build debootstrap xorriso squashfs-tools mtools dosfstools syslinux syslinux-common isolinux grub-efi-amd64-bin grub-pc-bin rsync zip python3)
missing=()
for p in "${PKGS[@]}"; do dpkg -s "$p" >/dev/null 2>&1 || missing+=("$p"); done
if [ ${#missing[@]} -eq 0 ]; then echo "[deps] OK"; exit 0; fi
echo "[deps] paquets manquants : ${missing[*]}"
if [ "${1:-}" = "--install" ]; then
  [ "$(id -u)" -eq 0 ] || { echo "[deps] --install demande root"; exit 1; }
  apt-get update && apt-get install -y --no-install-recommends "${missing[@]}"
else
  echo "[deps] relancez avec --install (root) ou : apt install ${missing[*]}"; exit 1
fi
