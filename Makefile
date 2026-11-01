# Commandes du dépôt. Détail de chaque commande : outils/README.md.
# Nom du dépôt et compte GitHub : outils/publication.conf (seul endroit où les écrire).
include outils/publication.conf

PYTHON ?= python3

.PHONY: aide construire verifier depot site version renommer

aide:
	@echo "Dépôt $(COMPTE_GITHUB)/$(NOM_DEPOT)"
	@echo "  make construire               refait chiffres, figures, papiers .docx, site (docs/), CITATION.cff, .zenodo.json"
	@echo "  make verifier                 contrôle de confidentialité et de cohérence (aucune action distante)"
	@echo "  make depot                    crée le dépôt public sur GitHub et y pousse la branche main"
	@echo "  make site                     publie le site avec GitHub Pages (main, dossier docs/)"
	@echo "  make version VERSION=v1.0.0   étiquette + version GitHub (archivée par Zenodo si activé)"
	@echo "  make renommer NOM=<nom>       change le nom du dépôt, avant sa création sur GitHub"

construire:
	$(PYTHON) outils/construire.py

verifier:
	$(PYTHON) outils/verifier_publication.py

depot:
	sh outils/creer_depot.sh

site:
	sh outils/publier_site.sh

version:
	@test -n "$(VERSION)" || { echo "usage : make version VERSION=v1.0.0"; exit 2; }
	sh outils/creer_version.sh $(VERSION)

renommer:
	@test -n "$(NOM)" || { echo "usage : make renommer NOM=<nouveau-nom>"; exit 2; }
	$(PYTHON) outils/renommer.py $(NOM)
