# Gabarit et pages communes du site / Site template

Ce qui est commun à tout le site : gabarit, style, accueil du projet. Les pages propres à un sujet sont dans son
dossier (`<sujet>/site/`). `make construire` assemble le tout dans `docs/`. *Shared site template, stylesheet and
project home page.*

## Fichiers

- `gabarit.html` — gabarit pandoc de toutes les pages : en-tête (nom du projet, langue, fil d'Ariane, menu), pied.
- `style.css` — feuille de style, claire et sombre, lisible sur téléphone.
- `images.lua` — filtre pandoc : chemins des figures (SVG sur le site, PNG dans le `.docx`) et des photos, lien de
  `references.md` vers le dépôt.
- `accueil.fr.md`, `accueil.en.md` — accueil du projet ; `{{sujets}}` y reçoit la carte de chaque sujet.
- `en_preparation.fr.md`, `en_preparation.en.md` — page qui remplace un papier pas encore écrit.
