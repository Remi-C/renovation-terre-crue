"""Tenue mesurée d'une vis selon sa longueur dans la bauge, en traction et de côté, sous les longueurs de vis conseillées par les textes : écrit figures/fig_tenue_longueur (français) et fig_tenue_longueur_en (anglais)."""

# Exécution, depuis la racine du dépôt : python3 vis-dans-la-bauge/code/figure_tenue.py   (« --langue fr|en » pour une seule)
# Mesures. Traction : donnees/resultats_calcules.json, clé « arrachement » (code/grandeurs.py) — par essai et par
# longueur, la rupture, sinon la charge la plus haute tenue. De côté : donnees/essais.csv, essais de cisaillement où la
# vis plaque une planche (C8, corde sur la tête de vis, est exclu). Aucun modèle ni extrapolation.
# Les deux essais ont été faits séparément, dans deux montages : la figure les superpose, elle ne les combine pas.
# Longueurs conseillées (papier, « Ce que conseillent les textes », réf. 4, 5 et 25) : recopiées des documents.

import csv
import json

import matplotlib.pyplot as plt
from matplotlib.ticker import NullLocator

from lecture import DONNEES
from style import ENCRE_2, FOND, SERIES, enregistrer, langues, traducteur

TRACTION, COTE = SERIES[0], SERIES[1]
TEXTES = "#6b6a66"     # gris des longueurs conseillées
MARQUE = {10: "o", 8: "s", 6: "^"}
TAILLE = {10: 8, 8: 7, 6: 8}
# petits décalages horizontaux, seulement pour que deux points de même longueur ne se cachent pas
DECALAGE = {("C1", 21.5): -0.25, ("C7", 21.5): 0.25, ("A1", 10.5): -0.35, ("A2", 10.5): 0.3, ("A3", 10.5): 0.6,
            ("A6", 8.0): -0.2, ("A7", 8.0): 0.2}

# Longueurs conseillées (cm) : (début, fin ou None = « et plus », libellé fr, libellé en)
LONGUEURS = [
    (10, 15, "pisé, APTE : vis entrées de 10 à 15 cm", "rammed earth, APTE: screws driven in 10 to 15 cm"),
    (12.7, None, "bauge, M. G. Smith : vis de 12,7 cm et plus", "cob, M. G. Smith: screws of 12.7 cm or more"),
    (20, None, "bauge, guide CobBauge : vis de 20 cm et plus", "cob, CobBauge guide: screws of 20 cm or more"),
]


def mesures():
    """(sollicitation, diamètre, longueur cm, charge basse, charge haute, a cédé, essai)."""
    res = json.loads((DONNEES / "resultats_calcules.json").read_text(encoding="utf-8"))
    out = [("traction", p["d_mm"], p["bauge_mm"] / 10, p["F_bas_kg"], p["F_haut_kg"], p["cede"], p["essai"])
           for p in res["arrachement"]["paliers"]]
    with open(DONNEES / "essais.csv", newline="", encoding="utf-8") as f:
        for l in csv.DictReader(f, delimiter=";"):
            if l["sollicitation"] != "cisaillement" or l["essai"] == "C8":
                continue
            F = float(l["effort_max_kg"])
            cede = l["issue"].startswith(("rupture", "glisse"))
            out.append(("cote", int(l["d_mm"]), int(l["ancrage_bauge_mm"]) / 10, F, F, cede, l["essai"]))
    return out


def figure(lang):
    _ = traducteur(lang)
    fig, (haut, ax) = plt.subplots(2, 1, figsize=(8.6, 6.8), sharex=True,
                                   gridspec_kw=dict(height_ratios=[1, 3.6], hspace=0.06))
    x_max, y_max = 25, 460

    # bandeau du haut : longueurs conseillées
    for i, (L0, L1, fr, en) in enumerate(LONGUEURS):
        y = len(LONGUEURS) - i
        if L1 is None:
            haut.annotate("", xy=(x_max, y), xytext=(L0, y),
                          arrowprops=dict(arrowstyle="-|>", color=TEXTES, lw=2.2, mutation_scale=11))
        else:
            haut.plot([L0, L1], [y, y], color=TEXTES, lw=2.2, solid_capstyle="butt")
        haut.plot([L0], [y], "|", color=TEXTES, ms=9, mew=2.2)
        haut.text(L0 - 0.3, y, _(fr, en), ha="right", va="center", fontsize=8, color=ENCRE_2)
    haut.set_ylim(0.3, len(LONGUEURS) + 0.7)
    haut.yaxis.set_major_locator(NullLocator())
    for c in ("left", "right", "top"):
        haut.spines[c].set_visible(False)
    haut.set_ylabel(_("longueurs\nconseillées", "advised\nlengths"), fontsize=8, color=TEXTES)
    haut.set_title(_("Ce que tient une vis dans la bauge (mesuré), et les longueurs conseillées par les textes",
                     "How much a screw holds in cob (measured), and the lengths advised by published texts"),
                   loc="left", fontsize=10.5)

    # mesures
    for sol, d, L, Fb, Fh, cede, nom in mesures():
        c = TRACTION if sol == "traction" else COTE
        x, F = L + DECALAGE.get((nom, L), 0), (Fb + Fh) / 2
        if Fh > Fb:
            ax.plot([x, x], [Fb, Fh], color=c, lw=1.4, zorder=3)
        ax.plot([x], [F], MARQUE[d], ms=TAILLE[d], color=c, mfc=c if cede else FOND, mec=c, mew=1.6, ls="none",
                zorder=5)
        if not cede:
            ax.annotate("", xy=(x, F + 28), xytext=(x, F + 7),
                        arrowprops=dict(arrowstyle="-|>", color=c, lw=1.1, mutation_scale=9), zorder=4)

    ax.set_xlim(0, x_max)
    ax.set_ylim(0, y_max)
    ax.set_xlabel(_("longueur de vis dans la bauge (cm)", "length of screw in the cob (cm)"))
    ax.set_ylabel(_("charge (kg)", "load (kg)"))
    rond = dict(ls="none", marker="o", ms=8)
    h = [plt.Line2D([], [], color=TRACTION, label=_("en traction : vis tirée hors du mur (7/11/2026)",
                                                     "pulled out: screw pulled out of the wall (7 Nov. 2026)"), **rond),
         plt.Line2D([], [], color=COTE, label=_("de côté : vis qui plaque une planche (30/10/2026)",
                                                "sideways: screw clamping a board (30 Oct. 2026)"), **rond),
         plt.Line2D([], [], color=ENCRE_2, label=_("plein : la vis a cédé", "filled: the screw gave way"), **rond),
         plt.Line2D([], [], color=ENCRE_2, mfc=FOND, mew=1.6,
                    label=_("vide et flèche : a tenu, essai arrêté ; elle cède plus haut",
                            "open with arrow: held, test stopped; it gives way higher"), **rond),
         plt.Line2D([], [], ls="none", marker="o", ms=8, color=ENCRE_2, label="Ø10"),
         plt.Line2D([], [], ls="none", marker="s", ms=7, color=ENCRE_2, label="Ø8"),
         plt.Line2D([], [], ls="none", marker="^", ms=8, color=ENCRE_2, label="Ø6")]
    ax.legend(handles=h, loc="upper left", bbox_to_anchor=(0, -0.12), fontsize=8, ncol=2)
    ax.text(0, -0.34, _("Mesures : un seul mur, un essai par point ; les deux sollicitations essayées séparément.\n"
                        "Longueurs conseillées : pour la bauge, longueur de la vis (pièce fixée comprise) ; pour le "
                        "pisé, longueur entrée dans le mur.",
                        "Measured: a single wall, one test per point; the two loadings tested separately.\n"
                        "Advised lengths: for cob, length of the screw (fixed part included); for rammed earth, "
                        "length driven into the wall."),
            transform=ax.transAxes, fontsize=7.8, color=ENCRE_2, va="top")
    enregistrer(fig, "fig_tenue_longueur", lang)


if __name__ == "__main__":
    for langue in langues():
        figure(langue)
