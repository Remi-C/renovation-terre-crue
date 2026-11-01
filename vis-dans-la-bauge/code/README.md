# Code du sujet « Vis dans la bauge » / Code

Scripts Python autonomes qui refont tous les chiffres et toutes les figures depuis `../donnees/`. Python 3 avec
matplotlib et numpy (Pillow et pandoc servent seulement à la construction du site, `make construire`). Chaque script
de figures produit la version française (`figures/<id>`) et la version anglaise (`figures/<id>_en`) ; l'option
`--langue fr` ou `--langue en` n'en produit qu'une. À lancer depuis la racine du dépôt (ou par `make construire`, qui les lance dans l'ordre de
`../sujet.toml`). *Standalone scripts that rebuild every number and figure from the data.*

```
python3 vis-dans-la-bauge/code/grandeurs.py
python3 vis-dans-la-bauge/code/figures_essais.py
python3 vis-dans-la-bauge/code/figure_pre_trou.py
python3 vis-dans-la-bauge/code/schemas.py
```

## Fichiers

- `lecture.py` — module partagé : lecture des relevés, découpage en montées de charge, lectures écartées.
- `style.py` — module partagé : couleurs, police, langue des libellés, écriture des figures en PNG et SVG sans date
  ni logiciel.
- `grandeurs.py` — grandeurs tirées des relevés sans aucun modèle → `donnees/resultats_calcules.json`.
- `figures_essais.py` — `fig_efforts`, `fig_premiere_charge`, `fig_ressort_freine`.
- `figure_pre_trou.py` — `fig_pre_trou` : couple de pose sans pré-trou (combles, 10/10/2026, prolongé par le calcul)
  et avec pré-trou (cabanon, 30/10/2026), face aux limites de la vis.
- `schemas.py` — `fig_implantation`, `fig_montage`, `fig_theorie`, `fig_platine` (schémas, cotes approximatives).
- `chiffres_site.py` — chiffres clés de la page de présentation du sujet sur le site.
- `README.md` — ce fichier.
