#!/bin/sh
# Crée une version : étiquette git + publication GitHub (« release ») ; si l'intégration Zenodo est activée pour ce
# dépôt, Zenodo archive la version et lui donne un DOI (make version VERSION=v1.0.0).
# Notes de version : outils/notes_version.md (à relire avant chaque version).
# Refuse si le contrôle échoue, si des modifications ne sont pas sur GitHub, ou si l'étiquette existe déjà.
set -eu
. "$(dirname "$0")/commun.sh"

V="${1:-}"
printf '%s' "$V" | grep -Eq '^v[0-9]+\.[0-9]+(\.[0-9]+)?$' || arreter "usage : make version VERSION=v1.0.0 (v, puis numéros séparés par des points)."
exiger_gh
exiger_verification
titre "Version $V de $DEPOT_GH"
depot_distant_existe || arreter "le dépôt $DEPOT_GH n'existe pas encore sur GitHub : lancer d'abord make depot."
[ -z "$(git status --porcelain)" ] || arreter "des fichiers sont modifiés ou non validés : git add -A ; git commit ; git push, puis relancer."
git fetch --quiet origin main --tags
[ "$(git rev-parse HEAD)" = "$(git rev-parse origin/main)" ] || arreter "la branche locale diffère de GitHub : git push (ou git pull), puis relancer."
git rev-parse -q --verify "refs/tags/$V" >/dev/null && arreter "l'étiquette $V existe déjà en local : choisir un autre numéro."
[ -z "$(git ls-remote --tags origin "refs/tags/$V")" ] || arreter "l'étiquette $V existe déjà sur GitHub : choisir un autre numéro."
[ -s outils/notes_version.md ] || arreter "outils/notes_version.md est vide : y écrire ce que contient la version."

titre "Notes de version (outils/notes_version.md)"
cat outils/notes_version.md
confirmer \
  "1. git tag -a $V -m \"Version $V\"   (sur le commit $(git rev-parse --short HEAD))" \
  "2. git push origin $V" \
  "3. gh release create $V --verify-tag --title \"$NOM_DEPOT $V\" --notes-file outils/notes_version.md" \
  "Zenodo n'archive la version et ne donne de DOI que si l'interrupteur de ce dépôt est déjà activé sur" \
  "https://zenodo.org/account/settings/github/ (voir la procédure) ; sinon, l'activer AVANT de répondre « oui »."

faire git tag -a "$V" -m "Version $V"
faire git push origin "$V"
faire gh release create "$V" --verify-tag --title "$NOM_DEPOT $V" --notes-file outils/notes_version.md

titre "Vérification"
gh release view "$V" --json url,tagName,publishedAt --jq '"version : \(.tagName)\nadresse : \(.url)\npubliée : \(.publishedAt)"'
printf '\nDOI : quelques minutes plus tard, sur https://zenodo.org/account/settings/github/repository/%s\n' "$DEPOT_GH"
printf 'Le reporter ensuite dans outils/publication.conf (ligne DOI=), puis make construire, commit, push.\n'
