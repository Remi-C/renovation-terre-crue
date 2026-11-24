# Humidité de la bauge / Moisture in cob

Quelle eau contient un vieux mur de bauge (terre crue) ? Neuf prélèvements de terre dans trois murs d'une maison en bauge
près de Rennes (17/11/2026), pesés tels quels puis après séchage au four de cuisine (18/11/2026) : un cœur sec et une peau
mouillée (10 % d'eau sur 10 cm dans le mur d'un cabanon), une façade trop peu fournie en terre pour un profil (5,3 ± 1,6 %
regroupée) ; puis ce que cela change avant d'isoler. Papier bilingue en trois parties, relevés, code, figures et photos.

*Nine earth samples from three walls of a cob house near Rennes (17 Nov. 2026), weighed as taken and after kitchen-oven drying
(18 Nov. 2026): a dry core and a wet skin (10 % water over 10 cm in a garden shed wall), a façade with too little earth for a
profile (5.3 ± 1.6 % pooled); then what this changes before insulating. Bilingual paper in three parts, raw readings, code,
figures, photos.*

Pages du site : <https://remi.cura.info/renovation-terre-crue/humidite-de-la-bauge/>

## Fichiers

- `sujet.toml` — titre, accroche et état du sujet (FR, EN), scripts à relancer, légendes des figures : lu par
  `outils/construire.py`.

## Sous-dossiers

- `papier/` — le papier de référence en Markdown, en trois parties (la mesure, son interprétation, ce que cela change pour
  isoler) : `fr/papier.md` et `fr/resume.md`, `en/paper.md` et `en/abstract.md`, `references.md` (sources citées, avec
  adresse et date de consultation). `make construire` en tire les `.docx` (FR, EN) et les pages du site.
- `donnees/` — masses lues, prélèvements, étapes, points publiés de deux isothermes de bauge, grandeurs calculées ;
  dictionnaire des colonnes dans son `README.md`.
- `code/` — scripts Python qui refont chiffres et figures depuis `donnees/`.
- `figures/` — figures produites par `code/` (PNG pour le `.docx`, SVG pour le site), en français (`<id>`) et en anglais
  (`<id>_en`).
- `photos/` — six photos choisies (four, poste de pesée, pots après séchage, feuilles de notes), réduites, sans
  métadonnées, et leurs légendes FR/EN (avec la date).
- `site/` — textes des pages du sujet sur le site (présentation, données et code).
