#!/bin/bash
# Tests en machine virtuelle QEMU (nécessite qemu-system-x86 et ovmf ; KVM recommandé).
#   test-vm.sh smoke   <iso>       démarre l'ISO en UEFI sans écran, capture une image, vérifie qu'elle n'est pas noire
#   test-vm.sh live    <iso>       démarre l'ISO avec fenêtre (UEFI)
#   test-vm.sh install <iso>       crée dist/test-disk.qcow2 (20 Go) et démarre l'ISO + ce disque : lancez l'installateur
#   test-vm.sh disk                démarre UNIQUEMENT le disque installé (sans ISO) : preuve de l'indépendance de la clé
#   Option BIOS=1 : démarrage BIOS (SeaBIOS) au lieu d'UEFI.  DUAL=1 : deux écrans virtuels.
set -euo pipefail
MODE="${1:?mode: smoke|live|install|disk}"; ISO="${2:-}"; D="$(cd "$(dirname "$0")/.." && pwd)/dist"; mkdir -p "$D"
DISK="$D/test-disk.qcow2"
CODE=/usr/share/OVMF/OVMF_CODE_4M.fd; VARS_SRC=/usr/share/OVMF/OVMF_VARS_4M.fd; VARS="$D/test-vars.fd"
ARGS=(-m 4096 -smp 2 -device virtio-vga -device qemu-xhci -device usb-kbd -device usb-tablet -nic user,model=virtio-net-pci)
[ -w /dev/kvm ] && ARGS+=(-enable-kvm -cpu host) || echo "[avertissement] pas de KVM : ce sera lent"
if [ "${BIOS:-0}" != "1" ]; then
  [ -f "$CODE" ] || { echo "OVMF introuvable (apt install ovmf)"; exit 1; }
  [ -f "$VARS" ] || cp "$VARS_SRC" "$VARS"
  ARGS+=(-drive if=pflash,format=raw,readonly=on,file="$CODE" -drive if=pflash,format=raw,file="$VARS")
fi
[ "${DUAL:-0}" = "1" ] && ARGS+=(-device virtio-vga -display gtk)
case "$MODE" in
  smoke)
    [ -s "$ISO" ] || { echo "ISO requise"; exit 1; }
    SHOT="$D/smoke.ppm"; rm -f "$SHOT"
    ( sleep "${WAIT:-150}"; echo "screendump $SHOT"; sleep 2; echo quit ) | qemu-system-x86_64 "${ARGS[@]}" -cdrom "$ISO" -boot d -display none -monitor stdio >/dev/null
    python3 - "$SHOT" <<'PY'
import sys
d = open(sys.argv[1], "rb").read()
body = d[d.index(b"\n255\n") + 5:] if b"\n255\n" in d else d
distinct = len(set(body[i:i+3] for i in range(0, min(len(body), 3_000_000), 3)))
print("couleurs distinctes dans la capture :", distinct)
sys.exit(0 if distinct > 50 else 1)
PY
    echo "capture : $SHOT (à regarder pour confirmer que le bureau KAVRION est affiché)";;
  live)    qemu-system-x86_64 "${ARGS[@]}" -cdrom "$ISO" -boot d;;
  install) [ -f "$DISK" ] || qemu-img create -f qcow2 "$DISK" 20G
           qemu-system-x86_64 "${ARGS[@]}" -drive file="$DISK",if=virtio -cdrom "$ISO" -boot d;;
  disk)    qemu-system-x86_64 "${ARGS[@]}" -drive file="$DISK",if=virtio -boot c;;
  *) echo "mode inconnu"; exit 2;;
esac
