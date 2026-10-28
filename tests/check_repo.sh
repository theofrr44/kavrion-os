#!/bin/bash
# Contrôles statiques du dépôt (exécutables sans réseau ni root).
set -uo pipefail
cd "$(dirname "$0")/.."
fail=0; ok(){ echo "  [OK]    $1"; }; ko(){ echo "  [ÉCHEC] $1"; fail=1; }
for f in scripts/*.sh tests/*.sh config/auto/* config/hooks/live/*.chroot; do
  bash -n "$f" 2>/dev/null || sh -n "$f" 2>/dev/null && ok "syntaxe shell : $f" || ko "syntaxe shell : $f"
done
for f in $(find config scripts tests -name '*.py'); do python3 -m py_compile "$f" 2>/dev/null && ok "python : $f" || ko "python : $f"; done
find . -name __pycache__ -prune -exec rm -rf {} \; 2>/dev/null
python3 - <<'PY' && ok "XML/YAML bien formés" || ko "XML/YAML invalides"
import glob, sys, xml.etree.ElementTree as ET
for f in glob.glob("config/**/*.xml", recursive=True) + glob.glob("config/**/*.svg", recursive=True):
    ET.parse(f)
try:
    import yaml
    for f in glob.glob("config/includes.chroot/etc/calamares/**/*.conf", recursive=True) + ["config/includes.chroot/etc/calamares/branding/kavrion/branding.desc"]:
        yaml.safe_load(open(f))
except ImportError:
    print("(PyYAML absent : YAML non validé)")
PY
for f in config/package-lists/kavrion.list.chroot config/includes.chroot/etc/calamares/settings.conf config/includes.chroot/usr/share/kavrion/wallpapers/kavrion-default.svg config/includes.chroot/usr/local/bin/kavrion-monitor docs/GUIDE-UTILISATEUR.md; do
  [ -s "$f" ] && ok "présent : $f" || ko "manquant : $f"
done
grep -q '^calamares$' config/package-lists/kavrion.list.chroot && ok "Calamares dans la liste de paquets" || ko "Calamares absent"
# sécurité : aucun secret / mot de passe en dur
if grep -rEi '(password|passwd)\s*[:=]\s*["'"'"']?[A-Za-z0-9]{3,}|chpasswd|useradd .*-p ' config scripts --include='*' 2>/dev/null | grep -vE 'passwordRequirements|allowWeakPasswords|setRootPassword|doReusePassword|minLength'; then ko "mot de passe en dur détecté"; else ok "aucun mot de passe en dur"; fi
grep -rq 'openssh-server' config/package-lists && ko "openssh-server installé par défaut" || ok "pas de serveur SSH par défaut"
grep -q 'doAutologin: false' config/includes.chroot/etc/calamares/modules/users.conf && ok "pas de connexion automatique après installation" || ko "autologin non désactivé"
grep -q '50-kavrion-live.conf' config/includes.chroot/etc/calamares/modules/shellprocess_cleanup.conf && ok "autologin Live retiré à l'installation" || ko "nettoyage autologin absent"
[ $fail -eq 0 ] && echo "=> DÉPÔT COHÉRENT" || { echo "=> PROBLÈMES DÉTECTÉS"; exit 1; }
