# ITE sur la terre / External insulation on earth

Isoler un mur de bauge (terre crue) par l'extérieur sans lui nuire : pourquoi par l'extérieur, ce qui est non négociable
(ouvert à la vapeur, fermé à la pluie), les deux problèmes (accrocher l'isolation, laisser sortir l'eau de la terre), le
trou réglementaire, et nos pistes selon l'eau du mur. Synthèse des sujets `vis-dans-la-bauge/` et
`humidite-de-la-bauge/` et de calculs d'humidité non publiés ; aucun papier, aucune donnée propre ; trois schémas.

*Insulating a cob wall from the outside without harming it: a synthesis page, three diagrams, no paper and no data of its
own.*

Pages du site : <https://remi.cura.info/renovation-terre-crue/ite-sur-la-terre/>

## Fichiers

- `sujet.toml` — titre, accroche et état du sujet (FR, EN), script à relancer, légendes des figures : lu par
  `outils/construire.py`.

## Sous-dossiers

- `site/` — textes des pages du sujet : `accueil.*.md` (la page elle-même : pourquoi, non-négociable, accroche, humidité,
  trou réglementaire, pistes, limites, références) et `donnees.*.md` (code et figures).
- `code/` — `figures_ite.py`, qui trace les trois schémas en français et en anglais.
- `figures/` — `fig_parements`, `fig_accroche`, `fig_regimes`, en PNG et SVG, français (`<id>`) et anglais (`<id>_en`) ;
  produites par `code/`, ne pas les modifier à la main.
- `photos/` — `legendes.csv` sans photo pour l'instant (la page « Photos » du sujet est vide).
