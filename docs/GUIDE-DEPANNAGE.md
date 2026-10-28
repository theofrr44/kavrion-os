# Dépannage

| Symptôme | Piste |
|---|---|
| La clé n'apparaît pas dans le menu de démarrage | Refaire la clé en mode Image ISO (au lieu de DD) ou l'inverse ; essayer un autre port USB (USB 2.0 de préférence) |
| « Secure Boot violation » / écran noir immédiat | Désactiver Secure Boot dans le BIOS/UEFI |
| Le PC démarre toujours Windows après l'installation | Choisir le disque KAVRION dans le menu de démarrage, ou le placer en premier dans le BIOS/UEFI |
| Écran noir après le logo | Au menu de démarrage de la clé, éditer la ligne de démarrage et ajouter `nomodeset` ; signaler le modèle de carte graphique |
| Wi-Fi absent | Brancher un câble Ethernet, puis `sudo apt update && sudo apt install firmware-<fabricant>` |
| Pas de second écran | `kavrion-displays status` dans un terminal ; essayer un autre câble/port ; choisir le profil dans Paramètres |

## Réparer le démarrage (GRUB) depuis la clé Live
Démarrez la clé Live, ouvrez un terminal, puis (remplacez `sdXN` par vos partitions ; `lsblk -f` les liste) :
```bash
sudo mount /dev/sdXN /mnt                 # partition racine de KAVRION (ext4)
sudo mount /dev/sdXM /mnt/boot/efi        # partition EFI (FAT32, ~512 Mo) — UEFI seulement
for d in dev dev/pts proc sys run; do sudo mount --bind /$d /mnt/$d; done
sudo chroot /mnt
grub-install --target=x86_64-efi --efi-directory=/boot/efi --bootloader-id=KAVRION --removable   # UEFI
# BIOS ancien :  grub-install /dev/sdX   (le disque, sans numéro)
update-grub
exit
```
Redémarrez sans la clé. Attention : n'indiquez que votre disque KAVRION.

## Journaux utiles
`journalctl -b -p err` (erreurs du dernier démarrage) ; journal de l'installateur : `~/.cache/calamares/session.log` (session Live).
