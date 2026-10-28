#!/bin/bash
# Construit l'ISO KAVRION OS (amd64). À lancer en ROOT sur Debian 12/13 ou Ubuntu 22.04+ (ou dans un conteneur debian:trixie --privileged).
# Usage : sudo scripts/build.sh [--install-deps]
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
VERSION="$(cat "$ROOT/VERSION")"
[ "$(id -u)" -eq 0 ] || { echo "Ce script doit être lancé en root (sudo)."; exit 1; }
[ "$(uname -m)" = "x86_64" ] || { echo "Construction amd64 : machine x86_64 requise."; exit 1; }
ARG="${1:-}"; "$ROOT/scripts/check-deps.sh" "${ARG/--install-deps/--install}"

WORK="$ROOT/build"; DIST="$ROOT/dist"; LOG="$DIST/build-$(date +%Y%m%d-%H%M%S).log"
mkdir -p "$DIST"; rm -rf "$WORK"; mkdir -p "$WORK"
cp -a "$ROOT/config" "$WORK/config"
python3 "$ROOT/scripts/gen-branding.py" "$WORK/config/includes.chroot/usr/share/kavrion/branding" >/dev/null
cd "$WORK"
{
  echo "== KAVRION OS $VERSION - construction $(date -u +%FT%TZ) =="
  # live-build attend le dossier auto/ à la racine du répertoire de travail
  mkdir -p auto && cp config/auto/* auto/
  lb config
  lb build
} 2>&1 | tee "$LOG"
[ "${PIPESTATUS[0]}" -eq 0 ] || { echo "ÉCHEC de la construction, voir $LOG"; exit 1; }

ISO="$(ls -1 "$WORK"/*.iso 2>/dev/null | head -n1 || true)"
[ -n "$ISO" ] && [ -s "$ISO" ] || { echo "ISO introuvable après construction, voir $LOG"; exit 1; }
OUT="$DIST/kavrion-os-$VERSION-amd64.iso"
mv "$ISO" "$OUT"
( cd "$DIST" && sha256sum "$(basename "$OUT")" > "$(basename "$OUT").sha256" )
cat > "$DIST/BUILD-INFO.txt" <<INFO
KAVRION OS $VERSION
Architecture : amd64 (PC x86-64, UEFI + BIOS via ISO hybride)
Base : Debian 13 "trixie"
Construit le : $(date -u +%FT%TZ)
SHA-256 : $(cut -d' ' -f1 "$OUT.sha256")
Journal : $(basename "$LOG")
INFO
echo "ISO : $OUT"; cat "$OUT.sha256"
echo "Étape suivante : sudo scripts/verify-iso.sh $OUT"
