#!/bin/sh
# Publie le site avec GitHub Pages, servi depuis le dossier docs/ de la branche main (make site).
# Idempotent : si Pages est déjà réglé sur main /docs, ne change rien et affiche l'état du site.
# Le site publié est celui de main SUR GITHUB : pousser d'abord (git push) toute construction locale.
set -eu
. "$(dirname "$0")/commun.sh"

exiger_gh
exiger_verification
titre "Site visé : $ADRESSE_SITE"
depot_distant_existe || arreter "le dépôt $DEPOT_GH n'existe pas encore sur GitHub : lancer d'abord make depot."
gh api "repos/$DEPOT_GH/contents/docs/index.html?ref=main" --silent 2>/dev/null \
  || arreter "docs/index.html n'est pas sur la branche main de GitHub : make construire, git add/commit, git push, puis relancer."

# Écart entre le local et GitHub : avertir, sans bloquer.
git fetch --quiet origin main 2>/dev/null || true
if [ -n "$(git status --porcelain)" ] || [ "$(git rev-parse HEAD)" != "$(git rev-parse origin/main 2>/dev/null || echo aucun)" ]; then
  printf '\nATTENTION : des modifications locales ne sont pas sur GitHub ; le site publié sera la version de GitHub.\n'
  printf 'Pour publier la version locale : git -C "%s" add -A ; git commit ; git push.\n' "$RACINE"
fi

if SOURCE=$(gh api "repos/$DEPOT_GH/pages" --jq '"\(.source.branch) \(.source.path)"' 2>/dev/null); then
  if [ "$SOURCE" = "main /docs" ]; then
    printf '\nGitHub Pages est déjà réglé sur main /docs : rien à changer.\n'
    ACTION=aucune
  else
    ACTION=modifier
    confirmer "GitHub Pages est réglé sur « $SOURCE » ; le passer sur main /docs :" \
      "gh api -X PUT repos/$DEPOT_GH/pages  (source : branche main, dossier /docs)"
  fi
else
  ACTION=creer
  confirmer "Activer GitHub Pages pour $DEPOT_GH, servi depuis la branche main, dossier /docs :" \
    "gh api -X POST repos/$DEPOT_GH/pages  (source : branche main, dossier /docs)" \
    "Le site sera public à l'adresse $ADRESSE_SITE"
fi

CORPS='{"build_type":"legacy","source":{"branch":"main","path":"/docs"}}'
case "$ACTION" in
  creer)    printf '\n$ gh api -X POST repos/%s/pages --input -\n' "$DEPOT_GH"
            printf '%s' "$CORPS" | gh api -X POST "repos/$DEPOT_GH/pages" --input - >/dev/null ;;
  modifier) printf '\n$ gh api -X PUT repos/%s/pages --input -\n' "$DEPOT_GH"
            printf '%s' "$CORPS" | gh api -X PUT "repos/$DEPOT_GH/pages" --input - >/dev/null ;;
esac

titre "Vérification"
gh api "repos/$DEPOT_GH/pages" --jq '"adresse : \(.html_url)\nsource : \(.source.branch) \(.source.path)\nétat : \(.status // "en attente")"'
printf '\nAttente de la construction par GitHub (jusqu’à 5 minutes)…\n'
i=0
while [ $i -lt 20 ]; do
  ETAT=$(gh api "repos/$DEPOT_GH/pages/builds/latest" --jq .status 2>/dev/null || echo "inconnu")
  printf '  construction : %s\n' "$ETAT"
  case "$ETAT" in built|errored) break ;; esac
  i=$((i + 1)); sleep 15
done
CODE=$(curl -s -o /dev/null -w '%{http_code}' "$ADRESSE_SITE" || echo "000")
printf '\nRéponse de %s : HTTP %s (200 = en ligne ; 404 = attendre une minute et recharger).\n' "$ADRESSE_SITE" "$CODE"
