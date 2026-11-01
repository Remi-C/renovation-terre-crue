# Vis dans la bauge / Screws in cob

Combien tient une vis à bois chargée de côté dans un vieux mur de bauge (terre crue), et comment la poser : huit essais
de cisaillement sur un mur existant, le 30/10/2026, avec du matériel courant ; papier de référence bilingue,
relevés, code, figures et photos. Les essais d'arrachement (vis tirées hors du mur) sont prévus en novembre 2026 : le
papier leur garde une section « à faire », les données les accueilleront au même format.

*Eight lateral load (shear) tests on wood screws in an old cob wall, 30 Oct. 2026: bilingual reference paper, raw
readings, code, figures, photos. Pull-out tests to come (November 2026).*

Pages du site : <https://remi-c.github.io/renovation-terre-crue/vis-dans-la-bauge/>

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
