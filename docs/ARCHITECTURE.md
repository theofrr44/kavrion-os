# Architecture et décisions

## Choix techniques
- **Base Debian 13 « trixie »** (stable au moment de la rédaction) construite avec **live-build** : outil officiel Debian, reproductible, ISO hybride BIOS + UEFI.
- **XFCE** + **LightDM** : faible empreinte mémoire, thème **Arc-Dark** + icônes **Papirus-Dark**, compositing désactivé par défaut (mode léger actif ; réactivable dans Paramètres).
- **Calamares** : installateur graphique éprouvé (partitionnement ciblé sur le disque choisi, confirmation avant écriture, UEFI/EFI, utilisateur créé par la personne). Retenu plutôt que debian-installer pour l'expérience graphique et le branding.
- **zram** (zstd, 50 % de la RAM) au lieu d'un swap disque : adapté à 4 Go.
- **Outils KAVRION** en Python + GTK3 (pas de dépendance lourde) : métriques lues dans `/proc` et `/sys`, jamais simulées ; valeur absente = « n/d ».
- Pas de noyau original : noyau Debian `linux-image-amd64`.
- Non inclus volontairement : Plymouth, thème GRUB/syslinux personnalisé, signature Secure Boot (à ajouter dans une version ultérieure).

## Indépendance du système installé
`unpackfs` copie le squashfs ; `shellprocess_cleanup` retire l'autologin Live, `/etc/live`, le lanceur d'installation ; `removeuser` supprime le compte Live ; `packages` retire live-boot, live-config et Calamares ; `bootloader` installe GRUB (EFI + entrée de repli) sur le disque choisi ; `initramfs` régénère l'initramfs.

## Sécurité
Aucun mot de passe/clé dans l'image (contrôlé par `verify-iso.sh` et `tests/check_repo.sh`) ; aucun serveur SSH ; `doAutologin: false` ; mots de passe faibles refusés ; mises à jour de sécurité automatiques. La session **Live** utilise le compte `user` (créé par live-config, connexion automatique, sudo sans mot de passe) : c'est propre au Live et supprimé à l'installation.

## Double écran
`kavrion-displays` (xrandr) applique le profil (`~/.config/kavrion/display.json`). `kavrion-dashboard` s'ouvre en plein écran sur le moniteur **non principal** et se ferme sans erreur s'il n'y en a qu'un.

## Version ARM64 (future, non incluse)
Ne pas réutiliser l'ISO x86-64. Prévoir un dépôt/cible séparé : image disque (pas d'ISO) pour Raspberry Pi 4 construite avec `debos`/`pi-gen` ou l'image Debian `raspi`, noyau `linux-image-arm64` + firmware Raspberry Pi, `config/` partagé pour le bureau et les outils KAVRION (Python pur, portable). Déclarer la compatibilité seulement après test sur le matériel réel.

## Licences
Scripts du projet : MIT. Composants Debian : licences d'origine. Ressources graphiques : originales (logo généré par `scripts/gen-branding.py`, fond SVG).
