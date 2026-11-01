# Outils du dépôt / Repository tools

Construction du site et des papiers, contrôle avant publication, création du dépôt GitHub, du site et des versions.
Chaque outil se lance par le `Makefile` depuis la racine du dépôt ; aucun n'agit à distance sans afficher ce qu'il va
faire et demander « oui ». *Build, pre-publication check and publishing scripts, run through the Makefile.*

## Fichiers

- `publication.conf` — **le seul endroit** où écrire le compte GitHub, le nom du dépôt, le DOI (après la première
  version Zenodo), l'ORCID et le contact public facultatif (`CONTACT=` ; vide, les retours passent par les issues
  GitHub seules) ; l'adresse du dépôt et celle du site en sont déduites.
- `publication.py` — lit `publication.conf` et la liste des sujets (dossiers à `sujet.toml`) pour les autres outils.
- `construire.py` — `make construire` : relance le code de chaque sujet (chiffres, figures en français et en
  anglais), produit les papiers `.docx` (pandoc), le site dans `docs/` (vidé et refait à chaque fois), `CITATION.cff`
  et `.zenodo.json`. Les PDF exportés à la main depuis les `.docx` se rangent dans `<sujet>/papier/pdf/` : la
  construction les copie dans `docs/<sujet>/telechargements/` et ajoute un bouton de téléchargement.
- `verifier_publication.py` — `make verifier` : sur le contenu **et le nom** de chaque fichier publié, chemins absolus
  et chemins du dossier de travail, e-mails (même masqués), téléphones, coordonnées GPS en texte, espaces réservés non
  remplis, marqueurs internes, commentaires HTML, métadonnées des images, PDF (repérés par leur contenu), liste blanche
  d'extensions, textes non UTF-8, fichiers Office et OpenDocument ouverts et lus ; avertit sur les montants en euros
  et les nombres à quatre décimales ; adresse du dépôt, liens internes du site, site à jour. Les noms à ne jamais
  publier sont dans une liste locale (ci-dessous). Code de retour 1 en cas d'échec ; n'écrit rien.
- `commun.sh` — fonctions partagées par les trois scripts suivants (contrôle préalable, plan affiché, confirmation).
- `creer_depot.sh` — `make depot` : `git init` sur `main` si besoin, identité d'auteur « noreply » de GitHub propre au
  dépôt, premier commit, `gh repo create <compte>/<nom> --public --source . --push`.
- `publier_site.sh` — `make site` : active GitHub Pages sur `main`, dossier `/docs` (sans effet si déjà fait) et suit
  la construction.
- `creer_version.sh` — `make version VERSION=v1.0.0` : étiquette, envoi de l'étiquette, `gh release create` ; Zenodo
  archive la version si l'intégration est activée.
- `notes_version.md` — notes de la prochaine version (publiées avec elle) : à relire avant chaque `make version`.
- `renommer.py` — `make renommer NOM=<nom>` : change le nom du dépôt avant sa création (configuration et adresses).
- `preparer_photos.py` — réduit les photos d'un sujet et retire toutes leurs métadonnées, depuis les originaux gardés
  hors du dépôt : `python3 outils/preparer_photos.py <sujet> <dossier d'originaux>…`.

Deux fichiers restent sur la machine de l'auteur (ignorés par git, jamais publiés) : `termes_interdits.txt` (ce que
`make verifier` recherche et qui ne doit pas être publié : noms des autres personnes et entreprises, adresse, montants,
noms des dossiers de travail ; trois sections `[noms]`, `[motifs]`, `[chemins]`, format décrit en tête du fichier ;
sans lui, le contrôle échoue) et `procedure_publication.md` (procédure pas à pas, avec les chemins de la machine).
