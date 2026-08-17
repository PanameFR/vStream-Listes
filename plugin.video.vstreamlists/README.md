# vStream Listes (`plugin.video.vstreamlists`)

Extension Kodi independante pour gerer des listes personnelles de films/series
(identifies par TMDB), lues via vStream / source Pastebin. Ne modifie aucun
fichier de vStream — voir le cahier des charges fourni pour le detail des
regles d'architecture.

## Installation

1. Copier le dossier `plugin.video.vstreamlists` dans le dossier `addons` de
   Kodi (ou l'installer via un zip depuis "Installer depuis un fichier zip").
2. Avoir `plugin.video.vstream` deja installe et configure (au moins une
   source Pastebin renseignee).
3. Ouvrir **vStream Listes**, aller dans ses parametres et renseigner une
   **cle API TMDB** (compte gratuit sur themoviedb.org, section API). Sans
   cette cle, les listes restent utilisables mais aucune recherche/metadonnee
   TMDB n'est possible.

## Ce qui est implemente (V1)

- Creer / renommer / supprimer une liste, avec confirmation de suppression.
- Ajouter un film ou une serie (recherche TMDB manuelle depuis une liste).
- Retirer un element, le deplacer ou le copier vers une autre liste.
- Reordonner listes et elements (monter/descendre/premier/dernier).
- Ouverture d'un element via `VStreamPastebinAdapter`, qui construit l'URL
  `plugin://plugin.video.vstream/?site=pastebin&function=showMovies&sTmdbId=...`
  (parametre natif de vStream qui filtre son contenu Pastebin par ID TMDB,
  toutes sources Pastebin configurees confondues) puis laisse entierement
  vStream gerer la suite (choix du lien, saisons/episodes, lecture).
- Menu contextuel externe **"Ajouter a mes listes"** visible uniquement sur
  les elements `plugin.video.vstream` provenant de `site=pastebin`.
- Cache local des metadonnees TMDB (SQLite, `lists.db`, propre a cette
  extension) avec rafraichissement automatique selon une duree configurable.
- Journalisation optionnelle (parametre "Activer les journaux de
  debogage").

## Limitations connues / a faire avant mise en prod reelle

- `icon.png` et `fanart.png` sont des aplats de couleur generes
  automatiquement, a remplacer par de vrais visuels avant diffusion.
- Le routage vStream (`VStreamPastebinAdapter`) a ete verifie contre le code
  source public de vStream (`resources/sites/pastebin.py` /
  `default.py`, depot `Kodi-vStream/venom-xbmc-addons`) au moment du
  developpement. Si une future version de vStream renomme `sTmdbId` /
  `showMovies` / `site=pastebin`, seul `resources/lib/adapters/vstream.py`
  doit etre adapte.
- Pas encore de page de details intermediaire (section 75 du cahier des
  charges), de recherche interne aux listes, ni de synchronisation
  multi-Kodi — explicitement hors perimetre V1.
- Non teste dans un Kodi reel a ce stade (pas d'environnement Kodi
  disponible dans cette session) : a valider sur un poste avec Kodi +
  vStream installes avant usage.
