"""Module partagé : chemins du sujet, lecture des pesées, des prélèvements, des étapes et des isothermes publiées."""

import csv
import statistics
from pathlib import Path

SUJET = Path(__file__).resolve().parent.parent
DONNEES = SUJET / "donnees"
FIGURES = SUJET / "figures"

POTS = ["F1", "F2", "F3", "F4", "C1", "C2", "A1", "A2"]   # les huit pots de terre ; T est le témoin (pot vide)
FACADE = ["F1", "F2", "F3", "F4"]
SEC, TARE, TEL_QUEL = "E1", "E5", "E0"        # séries qui servent à la teneur en eau (voir le papier, 2.1)
SERIES_SECHES = ["E1", "E3", "E5"]            # séries de pots chauds et secs, pour la dérive du témoin


def _csv(nom):
    with open(DONNEES / nom, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f, delimiter=";"))


def lire_pesees():
    """{(échantillon, étape): {"lectures": [g], "moy": g ou None, "rang": int ou None, "remarques": str}}."""
    d = {}
    for r in _csv("pesees.csv"):
        lect = [float(x) for x in r["lectures_g"].split()]
        d[(r["echantillon"], r["etape"])] = {
            "lectures": lect, "moy": statistics.fmean(lect) if lect else None,
            "rang": int(r["rang_pesee"]) if r["rang_pesee"] else None, "remarques": r["remarques"]}
    return d


def lire_prelevements():
    """{échantillon: {"mur", "profondeur_cm", "lieu", "outil"}}."""
    return {r["echantillon"]: r for r in _csv("prelevements.csv")}


def lire_etapes():
    return _csv("etapes.csv")


def milieu(profondeur):
    """Milieu d'une tranche « a-b » (cm)."""
    a, b = (float(x) for x in profondeur.split("-"))
    return (a + b) / 2


def lire_isothermes():
    """{sol: {"desorption": [(HR %, w %)], "retention": [...], "sorption": [...]}}, chaque liste triée par HR croissante."""
    iso = {}
    for r in _csv("isotherme_phung_2018.csv"):
        iso.setdefault(r["sol"], {}).setdefault(r["serie"], []).append((float(r["hr_pct"]), float(r["w_pct"])))
    for sol in iso.values():
        for k in sol:
            sol[k].sort()
    return iso


def courbe_sechage(iso_sol):
    """Courbe d'équilibre d'un sol en séchage : désorption de 5 à 90 % d'humidité relative, puis courbe de rétention de
    93 % à la saturation. Les deux séries viennent d'éprouvettes différentes : le raccord de 90 à 93 % est le point faible."""
    bas = [p for p in iso_sol["desorption"] if p[0] <= 90]
    haut = [p for p in iso_sol["retention"] if p[0] >= 93]
    return bas + haut


def hr_depuis_w(w, courbe):
    """Humidité relative d'équilibre (%) d'une teneur en eau w (%), par interpolation linéaire sur la courbe ;
    None hors de la courbe (en dessous de son premier point ou au-dessus du dernier)."""
    if w < courbe[0][1] or w > courbe[-1][1]:
        return None
    for (h0, w0), (h1, w1) in zip(courbe, courbe[1:]):
        if w0 <= w <= w1:
            return h0 + (h1 - h0) * (w - w0) / (w1 - w0)
    return None
