# Données des essais / Test data

Relevés bruts des essais de cisaillement du 30/10/2026 (vis chargées de côté dans un mur en bauge) et des essais en
traction du 07/11/2026 (vis tirées hors du même mur), caractéristiques des vis, couples de pose notés, et grandeurs
recalculées par `code/grandeurs.py`. Tous les fichiers sont en UTF-8,
séparateur `;`, nombres au point décimal.

> **En bref** — 8 essais de côté et 8 en traction, un seul mur (bauge sèche d'un cabanon de jardin d'au moins 50 ans, Clos Poulain, région de
> Rennes), deux journées. Les **efforts** (lus au peson) sont fiables. Les **déplacements** (lus au comparateur) le sont
> moins : le comparateur est porté par la platine de réaction, qui bouge un peu, et sa tige est inclinée de 25 à 45°.
> Rien ici n'est une valeur admissible ni une caractéristique de la bauge.

*English summary — Raw readings of eight lateral (shear) load tests (30 Oct. 2026) and eight pull-out tests
(7 Nov. 2026) on screws driven into a dry cob wall; screw data; installation torques; derived quantities. Loads (read on the crane scale) are reliable; displacements (dial gauge
carried by the reaction plate, stem inclined 25–45°) are indicative. Column names are in French; the dictionary below
gives their meaning.*

## Fichiers

- `releves_cisaillement_2026_10_30.csv` — relevés ligne à ligne, tels que notés sur la fiche d'essai, sans retouche
  (y compris les fautes de frappe et les remarques). Une ligne par lecture.
- `releves_arrachement_2026_11_07.csv` — relevés des essais en traction, une ligne par charge, tels que notés le
  07/11/2026 avec les précisions de l'auteur du même jour (pré-trous, filet hors de la bauge, longueur notée), sans
  accents.
- `essais.csv` — une ligne par essai, de côté (C1 à C8) et en traction (A1 à A8) : la vis, l'ancrage, la pièce serrée,
  le pré-trou, l'issue, et le statut des déplacements (ce qui est écarté et pourquoi).
- `vis.csv` — caractéristiques des vis essayées, une ligne par référence achetée, telles que les publient les
  fabricants (agrément ETA-21/0751, brochure et pages produit fischer) ; source, pages et date de consultation par ligne.
- `couple_pose.csv` — couple de vissage noté à la pose (débrayage de la visseuse), essais des 10/10 et 30/10/2026.
- `resultats_calcules.json` — grandeurs tirées des relevés **sans aucun modèle**, écrites par `code/grandeurs.py` :
  effort maximal, rupture, déplacement à 25, 50 et 100 kg sur la première charge (interpolé entre deux lectures),
  résiduels, part rendue à la décharge, raideurs de l'assemblage. Les clés `raideur_…_assemblage_…` (kg/mm) sont
  celles de tout le montage tel que le comparateur le lit (vis, planche, platine de réaction qui recule) : ce n'est
  pas une raideur de la bauge seule. Le papier en tire une fourchette large pour l'assemblage (section « Sous 100 kg,
  la profondeur change peu ; le diamètre, si »). Clé `arrachement` : pour chaque essai en traction et chaque longueur
  de vis dans la bauge, la rupture, sinon la charge la plus haute tenue (un minimum).

## Dictionnaire des colonnes

### `releves_cisaillement_2026_10_30.csv`

| Colonne | Sens |
|---|---|
| `essai` | C1 à C8, dans l'ordre où les essais ont été faits |
| `vis` | diamètre × longueur, en mm (ex. `10x260`) |
| `position` | emplacement autour de la platine de réaction, de 1/6 à 6/6 (voir `figures/fig_implantation`) ; C7 entre 5/6 et 6/6 ; C8 dans le trou de C1 |
| `eprouvette` | la planche serrée par la vis (chêne ou douglas) ; C8 : aucune, corde passée sur la tête de vis |
| `pretrou` | diamètre × longueur du foret de pré-perçage, en mm ; « Pas de pretrou » : aucun |
| `pose` | ce qui a été noté à la pose : réglage de la visseuse au débrayage (« S4 » = molette 4) et longueur restant à visser (« reste 10cm ») |
| `rang` | ordre de la lecture dans l'essai |
| `F_kg` | effort lu au peson, kg (point haut atteint au palier) ; 0 = chaîne détendue |
| `delta_mm` | déplacement lu au comparateur au même instant, mm ; vide = non lu |
| `reglage_visseuse` | réglage utilisé pour tendre la chaîne à l'écrou (« Max 2 » = molette maximale, 2e passe) |
| `observation` | remarque notée pendant l'essai ; « RAZ » = remise à zéro du comparateur |

Lecture d'un essai : une ligne à 0 kg clôt une montée de charge (le déplacement lu alors est le résiduel) ; la montée
suivante repart de zéro si une remise à zéro est notée. Règles complètes : `code/lecture.py`.

### `essais.csv`

| Colonne | Sens |
|---|---|
| `sollicitation` | `cisaillement` (effort parallèle au mur) ; `arrachement` (vis tirée dans son axe, hors du mur) |
| `ancrage_bauge_mm` | longueur de vis dans la bauge = longueur − 45 mm de planche ; C8 : toute la vis (tête à fleur de mur). L'épaisseur des planches de chêne n'a pas été mesurée (45 mm supposés). Arrachement : longueur à la rupture (les charges tenues plus profond sont dans les relevés) |
| `position` | cisaillement : emplacement autour de la platine de réaction ; arrachement : « — » (tous à ≈ 1,10 m du sol) |
| `effort_max_kg` | effort le plus haut écrit pour l'essai |
| `issue` | rupture notée et ses mots, ou « aucune rupture (essai arrêté) » : l'effort de rupture est alors plus haut que `effort_max_kg` |
| `statut_des_deplacements` | lectures écartées et pourquoi (décision de l'auteur, 31/10/2026) |

### `releves_arrachement_2026_11_07.csv`

| Colonne | Sens |
|---|---|
| `essai` | A1 à A8, dans l'ordre où les essais ont été faits |
| `vis`, `d_mm`, `longueur_mm` | la vis, son diamètre et sa longueur (A8 : longueur non notée) |
| `pretrou` | `Ø5`, `Ø6 long` (foret long, sur toute la longueur de la vis), `aucun` |
| `rang` | ordre de la charge dans l'essai |
| `devisse_mm` | longueur dévissée depuis la pose à fond, cumulée |
| `air_mm` | filet resté hors de la bauge, là où le mur n'est pas plan |
| `prof_notee_mm` | longueur de vis dans la bauge notée sur le moment, quand elle l'a été |
| `F_bas_kg`, `F_haut_kg` | charge lue au peson ; deux valeurs quand elle a été notée en fourchette |
| `issue` | `tenu` (la vis a tenu au moins quelques secondes) ou `cede` (rupture) |
| `reglage` | réglage de couple de la visseuse qui tournait la tige filetée (`S1` à `S9`, « max » = débrayage) : il limite l'effort, le peson fait foi |
| `mode`, `observation` | ce qui a été vu à la rupture (glissement, cône), remarques |

Longueur de vis dans la bauge (`code/grandeurs.py`) = `longueur_mm` − 15 mm pris dans la platine − `devisse_mm` −
`air_mm`, sauf si `prof_notee_mm` est rempli (A5 à la rupture : 90 mm notés, 85 calculés). A8 : 60 mm notés ; la vis
n'a que ≈ 50 mm de filet (mesuré sur photo) et seul le filet était dans la bauge (l'auteur, 08/11/2026) : 50 mm
retenus.

### `vis.csv`

Une ligne par vis achetée et essayée (référence et longueur). Toutes les valeurs sont celles que publie le fabricant ;
aucune n'a été mesurée sur les vis. Une valeur que le fabricant ne publie pas est écrite `non publiée`. Les valeurs
d'acier de l'agrément sont **caractéristiques** : des valeurs basses, que 95 % des vis atteignent ou dépassent.

| Colonne | Sens |
|---|---|
| `vis` | nom court : marque, gamme, diamètre × longueur en mm |
| `fabricant`, `designation`, `article` | qui la fabrique ou la vend, sa désignation commerciale, son numéro d'article |
| `longueur_mm`, `longueur_filetee_mm` | longueur totale (sous la tête comprise) et longueur filetée ; la différence est la partie lisse sous la tête |
| `d_filet_mm`, `d_noyau_mm` | diamètre extérieur du filet ; diamètre du noyau (la tige pleine sous le filet) |
| `d_tige_lisse_mm` | diamètre de la partie lisse, entre la tête et le filet |
| `tete`, `d_tete_mm`, `hauteur_tete_mm` | forme, diamètre et hauteur de la tête |
| `empreinte` | empreinte de vissage (Torx TX, cruciforme Pozidriv) |
| `pointe` | forme de la pointe et sa longueur |
| `acier`, `revetement` | acier et protection contre la corrosion ; pour l'inox, la nuance |
| `resistance_torsion_Nm` | couple qui casse la vis en torsion (valeur caractéristique) |
| `limite_de_pose_Nm` | **calculé** : `resistance_torsion_Nm` / 1,5. L'agrément demande que le couple moyen de pose dans le bois reste 1,5 fois sous la résistance à la torsion (bois de référence de 480 kg/m³) |
| `moment_plastique_My_Nmm` | moment qui fait plier la vis durablement (moment de plastification) |
| `resistance_traction_acier_kN` | effort de traction qui casse l'acier de la vis |
| `limite_elastique_Nmm2` | limite d'élasticité de l'acier |
| `pre_percage_bois_mm` | diamètre de pré-perçage recommandé par le fabricant **dans le bois** (résineux et feuillus) ; aucun fabricant n'en donne pour la terre |
| `couple_pose_fabricant_Nm` | couple de pose recommandé par le fabricant ; aucun n'en publie (voir `limite_de_pose_Nm`) |
| `agrement` | évaluation technique européenne qui couvre la vis, et pour quel matériau |
| `source` | document, tableau et page de chaque valeur |
| `consulte_le` | date de consultation des sources (AAAA-MM-JJ) |

Vis inox 6×80 : marque de marchand, sans fiche technique ; seuls sont connus le diamètre, la longueur, la tête
demi-ronde, le filetage total et l'acier inox A2 (famille des inox austénitiques au chrome-nickel ; nuance exacte non
publiée).

### `couple_pose.csv`

`reste_a_visser_mm` longueur de vis encore dehors au débrayage ; `filet_dans_la_bauge_mm` = longueur − reste − 45 mm de
planche ; `couple_min_Nm`, `couple_max_Nm` couple correspondant au réglage noté. Table du réglage (notice de la visseuse
Metabo SB 18 LTX-3 BL Q I, 1re vitesse) : molette 4 = 7 N·m, molette 8 = 16 N·m, maximum ≈ 60 N·m ; en 2e vitesse,
ces couples sont environ deux fois plus bas. La vitesse n'a pas été notée le 30/10 : 1re supposée. Le couple de la
planche traversée n'est pas retiré. Le 10/10, le plafond de la visseuse a été contrôlé à la clé (18–20 N·m).
**Le 30/10, ces réglages ne donnent pas un couple par centimètre de bauge** : ils ne disent que le réglage où la
visseuse a débrayé à ce moment-là. Ce que l'auteur retient de la pose du 30/10 (01/11/2026) : avec un pré-trou
(6 mm sur presque toute la longueur pour C1, C2 et C7 ; 5 mm partiel pour C3 et C4), presque tout a été posé à
20 N·m au plus (réglage 10 de la visseuse), jusqu'à 21,5 cm de bauge ; C7 a été
finie au couple maximal à cause d'un caillou. C'est ce que montre `figures/fig_pre_trou`.

## Ce qui est mesuré, ce qui ne l'est pas

- **Mesuré** : efforts au peson (de côté et en traction) ; déplacements au comparateur (au 1/100 mm, petites lectures notées au 0,1 mm) ;
  ruptures et remarques notées sur le moment ; réglage de la visseuse au débrayage.
- **Écarté** : C1, 1re charge et 2e cycle (une manille frottait sur la platine) ; C7, deux premières lectures (le
  comparateur touchait le peson).
- **Contexte seulement** : déplacements de C8 (touche sur une tête de vis très petite, trou déjà déformé par C1). Son
  effort (300 kg) est certain ; à l'œil, son déplacement était le plus grand des huit essais, au moins 3 mm à 300 kg.
- **Non mesuré** : déplacements en traction (pas de comparateur) ; état des vis C2 à C7 au démontage ; angle de la tige du comparateur, essai par essai ; teneur en eau,
  densité et levée de la bauge ; épaisseur des planches de chêne ; couple de pose à la clé le 30/10 ; effort stabilisé
  à chaque palier (sauf C7 : 174 → 137 kg en 30 s, comparateur immobile à 0,8 mm).
- **Le mur** : bauge en place, non prélevée ; épaisseur ≥ 45 cm ; protégée par un bardage sur lame d'air, sans signe
  d'humidité ; très sèche au toucher. De côté : planches à ≈ 1,70 m du sol, platine de réaction à ≈ 1,10 m.
  En traction : vis à ≈ 1,10 m du sol, bauge dressée au rabot (5 mm enlevés au plus).

## Licence

Données : CC BY 4.0 (voir `LICENSE` à la racine du dépôt).
