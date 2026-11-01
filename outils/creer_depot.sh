#!/bin/sh
# Crée le dépôt public sur GitHub et y pousse la première version (make depot).
# Étapes : contrôle de publication ; git init sur la branche main si besoin ; identité d'auteur propre à ce dépôt
# (adresse « noreply » de GitHub, pour ne publier aucune adresse e-mail) ; premier commit ;
# gh repo create <compte>/<nom> --public --source . --push. Affiche tout avant de le faire et demande « oui ».
# Sans effet si le dépôt existe déjà sur GitHub.
set -eu
. "$(dirname "$0")/commun.sh"

exiger_gh
titre "Dépôt visé : $ADRESSE_DEPOT"
if depot_distant_existe; then
  printf 'Le dépôt %s existe déjà sur GitHub : rien à créer.\n' "$DEPOT_GH"
  printf 'Pour envoyer de nouvelles modifications : git -C "%s" add -A, git commit, git push.\n' "$RACINE"
  exit 0
fi
exiger_verification

ID=$(gh api user --jq .id) || arreter "impossible de lire l'identifiant GitHub du compte connecté."
CONNECTE=$(gh api user --jq .login)
[ "$CONNECTE" = "$COMPTE_GITHUB" ] || arreter "gh est connecté au compte $CONNECTE, pas $COMPTE_GITHUB (outils/publication.conf)."
COURRIEL="$ID+$COMPTE_GITHUB@users.noreply.github.com"
AUTEUR="Rémi Cura"
DESCRIPTION="Rénover le bâti en terre crue : retours d'expérience, essais, données et code. Renovating earth buildings: field notes."

if [ ! -d .git ]; then
  ETAPE_INIT="git init -b main"
else
  ETAPE_INIT="(dépôt git local déjà présent : branche renommée main si besoin)"
fi
NB=$(git ls-files -co --exclude-standard 2>/dev/null | wc -l | tr -d ' ' || true)
[ -d .git ] || NB="(tous les fichiers non ignorés par .gitignore)"
confirmer \
  "1. $ETAPE_INIT" \
  "2. git config user.name \"$AUTEUR\" et user.email $COURRIEL (dans ce dépôt seulement)" \
  "3. git add -A ; fichiers ajoutés : $NB" \
  "4. git commit -m \"Première version publique\"" \
  "5. gh repo create $DEPOT_GH --public --source . --remote origin --push --homepage $ADRESSE_SITE" \
  "   (crée le dépôt PUBLIC sur GitHub et y pousse la branche main)"

if [ ! -d .git ]; then
  faire git init -b main
else
  faire git branch -M main 2>/dev/null || true
fi
faire git config user.name "$AUTEUR"
faire git config user.email "$COURRIEL"
faire git add -A
if git diff --cached --quiet; then
  printf '\nRien de nouveau à valider.\n'
else
  faire git commit -m "Première version publique" -m "Papier, relevés, code, figures, photos et site du sujet « vis dans la bauge »."
fi
faire gh repo create "$DEPOT_GH" --public --source . --remote origin --push --description "$DESCRIPTION" --homepage "$ADRESSE_SITE"

titre "Vérification"
gh repo view "$DEPOT_GH" --json url,visibility,defaultBranchRef --jq '"adresse : \(.url)\nvisibilité : \(.visibility)\nbranche : \(.defaultBranchRef.name)"'
git status -sb | head -1
printf '\nDépôt créé : %s\nÉtape suivante : make site (publication du site).\n' "$ADRESSE_DEPOT"
