Everything behind the paper is in the [`vis-dans-la-bauge/`]({{arbre_sujet}}) folder of the GitHub repository: raw
readings, the code that rebuilds the numbers and figures, and the photos. Text, data, figures and photos under
CC BY 4.0; code under the MIT licence. File and column names are in French; the data dictionary explains them.

## Data

- [`donnees/releves_cisaillement_2026_10_30.csv`]({{fichier_sujet}}/donnees/releves_cisaillement_2026_10_30.csv):
  readings as written down during the tests, one row per reading (load read on the crane scale, displacement read on
  the dial gauge, remarks).
- [`donnees/essais.csv`]({{fichier_sujet}}/donnees/essais.csv): one row per test (screw, embedment, board, pilot
  hole, outcome, discarded readings and why).
- [`donnees/vis.csv`]({{fichier_sujet}}/donnees/vis.csv) and
  [`donnees/couple_pose.csv`]({{fichier_sujet}}/donnees/couple_pose.csv): screw data, driving torque noted at
  installation.
- [`donnees/resultats_calcules.json`]({{fichier_sujet}}/donnees/resultats_calcules.json): what the readings give
  without any model.
- Column dictionary and status of each reading: [`donnees/README.md`]({{fichier_sujet}}/donnees/README.md).

## Code

Python 3 with matplotlib and numpy; Pillow and pandoc for the build. Each figure script writes the French and the
English version (suffix `_en`). From the repository root:

```
python3 vis-dans-la-bauge/code/grandeurs.py        # numbers derived from the readings
python3 vis-dans-la-bauge/code/figures_essais.py   # measurement figures
python3 vis-dans-la-bauge/code/figure_pre_trou.py  # driving torque and pilot hole
python3 vis-dans-la-bauge/code/schemas.py          # diagrams
make construire                                    # all of the above, plus the paper (.docx) and this site
```

## Figures

{{figures}}

## How to cite

{{citation}}
