# Code du sujet « Humidité de la bauge » / Code

Scripts Python autonomes qui refont tous les chiffres et toutes les figures depuis `../donnees/` ; aucun fichier extérieur
au sujet. Python 3 avec matplotlib et numpy (Pillow et pandoc servent seulement à la construction du site,
`make construire`). Le script de figures produit la version française (`figures/<id>`) et la version anglaise
(`figures/<id>_en`) ; l'option `--langue fr` ou `--langue en` n'en produit qu'une. À lancer depuis la racine du dépôt (ou
par `make construire`, qui les lance dans l'ordre de `../sujet.toml`). *Standalone scripts that rebuild every number and
figure from the data.*

```
python3 humidite-de-la-bauge/code/grandeurs.py
python3 humidite-de-la-bauge/code/figures_humidite.py
```

## Fichiers

- `lecture.py` — module partagé : chemins du sujet, lecture des pesées, des prélèvements, des étapes et des isothermes
  publiées, courbe de séchage d'un sol, conversion d'une teneur en eau en humidité relative d'équilibre.
- `style.py` — module partagé : couleurs, police, langue des libellés, écriture des figures en PNG et SVG sans date ni
  logiciel.
- `grandeurs.py` — bruit de pesée, teneur en eau de chaque pot et son incertitude, façade regroupée, reprise d'humidité,
  humidité relative équivalente sur chacun des deux sols publiés, bilan d'eau de la peau du cabanon (masse volumique
  supposée) → `donnees/resultats_calcules.json`.
- `figures_humidite.py` — `fig_protocole`, `fig_ecarts`, `fig_bruit`, `fig_profils`, `fig_isotherme`.
- `README.md` — ce fichier.
