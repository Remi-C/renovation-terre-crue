"""Lecture des relevés de cisaillement du 30/10/2026 et découpage en montées de charge (module partagé par code/)."""

# Utilisé par les autres scripts de code/ ; ne s'exécute pas seul.
# Chemins relatifs au dossier du sujet (parent de code/), quel que soit le dossier courant ; les scripts se lancent par « python3 vis-dans-la-bauge/code/<script>.py » depuis la racine.

import csv
import pathlib

RACINE = pathlib.Path(__file__).resolve().parent.parent
DONNEES = RACINE / "donnees"
FIGURES = RACINE / "figures"
RELEVES = DONNEES / "releves_cisaillement_2026_10_30.csv"

# Statut des données décidé par l'auteur le 31/10/2026 (voir donnees/README.md) :
# C1 : 1re charge et 2e cycle écartés (une manille frottait sur la platine jusqu'au « tour sup sur manille ») ;
# C8 : déplacements donnés pour contexte seulement (touche sur une tête de vis très petite, trou déjà déformé par C1).
MONTEES_ECARTEES = {"C1": {1, 2}}
DEPLACEMENTS_CONTEXTE = {"C8"}
MOTS_RUINE = ("arrach", "coulisse", "glisse")


def nombre(txt):
    txt = (txt or "").strip().replace(",", ".")
    return float(txt) if txt else None


def lire_releves(chemin=RELEVES):
    """Relevés ligne à ligne, groupés par essai, dans l'ordre de la fiche."""
    essais = {}
    with open(chemin, newline="", encoding="utf-8") as f:
        for l in csv.DictReader(f, delimiter=";"):
            essais.setdefault(l["essai"], []).append({
                "rang": int(l["rang"]), "F": nombre(l["F_kg"]), "d": nombre(l["delta_mm"]),
                "obs": (l["observation"] or "").strip(), "vis": l["vis"], "eprouvette": l["eprouvette"],
            })
    return essais


def montees(lignes):
    """Découpe un essai en montées de charge, chacune lue depuis une origine connue.

    Règles, reprises de la fiche telle qu'elle a été remplie :
    - une ligne « Mauvaise mesure » est écartée ;
    - une ligne à 0 kg clôt la montée en cours ; si le comparateur y est lu, c'est le déplacement résiduel ;
    - la montée suivante part de 0 si la fiche note « RAZ » (remise à zéro du comparateur) ou si la lecture à 0 kg est
      écrite 0 ; elle part du résiduel si aucune remise à zéro n'est notée et que la lecture suivante est plus grande ;
    - sinon, l'origine n'est pas notée : la montée est lue depuis 0 et marquée comme telle.
    """
    groupes = []
    cour = {"origine": 0.0, "statut": "zéro du protocole", "points": [], "evenements": [], "residuel": None}
    for i, l in enumerate(lignes):
        if "Mauvaise mesure" in l["obs"]:
            continue
        if l["F"] == 0:
            if cour["points"]:
                cour["residuel"] = l["d"]
                groupes.append(cour)
            suivante = next((x for x in lignes[i + 1:] if x["F"] and x["d"] is not None), None)
            if "RAZ" in l["obs"] or l["d"] == 0:
                cour = {"origine": 0.0, "statut": "remise à zéro notée"}
            elif l["d"] is not None and suivante and suivante["d"] >= l["d"]:
                cour = {"origine": l["d"], "statut": "suite sans remise à zéro"}
            elif not cour["points"] and not groupes:
                cour = {"origine": 0.0, "statut": "zéro non noté"}
            else:
                cour = {"origine": 0.0, "statut": "origine non notée"}
            cour.update(points=[], evenements=[], residuel=None)
            continue
        if l["F"] is not None and l["d"] is not None:
            cour["points"].append((l["F"], l["d"]))
        elif l["F"] is not None:
            cour["evenements"].append((l["F"], l["obs"]))
    if cour["points"] or cour["evenements"]:
        groupes.append(cour)
    for n, g in enumerate(groupes, start=1):
        g["n"] = n
    return groupes


def interp(points, origine, f):
    """Déplacement à l'effort f sur une montée (droite entre deux lectures), depuis 0 kg ; None si f n'est pas atteint."""
    fs = [0.0] + [p[0] for p in points]
    ds = [origine] + [p[1] for p in points]
    for (f0, d0), (f1, d1) in zip(zip(fs, ds), zip(fs[1:], ds[1:])):
        if f1 > f0 and f0 <= f <= f1:
            return d0 + (d1 - d0) * (f - f0) / (f1 - f0)
    return None


def essais_decoupes():
    """Pour chaque essai : ses montées, avec la mention « écartée » quand le statut des données l'exige."""
    sortie = {}
    for nom, lignes in lire_releves().items():
        ms = montees(lignes)
        for m in ms:
            m["ecartee"] = m["n"] in MONTEES_ECARTEES.get(nom, set())
        sortie[nom] = {"lignes": lignes, "montees": ms}
    return sortie
