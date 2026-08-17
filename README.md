<p align="center">
  <img src="plugin.video.vstreamlists/icon-v2.png" width="140" alt="vStream Listes">
</p>

<h1 align="center">vStream Listes</h1>

<p align="center">
  Listes personnelles de films et séries pour Kodi, propulsées par TMDB et la source Pastebin de vStream.
</p>

<p align="center">
  <img alt="Version extension" src="https://img.shields.io/badge/vStream%20Listes-0.1.10-2ea3f2">
  <img alt="Version depot" src="https://img.shields.io/badge/Repository-1.0.3-2ea3f2">
  <img alt="Licence" src="https://img.shields.io/badge/licence-GPL--3.0-lightgrey">
</p>

---

## 🎬 C'est quoi ?

**vStream Listes** est une extension Kodi 100% indépendante qui te permet de
créer tes propres listes de films et séries (Favoris, À regarder, Marvel,
Films d'horreur...) directement depuis Kodi.

Elle **ne modifie jamais vStream** : elle s'appuie simplement dessus pour
retrouver et lire tes contenus via sa source Pastebin, pendant que **TMDB**
fournit les affiches, synopsis, notes et années. Pas de compte, pas de
Trakt, pas de données envoyées ailleurs : tout reste local, dans Kodi.

vStream lui-même est développé par l'équipe [Kodi-vStream](https://github.com/kodi-vstream/venom-xbmc-addons),
un immense merci à eux pour leur travail, sans lequel cette extension n'aurait
pas de raison d'exister.

## ✨ Fonctionnalités

- 📂 Créer, renommer, supprimer et réordonner autant de listes que tu veux
- 🎞️ Ajouter un film ou une série **directement depuis vStream**, via
  "Ajouter à mes listes" dans son menu contextuel
- 🔀 Déplacer ou copier un contenu d'une liste à une autre
- 🖼️ Affiches, synopsis, année, genres et note TMDB pour chaque titre
- ▶️ Un clic pour lancer la lecture via vStream / Pastebin
- 🔁 Mises à jour automatiques une fois le dépôt installé

## 📦 Installation

1. **Ajouter la source** : *Système → Gestionnaire de fichiers → Ajouter une
   source → Aucun* → saisir :
   ```
   https://PanameFR.github.io/vStream-Listes/
   ```
2. **Installer le dépôt** : *Extensions → Installer depuis un fichier zip* →
   sélectionner la source ajoutée → `repo/` → `repository.vstreamlists/` →
   le fichier `.zip`.
3. **Installer l'extension** : *Extensions → Installer depuis un dépôt →
   vStream Listes Repository → Extensions vidéo → vStream Listes →
   Installer*.

Les mises à jour suivantes se font automatiquement, plus besoin de repasser
par un zip.

## ✅ Prérequis

- [vStream](https://kodi-vstream.github.io/) installé et configuré, avec au
  moins une source Pastebin active
- Une clé API [TMDB](https://www.themoviedb.org/settings/api) (gratuite), à
  renseigner dans les paramètres de vStream Listes

## 🛠️ Support

vStream Listes est un addon gratuit et libre de modification, développé sur
mon temps bénévole. Les futures mises à jour dépendront des
[issues](../../issues) ouvertes sur ce dépôt et du temps disponible, sans
garantie de délai.

Pour tout problème lié à **vStream Listes**, ouvre une issue ici. Merci de
ne pas contacter l'équipe de vStream à ce sujet, ce projet n'a aucun lien
avec eux et ils n'ont pas à gérer nos bugs.

## 📄 Licence & crédits

Distribué sous licence GPL-3.0. S'appuie sur [vStream](https://github.com/Kodi-vStream/venom-xbmc-addons)
pour la lecture et sur l'API [TMDB](https://www.themoviedb.org/) pour les
métadonnées. Ce produit utilise l'API TMDB mais n'est ni approuvé ni certifié par TMDB.

Projet non officiel, développé indépendamment : il n'est ni développé, ni
approuvé, ni maintenu par l'équipe de vStream.
