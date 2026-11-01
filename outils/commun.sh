# Fonctions communes aux scripts de publication (creer_depot.sh, publier_site.sh, creer_version.sh).
# Ce fichier est lu par « . outils/commun.sh » ; il ne s'exécute pas seul.

RACINE=$(cd "$(dirname "$0")/.." && pwd)
cd "$RACINE"
. "$RACINE/outils/publication.conf"
DEPOT_GH="$COMPTE_GITHUB/$NOM_DEPOT"
COMPTE_MIN=$(printf '%s' "$COMPTE_GITHUB" | tr '[:upper:]' '[:lower:]')
ADRESSE_DEPOT="https://github.com/$DEPOT_GH"
ADRESSE_SITE="https://$COMPTE_MIN.github.io/$NOM_DEPOT/"

titre() { printf '\n== %s ==\n' "$1"; }
arreter() { printf '\nARRÊT : %s\n' "$1" >&2; exit 1; }

exiger_gh() {
  command -v gh >/dev/null 2>&1 || arreter "gh (GitHub CLI) introuvable : brew install gh, puis gh auth login."
  gh auth status >/dev/null 2>&1 || arreter "gh n'est pas connecté : lancer gh auth login."
}

exiger_verification() {
  titre "Contrôle de publication (make verifier)"
  make --no-print-directory verifier || arreter "le contrôle de publication échoue : rien n'a été fait. Corriger, puis relancer."
}

depot_distant_existe() { gh repo view "$DEPOT_GH" >/dev/null 2>&1; }

# Affiche le plan (lignes passées en arguments) et demande « oui » ; toute autre réponse arrête sans rien faire.
confirmer() {
  titre "Ce qui va être fait"
  for ligne in "$@"; do printf '  %s\n' "$ligne"; done
  printf '\nTaper « oui » pour lancer, autre chose pour arrêter : '
  { read -r reponse </dev/tty; } 2>/dev/null || reponse=""
  [ "$reponse" = "oui" ] || arreter "annulé, rien n'a été fait."
}

# Lance une commande en l'affichant d'abord.
faire() { printf '\n$ %s\n' "$*"; "$@"; }
