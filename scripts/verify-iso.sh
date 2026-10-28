#!/bin/bash
# Vérifie l'ISO produite : somme SHA-256, structure hybride, noyau, bootloaders UEFI/BIOS, contenu du système.
# Usage : scripts/verify-iso.sh dist/kavrion-os-X-amd64.iso     (nécessite xorriso, squashfs-tools)
set -uo pipefail
ISO="${1:?usage: verify-iso.sh <fichier.iso>}"
fail=0; ok(){ echo "  [OK]    $1"; }; ko(){ echo "  [ÉCHEC] $1"; fail=1; }
[ -s "$ISO" ] && ok "fichier présent ($(du -h "$ISO" | cut -f1))" || { ko "ISO absente"; exit 1; }
if [ -f "$ISO.sha256" ]; then ( cd "$(dirname "$ISO")" && sha256sum -c "$(basename "$ISO").sha256" >/dev/null 2>&1 ) && ok "SHA-256 conforme" || ko "SHA-256 différent"; else ko "fichier .sha256 absent"; fi
[ "$(dd if="$ISO" bs=1 skip=510 count=2 2>/dev/null | od -An -tx1 | tr -d " \n")" = "55aa" ] && ok "secteur de démarrage hybride (clé USB / BIOS)" || ko "pas de MBR hybride"
LIST="$(xorriso -indev "$ISO" -find / -type f 2>/dev/null)"
has(){ echo "$LIST" | grep -qiE "$1"; }
has "/live/filesystem.squashfs" && ok "système compressé /live/filesystem.squashfs" || ko "squashfs absent"
has "/live/vmlinuz" && has "/live/initrd" && ok "noyau + initrd" || ko "noyau/initrd absents"
has "/EFI/(boot|BOOT)/boot(x64)?\.efi|efi\.img" && ok "démarrage UEFI" || ko "démarrage UEFI absent"
has "isolinux|syslinux" && ok "démarrage BIOS (isolinux)" || ko "démarrage BIOS absent"
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
xorriso -osirrox on -indev "$ISO" -extract /live/filesystem.squashfs "$TMP/fs.squashfs" >/dev/null 2>&1
if [ -s "$TMP/fs.squashfs" ]; then
  cat_(){ unsquashfs -cat "$TMP/fs.squashfs" "$1" 2>/dev/null; }
  cat_ etc/os-release | grep -q 'KAVRION OS' && ok "os-release = KAVRION OS" || ko "os-release incorrect"
  for f in usr/bin/calamares usr/lib/kavrion/kavrion_monitor.py usr/bin/lightdm usr/bin/startxfce4 etc/calamares/settings.conf; do
    unsquashfs -ll "$TMP/fs.squashfs" "$f" 2>/dev/null | grep -q "$(basename "$f")" && ok "présent : /$f" || ko "manquant : /$f"
  done
  # aucun mot de passe intégré : aucun hash réel dans /etc/shadow (champ 2 doit être ! * ou vide)
  if cat_ etc/shadow | awk -F: '$2 ~ /^\$/ {bad=1} END{exit bad?0:1}'; then ko "hash de mot de passe trouvé dans /etc/shadow"; else ok "aucun hash de mot de passe dans l'image"; fi
  unsquashfs -ll "$TMP/fs.squashfs" 2>/dev/null | grep -qE 'ssh/sshd_config|usr/sbin/sshd' && ko "serveur SSH présent" || ok "aucun serveur SSH"
else ko "extraction du squashfs impossible"; fi
[ $fail -eq 0 ] && echo "=> ISO VALIDE (contrôles statiques uniquement : testez aussi le démarrage, voir docs/TESTS.md)" || { echo "=> ISO NON CONFORME"; exit 1; }
