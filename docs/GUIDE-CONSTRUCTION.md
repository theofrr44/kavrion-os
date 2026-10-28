# Construire l'ISO KAVRION OS

La construction exige **Linux** (Debian 12/13 ou Ubuntu 22.04+), les droits root et ~15 Go libres. Elle ne fonctionne pas correctement sous Windows seul.

## Option A — Gratuite, sans Linux : GitHub Actions
1. Créez un compte sur https://github.com et un dépôt **privé** vide (ex. `kavrion-os`).
2. Envoyez-y le contenu du dossier `kavrion-os` (bouton *Add file → Upload files*, en incluant le dossier caché `.github`). Si l'interface refuse un dossier caché, utilisez *Add file → Create new file*, nommez-le `.github/workflows/build-iso.yml` et collez le contenu du fichier.
3. Onglet **Actions** → « Construire l'ISO KAVRION OS » → **Run workflow**.
4. Attendez (30 à 60 min environ). En cas d'échec, ouvrez le journal : il indique la ligne en cause (voir « Si la construction échoue »).
5. En bas de l'exécution réussie, téléchargez l'artefact **kavrion-os-iso** (un ZIP contenant l'ISO, le `.sha256`, `BUILD-INFO.txt` et le journal).

## Option B — Machine Linux ou machine virtuelle Debian
```bash
sudo apt install git make python3
cd kavrion-os
sudo scripts/build.sh --install-deps
scripts/verify-iso.sh dist/kavrion-os-0.1.0-amd64.iso
```
Résultat dans `dist/` : l'ISO, `*.iso.sha256`, `BUILD-INFO.txt`, journal `build-*.log`. Le script s'arrête à la première erreur importante.

## Vérifier la somme SHA-256 (Windows)
PowerShell, dans le dossier de l'ISO :
```powershell
Get-FileHash .\kavrion-os-0.1.0-amd64.iso -Algorithm SHA256
```
Comparez avec le contenu du fichier `.sha256`.

## Si la construction échoue
Cette configuration n'a **jamais été exécutée** : une option `lb config` ou un nom de paquet peut devoir être ajusté à la version exacte de Debian. Cherchez dans le journal `E:` ou `Unable to locate package`, corrigez `config/package-lists/kavrion.list.chroot` ou `config/auto/config`, puis relancez.

## Tester avant de graver
`scripts/test-vm.sh smoke|live|install|disk <iso>` (QEMU + OVMF). Voir `docs/TESTS.md`.
