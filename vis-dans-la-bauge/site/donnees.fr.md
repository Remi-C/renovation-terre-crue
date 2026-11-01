Tout ce qui sert au papier est dans le dossier [`vis-dans-la-bauge/`]({{arbre_sujet}}) du dépôt GitHub : les relevés
bruts, le code qui refait les chiffres et les figures, les photos. Texte, données, figures et photos sous licence
CC BY 4.0 ; code sous licence MIT.

## Les données

- [`donnees/releves_cisaillement_2026_10_30.csv`]({{fichier_sujet}}/donnees/releves_cisaillement_2026_10_30.csv) :
  les relevés tels que notés pendant les essais, une ligne par lecture (effort au peson, déplacement au comparateur,
  remarques).
- [`donnees/essais.csv`]({{fichier_sujet}}/donnees/essais.csv) : une ligne par essai (vis, ancrage, planche,
  pré-trou, issue, lectures écartées et pourquoi).
- [`donnees/vis.csv`]({{fichier_sujet}}/donnees/vis.csv) et
  [`donnees/couple_pose.csv`]({{fichier_sujet}}/donnees/couple_pose.csv) : caractéristiques des vis, couple de
  vissage noté à la pose.
- [`donnees/resultats_calcules.json`]({{fichier_sujet}}/donnees/resultats_calcules.json) : ce que les relevés donnent
  sans aucun modèle.
- Dictionnaire des colonnes et statut de chaque lecture : [`donnees/README.md`]({{fichier_sujet}}/donnees/README.md).

## Le code

Python 3 avec matplotlib et numpy ; Pillow et pandoc pour la construction. Chaque script de figures produit la
version française et la version anglaise (suffixe `_en`). Depuis la racine du dépôt :

```
python3 vis-dans-la-bauge/code/grandeurs.py        # chiffres tirés des relevés
python3 vis-dans-la-bauge/code/figures_essais.py   # figures des mesures
python3 vis-dans-la-bauge/code/figure_pre_trou.py  # couple de pose et pré-trou
python3 vis-dans-la-bauge/code/schemas.py          # schémas
make construire                                    # tout, plus le papier (.docx) et ce site
```

## Les figures

{{figures}}

## Citer

{{citation}}
