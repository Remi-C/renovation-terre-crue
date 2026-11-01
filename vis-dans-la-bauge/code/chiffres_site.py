"""Chiffres clés de l'accueil du sujet sur le site, tirés de donnees/resultats_calcules.json et donnees/essais.csv."""

# Appelé par outils/construire.py (fonction tuiles) ; exécuté seul, affiche les tuiles : python3 vis-dans-la-bauge/code/chiffres_site.py

import csv
import json
import pathlib

RACINE = pathlib.Path(__file__).resolve().parent.parent


def tuiles(lang):
    """Liste de (valeur, sens) pour la langue « fr » ou « en »."""
    res = json.loads((RACINE / "donnees" / "resultats_calcules.json").read_text(encoding="utf-8"))["essais"]
    with open(RACINE / "donnees" / "essais.csv", newline="", encoding="utf-8") as f:
        meta = {l["essai"]: l for l in csv.DictReader(f, delimiter=";")}
    tenues = [n for n, g in res.items() if g["rupture"] is None and n != "C8" and meta[n]["d_mm"] == "10"]
    f_tenues = [res[n]["effort_max_kg"] for n in tenues]
    anc = [int(meta[n]["ancrage_bauge_mm"]) / 10 for n in tenues]
    ruptures = {n: g["rupture"]["effort_kg"] for n, g in res.items() if g["rupture"]}
    courtes = [n for n in ruptures if meta[n]["d_mm"] in ("8", "10")]
    inox = [n for n in ruptures if meta[n]["d_mm"] == "6"]
    v = lambda x: f"{x:g}".replace(".", "," if lang == "fr" else ".")  # noqa: E731
    cm = lambda n: v(int(meta[n]["ancrage_bauge_mm"]) / 10)  # noqa: E731
    et = " et " if lang == "fr" else " and "
    a = " à " if lang == "fr" else " at "
    desc_courtes = et.join(f"Ø{meta[n]['d_mm']}{a}{cm(n)} cm" for n in courtes)
    if lang == "fr":
        return [
            (f"{min(f_tenues):.0f}–{max(f_tenues):.0f} kg",
             f"Ø10 ancrées de {v(min(anc))} à {v(max(anc))} cm, planche serrée : aucune rupture, essais arrêtés avant"),
            (f"{min(ruptures[n] for n in courtes):.0f} kg", f"{desc_courtes} : rupture"),
            (f"{ruptures[inox[0]]:.0f} kg", f"vis inox Ø6 à {cm(inox[0])} cm : elle glisse"),
            (f"{len(res)} essais", "un mur, une journée (30/10/2026), matériel courant"),
        ]
    return [
        (f"{min(f_tenues):.0f}–{max(f_tenues):.0f} kg",
         f"Ø10 embedded {v(min(anc))} to {v(max(anc))} cm, clamping a board: no failure, tests stopped first"),
        (f"{min(ruptures[n] for n in courtes):.0f} kg", f"{desc_courtes}: failure"),
        (f"{ruptures[inox[0]]:.0f} kg", f"stainless Ø6 at {cm(inox[0])} cm: slips"),
        (f"{len(res)} tests", "one wall, one day (30 Oct. 2026), ordinary tools"),
    ]


if __name__ == "__main__":
    for lang in ("fr", "en"):
        for valeur, sens in tuiles(lang):
            print(f"{lang}  {valeur:>12}  {sens}")
