# Guide utilisateur — installer KAVRION OS depuis Windows

> ⚠️ **Deux effacements possibles.** (1) La préparation de la clé USB **efface tout** son contenu. (2) L'installation **peut effacer tout le disque** que vous sélectionnez, Windows compris. Sauvegardez vos fichiers importants avant de commencer et vérifiez deux fois le disque choisi.
>
> Cette version (0.1.0) n'a pas encore été testée sur un vrai PC. Essayez d'abord dans une machine virtuelle ou sur un ordinateur dont vous pouvez perdre le contenu.

## A. Où récupérer les fichiers
Après la construction (voir `GUIDE-CONSTRUCTION.md`), vous obtenez : `kavrion-os-0.1.0-amd64.iso`, `kavrion-os-0.1.0-amd64.iso.sha256` et `BUILD-INFO.txt`.

## B. Vérifier l'intégrité
PowerShell : `Get-FileHash .\kavrion-os-0.1.0-amd64.iso -Algorithm SHA256`. Le résultat doit être identique au contenu du fichier `.sha256`. Sinon, retéléchargez l'ISO.

## C. Télécharger Rufus
Uniquement depuis le site officiel : **https://rufus.ie/** (version « portable » possible, sans installation).

## D. Créer la clé USB
1. Branchez une clé USB de 8 Go ou plus **dont le contenu peut être effacé**.
2. Lancez Rufus. Dans **Périphérique**, vérifiez que c'est bien votre clé (taille et nom).
3. Cliquez **SÉLECTION** et choisissez `kavrion-os-0.1.0-amd64.iso`.
4. **Schéma de partition** : *GPT* pour un PC récent en UEFI ; *MBR* pour un très ancien PC en BIOS. Rufus propose normalement la bonne valeur ; en cas de doute, gardez-la.
5. Cliquez **DÉMARRER**. Rufus détecte une image « ISOHybrid » et demande un mode d'écriture : choisissez **Écriture en mode Image DD** (le plus fidèle pour ce type d'image). Si la clé ne démarre pas ensuite, refaites-la en **mode Image ISO**.
6. Acceptez l'avertissement d'effacement, attendez la fin (« PRÊT »), puis fermez Rufus.

*Ces réglages Rufus sont ceux habituellement recommandés pour une ISO hybride Debian ; l'écran de Rufus peut différer selon sa version — suivez ses indications si elles diffèrent, et notez que ces réglages n'ont pas pu être vérifiés sur l'ISO finale.*

## E. Démarrer sur la clé
1. Laissez la clé branchée et redémarrez le PC.
2. Appuyez immédiatement et plusieurs fois sur la touche du menu de démarrage (souvent **F12**, **F10**, **F9**, **Échap** ou **F8**, selon la marque).
3. Choisissez la clé USB (une entrée « UEFI : … » de préférence).
4. Si le PC refuse de démarrer la clé : entrez dans le BIOS/UEFI et **désactivez Secure Boot** (cette version n'est pas signée pour Secure Boot). Sous Windows, si le PC démarre toujours Windows : désactivez le « démarrage rapide » (Options d'alimentation) et réessayez.

## F. Tester le mode Live
Le bureau KAVRION s'ouvre sans rien installer (session « user », sans mot de passe, valable uniquement pendant le test). Vous pouvez essayer le menu, le **KAVRION Moniteur**, les **Paramètres** et le réseau. Rien n'est écrit sur le disque tant que vous n'installez pas.

## G. Lancer l'installation
1. Double-cliquez sur **Installer KAVRION OS** (bureau).
2. Choisissez la langue, le clavier, le fuseau horaire.
3. **Disque** : sélectionnez avec attention votre disque interne. « Effacer le disque » **détruit toutes les données de ce disque**. Calamares affiche un récapitulatif et demande une confirmation avant d'écrire. Les autres disques ne sont pas touchés.
4. Créez votre compte et **votre propre mot de passe** (8 caractères minimum). Aucun mot de passe n'est fourni avec le système.
5. Vérifiez le résumé, cliquez **Installer**, attendez la fin.

## H. Terminer
Cochez « Redémarrer maintenant », puis **retirez la clé USB** quand l'écran s'éteint. L'ordinateur démarre sur KAVRION OS depuis le disque interne et affiche l'écran de connexion. Si Windows ou la clé repart : choisissez le disque KAVRION dans le menu de démarrage (touche de l'étape E) ou placez-le en premier dans l'ordre de démarrage du BIOS/UEFI.

## I. Si le démarrage ne fonctionne pas
Voir `GUIDE-DEPANNAGE.md` (réparation de GRUB depuis la clé Live).

## J. Mettre à jour et sauvegarder
- **Mises à jour** : les correctifs de sécurité s'installent automatiquement (connexion Internet requise). Pour tout mettre à jour : Terminal → `sudo apt update && sudo apt full-upgrade`, ou le gestionnaire **Synaptic** (menu → Système).
- **Sauvegarde** : copiez votre dossier personnel vers un disque externe, par exemple `rsync -a --progress ~/ /media/$USER/MON_DISQUE/sauvegarde/` (remplacez `MON_DISQUE`).

## Deux écrans / télévisions
**KAVRION Paramètres → Écrans** : *Automatique* (2 écrans détectés = bureau sur le premier, **Tableau de bord** sur le second), *Simple écran*, ou *Double écran*. Si le second écran est débranché, la session démarre normalement et le tableau de bord ne s'ouvre pas. Mode léger : *Paramètres → Performances*.
