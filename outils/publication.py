"""Nom du dépôt, adresses du dépôt et du site, liste des sujets : lus une fois, partagés par les outils."""

# Le nom du dépôt et le compte GitHub sont écrits dans outils/publication.conf, et nulle part ailleurs à la main.
# Un sujet est un dossier de la racine qui contient un fichier sujet.toml (voir vis-dans-la-bauge/sujet.toml).

import pathlib
import tomllib

RACINE = pathlib.Path(__file__).resolve().parent.parent
CONF = RACINE / "outils" / "publication.conf"


def lire_conf(chemin=CONF):
    valeurs = {}
    for ligne in chemin.read_text(encoding="utf-8").splitlines():
        ligne = ligne.strip()
        if ligne and not ligne.startswith("#") and "=" in ligne:
            cle, val = ligne.split("=", 1)
            valeurs[cle.strip()] = val.strip()
    return valeurs


_conf = lire_conf()
COMPTE = _conf["COMPTE_GITHUB"]
NOM = _conf["NOM_DEPOT"]
DEPOT = f"https://github.com/{COMPTE}/{NOM}"
DOMAINE = _conf.get("DOMAINE_PAGES", "").strip() or f"{COMPTE.lower()}.github.io"
SITE = f"https://{DOMAINE}/{NOM}/"


def sujets():
    """Les sujets, dans l'ordre de leur clé « ordre » : liste de (dossier, description lue dans sujet.toml)."""
    trouves = []
    for f in sorted(RACINE.glob("*/sujet.toml")):
        with open(f, "rb") as fh:
            d = tomllib.load(fh)
        d["id"] = f.parent.name
        trouves.append((f.parent, d))
    return sorted(trouves, key=lambda x: (x[1].get("ordre", 99), x[1]["id"]))
