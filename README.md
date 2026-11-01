# Rénover le bâti en terre crue : retours d'expérience / Renovating earth buildings: field notes

**Français** — Retours d'expérience d'un particulier qui rénove une maison en bauge (terre crue) près de Rennes.
Quand une question pratique n'a pas de réponse publiée, on essaie, on mesure avec du matériel courant, et on publie
tout : relevés bruts, code qui refait chaque chiffre et chaque figure, photos, et les conseils qu'on croit pouvoir en
tirer. Ce ne sont pas des essais de laboratoire : ils sont là pour être discutés, refaits, corrigés.

**English** — Field notes from a homeowner renovating a cob (earth) house near Rennes, France: tests made with ordinary
tools, raw readings, code that rebuilds every number and figure, photos, and the advice we think they support. Not
laboratory tests: they are here to be discussed, repeated and corrected.

Site : <https://remi-c.github.io/renovation-terre-crue/> (français, English)

## Sujets / Topics

| Dossier | Sujet | Topic | État / Status |
|---|---|---|---|
| [`vis-dans-la-bauge/`](vis-dans-la-bauge/) | Vis dans la bauge : combien tient une vis chargée de côté dans un vieux mur de bauge, et comment la poser | Screws in cob: how much a screw loaded sideways holds in an old cob wall, and how to drive it | cisaillement fait (30/10/2026), arrachement à venir / lateral load done, pull-out to come |

## Organisation

- Un sujet = un dossier à la racine (`papier/`, `donnees/`, `code/`, `figures/`, `photos/`, `site/`, `sujet.toml`).
- `site/` : gabarit, style et accueil du site ; `docs/` : site construit, servi par GitHub Pages (ne pas modifier).
- `outils/` : construction, contrôle de publication, création du dépôt, du site et des versions.

```
make construire   # refait chiffres, figures, papiers .docx et site — rebuilds everything
make verifier     # contrôle avant publication — pre-publication check
```

Python 3 avec matplotlib et numpy (code), Pillow (photos) ; pandoc 3. Python 3 with matplotlib and numpy (code),
Pillow (photos); pandoc 3.

## Retours / Feedback

Retours : les [issues](https://github.com/Remi-C/renovation-terre-crue/issues) du dépôt GitHub.
Feedback: the GitHub repository's [issues](https://github.com/Remi-C/renovation-terre-crue/issues).

## Citer / Cite · Licence

Voir / see [`CITATION.cff`](CITATION.cff) (bouton « Cite this repository » de GitHub). Texte, données, figures, photos :
CC BY 4.0 ([`LICENSE`](LICENSE)) ; code : MIT ([`LICENSE-code`](LICENSE-code)). © 2026 Rémi Cura.
