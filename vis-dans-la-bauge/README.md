# Vis dans la bauge / Screws in cob

Combien tient une vis à bois dans un vieux mur de bauge (terre crue), de côté et en traction, et comment la poser :
huit essais de côté (cisaillement) le 30/10/2026 et huit en traction (vis tirées hors du mur) le 07/11/2026, sur un
mur existant, avec du matériel courant ; mesures mises à côté des longueurs et des charges conseillées par les
textes, sans charge sûre ; papier de référence bilingue, relevés, code, figures et photos.

*Eight lateral load (shear) tests (30 Oct. 2026) and eight pull-out tests (7 Nov. 2026) on wood screws in an old cob
wall, set next to the lengths and loads advised by published texts: bilingual reference paper, raw readings, code, figures, photos.*

Pages du site : <https://remi.cura.info/renovation-terre-crue/vis-dans-la-bauge/>

## Fichiers

- `sujet.toml` — titre, accroche et état du sujet (FR, EN), scripts à relancer, légendes des figures : lu par
  `outils/construire.py`.

## Sous-dossiers

- `papier/` — le papier de référence en Markdown : `fr/papier.md` et `fr/resume.md`, `en/paper.md` et
  `en/abstract.md`, `references.md` (sources citées, avec adresse et date de consultation). `make construire` en tire
  les `.docx` (FR, EN) et les pages du site. Les PDF exportés de ces `.docx`, s'il y en a, vont dans `papier/pdf/`.
- `donnees/` — relevés bruts, essais, vis, couples de pose, grandeurs calculées ; dictionnaire des colonnes dans son
  `README.md`.
- `code/` — scripts Python qui refont chiffres et figures depuis `donnees/`.
- `figures/` — figures produites par `code/` (PNG pour le `.docx`, SVG pour le site), en français (`<id>`) et en
  anglais (`<id>_en`).
- `photos/` — photos choisies, réduites, sans métadonnées de fichier, et leurs légendes FR/EN (avec la date).
- `site/` — textes des pages du sujet sur le site (présentation, données et code).
