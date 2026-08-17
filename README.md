# vStream Listes - depot Kodi

Ce depot heberge le code source de **vStream Listes**
(`plugin.video.vstreamlists`) ainsi que son propre depot Kodi
(`repository.vstreamlists`), sur le meme modele que celui de vStream
(`repository.vstream` + `raw.githubusercontent.com`).

## Structure

```
plugin.video.vstreamlists/   code source de l'extension
repository.vstreamlists/     petit addon "depot" (pointe vers ce repo GitHub)
tools/build_repo.py          regenere addons.xml / addons.xml.md5 / repo/
repo/                        (genere) zips + fiches par addon
addons.xml, addons.xml.md5   (generes) index consomme par Kodi pour les MAJ
index.html                   (genere) page de navigation pour Kodi/GitHub Pages
```

Apres toute modification du code d'un addon (nouvelle version dans son
`addon.xml`), relancer :

```bash
python tools/build_repo.py
```

puis commit + push. C'est cette regeneration + push qui met a jour le depot,
il n'y a pas d'automatisation CI pour l'instant.

## Installation dans Kodi (comme vStream)

1. **Ajouter la source** : Systeme -> Gestionnaire de fichiers -> Ajouter une
   source -> Aucun -> saisir
   `https://GITHUB_USER.github.io/REPO_NAME/` (nommer par ex. "repo vstreamlists").
2. **Installer le depot** : Extensions -> Installer depuis un fichier zip ->
   choisir la source ajoutee -> `repo/repository.vstreamlists/repository.vstreamlists-1.0.0.zip`.
3. **Installer l'extension** : Extensions -> Installer depuis un depot ->
   "vStream Listes Repository" -> Extensions video -> vStream Listes ->
   Installer.

Les mises a jour futures sont ensuite automatiques (Kodi interroge
`addons.xml` / `addons.xml.md5` via `raw.githubusercontent.com`, comme le
fait `repository.vstream` pour vStream).

## A faire pour publier

`GITHUB_USER` et `REPO_NAME` ci-dessus (et dans
`repository.vstreamlists/addon.xml`) sont des valeurs a remplacer une fois
le depot GitHub cree, puis GitHub Pages a activer sur la branche `main`
(racine).
