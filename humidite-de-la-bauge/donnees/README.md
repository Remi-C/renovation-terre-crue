# Données de l'essai d'humidité / Moisture test data

Masses lues le 18/11/2026 sur neuf pots de terre (huit prélèvements de bauge et un témoin vide) avant et après séchage au
four, lieux et outils de prélèvement, étapes de l'essai, points publiés de deux isothermes de bauge de laboratoire, et
grandeurs recalculées par `code/grandeurs.py`. Tous les fichiers sont en UTF-8, séparateur `;` (sauf le JSON), nombres au
point décimal, masses en grammes.

> **En bref** — Trois murs d'une maison en bauge près de Rennes (façade sud, mur de refend des combles, mur d'un cabanon de
> jardin), prélèvements du 17/11/2026, pesées du 18/11/2026. Les **masses** sont lues au centième de gramme ; les
> **teneurs en eau** qui en résultent sont fiables pour les combles et le cabanon (7 à 16 g de terre par pot), pas pour la
> façade (0,5 à 2 g par tranche). Les **humidités relatives** équivalentes sont des lectures sur d'autres terres, pas des
> mesures. Rien ici n'est une valeur admissible ni une caractéristique de la bauge.

*English summary — Masses read on 18 Nov. 2026 on nine pots (eight cob samples and one empty control) before and after oven
drying, sampling places and tools, test steps, published points of two laboratory cob isotherms, and quantities recomputed
by `code/grandeurs.py`. Column names are in French; the dictionary below gives their meaning.*

## Fichiers

- `pesees.csv` — une ligne par pot et par étape (54 lignes) : toutes les lectures de la balance, telles que transcrites de
  la fiche de terrain manuscrite (non publiée).
- `prelevements.csv` — une ligne par pot (9 lignes).
- `etapes.csv` — une ligne par étape (6 lignes).
- `isotherme_phung_2018.csv` — points publiés de deux sols de bauge de laboratoire, relevés dans la thèse de Phung (2018,
  HAL tel-01938827), annexes 2 à 5.
- `resultats_calcules.json` — grandeurs écrites par `code/grandeurs.py` : bruit de pesée, teneur en eau et incertitude par
  pot, façade regroupée (0-20 cm) et 0-10 cm, écarts bruts entre pesées, reprise d'humidité, humidité relative équivalente
  sur chacun des deux sols, pente de l'isotherme entre 80 et 90 %, bilan d'eau de la peau du cabanon (masse volumique
  sèche supposée, non mesurée).

## Dictionnaire des colonnes

### `pesees.csv`

| Colonne | Sens |
|---|---|
| `echantillon` | F1 à F4 (façade sud), C1, C2 (combles), A1, A2 (cabanon), T (témoin, pot vide) |
| `etape` | E0 à E5 (voir `etapes.csv`) |
| `rang_pesee` | pour E1 et E3 : rang de pesée dans la série (1 = pesé le premier, donc le plus chaud) ; vide sinon |
| `lectures_g` | toutes les lectures de la balance pour cette pesée, séparées par des espaces ; la première est la valeur principale écrite sur la fiche. Les lectures répétées, notées sur la fiche par leurs deux derniers chiffres, sont reconstruites en valeur complète (la partie entière la plus proche de la valeur principale) |
| `remarques` | lecture rayée, annotation illisible, lecture reprise ; vide = rien à signaler |

Le témoin n'a pas été pesé en E2 : `lectures_g` vide.

### `prelevements.csv`

| Colonne | Sens |
|---|---|
| `echantillon` | comme ci-dessus |
| `mur` | `facade_sud`, `combles`, `cabanon`, `temoin` |
| `profondeur_cm` | tranche de profondeur depuis la face percée, en cm (« 0-5 » = de 0 à 5 cm) |
| `lieu` | où le prélèvement a été fait, et ce qu'on sait ou ne sait pas de la face percée |
| `outil` | outil de perçage |

### `etapes.csv`

| Colonne | Sens |
|---|---|
| `etape` | E0 à E5, dans l'ordre chronologique |
| `libelle` | nom court de l'étape |
| `four` | passage au four qui précède la pesée |
| `conditions_pesee` | conditions de la pesée, telles que dites par l'auteur |
| `etat_thermique_pot` | pot froid, tiède ou chaud au moment de la pesée |
| `ordre_de_pesee` | pour E1 et E3 : ordre des pots dans la série, du premier pesé au dernier |

### `isotherme_phung_2018.csv`

| Colonne | Sens |
|---|---|
| `sol` | `A` ou `B` : les deux mélanges de terre de la thèse |
| `serie` | `sorption` (de 5 à 90 % d'humidité relative, annexes 4 et 5), `desorption` (de 90 % à 5 %, mêmes annexes ; le point à 90 % est celui de fin de sorption), `retention` (courbe de rétention en séchage, de 9 % à la saturation, annexes 2 et 3) |
| `hr_pct` | humidité relative d'équilibre, % |
| `w_pct` | teneur en eau, % de la masse sèche ; colonne « 1 % de fibre » des annexes 4 et 5, colonne « 1 %-Paille » des annexes 2 et 3 |
| `source` | annexe de la thèse |

La courbe de séchage utilisée par `code/lecture.py` assemble la désorption de 5 à 90 % et la rétention de 93 % à la
saturation : ce sont deux séries d'éprouvettes différentes, leur raccord de 90 à 93 % est le point faible. Ce sont **deux
autres terres** que celles des murs mesurés.

### `resultats_calcules.json`

Écart-types de pesée en g ; teneurs en eau et incertitudes en % de la masse sèche (points de pourcentage pour les
incertitudes) ; humidités relatives en % ; `null` quand une borne sort de la courbe publiée. `hr_pct` donne, pour chaque sol,
l'humidité relative de *w* (`centre`), de *w* − 1 σ (`basse`) et de *w* + 1 σ (`haute`).

## Ce qui est mesuré, ce qui ne l'est pas

- **Mesuré** : masses au centième de gramme, plusieurs lectures par pesée ; dérive d'un pot témoin vide à travers toutes les
  étapes.
- **Calculé** : teneur en eau, incertitude de pesée, humidité relative équivalente sur d'autres terres, bilan d'eau.
- **Écarté** : la série E3 (décalage commun de la balance sur trois pesées de suite) ; E2 et E4 ne servent pas à la teneur en
  eau.
- **Non mesuré** : isotherme de ces terres ; masse volumique ; teneur en pierres ; humidité de l'air dans les locaux ;
  face depuis laquelle la façade a été percée ; ce qui a arrêté le perçage de la façade ; pot d'où la pierre a été retirée.

## Licence

Données : CC BY 4.0 (voir `LICENSE` à la racine du dépôt). Les points de `isotherme_phung_2018.csv` sont des valeurs
publiées dans la thèse citée, reprises pour la reproductibilité ; la thèse est en accès ouvert sur HAL.
