"""Effort de côté selon la longueur de vis dans la bauge, mesures et extrapolation : écrit figures/fig_profondeur (français) et fig_profondeur_en (anglais)."""

# Exécution, depuis la racine du dépôt : python3 vis-dans-la-bauge/code/figure_profondeur.py   (« --langue fr|en » pour une seule)
# Points : donnees/essais.csv (vis plaquant une planche ; C8, corde sur la tête de vis, est exclu). Rupture = point
# plein ; tenue sans rupture (essai arrêté) = triangle vide : la résistance est au-dessus. Ø6 : tient 40 kg, glisse à
# 50 kg (donnees/releves_cisaillement_2026_10_30.csv).
# Extrapolation (hypothèse, non mesurée) : la bauge porte la vis sur sa longueur, donc effort ∝ longueur, droite issue
# de zéro et passant par la rupture de chaque diamètre (Ø10 : C4 ; Ø8 : C5), arrêtée à 350 kg : au-delà, jamais mesuré.

import csv

import matplotlib.pyplot as plt
import numpy as np

from lecture import DONNEES
from style import ENCRE, ENCRE_2, ENCRE_3, FOND, SERIES, enregistrer, langues, nombre, traducteur

COULEUR = {"10": SERIES[0], "8": SERIES[1], "6": SERIES[2]}
MARQUE = {"10": "o", "8": "D", "6": "s"}
PLUS_HAUT_MESURE = 350   # kg : effort le plus haut jamais appliqué (C2)
TIENT_O6 = 40            # kg : dernier palier tenu par la Ø6 avant de glisser à 50 kg


def a_lache(l):
    """La vis a cédé (rupture ou glissement) ; « aucune rupture (essai arrêté) » veut dire qu'elle a tenu."""
    return l["issue"].startswith(("rupture", "glisse"))


def lire_essais():
    with open(DONNEES / "essais.csv", newline="", encoding="utf-8") as f:
        return [l for l in csv.DictReader(f, delimiter=";") if l["essai"] != "C8"]


def figure(lang):
    _ = traducteur(lang)
    essais = lire_essais()
    fig, ax = plt.subplots(figsize=(8.6, 6.0))
    x_max, y_max = 24, 450

    # zone jamais mesurée
    ax.axhspan(PLUS_HAUT_MESURE, y_max, color=ENCRE_3, alpha=0.10, lw=0)
    ax.text(0.4, (PLUS_HAUT_MESURE + y_max) / 2,
            _(f"au-delà de {PLUS_HAUT_MESURE} kg : jamais mesuré (essais arrêtés avant rupture)",
              f"above {PLUS_HAUT_MESURE} kg: never measured (tests stopped before failure)"),
            va="center", fontsize=8.5, color=ENCRE_2)

    # extrapolation : droite par zéro et par la rupture de chaque diamètre
    z = np.linspace(0, x_max, 200)
    for d in ("10", "8"):
        r = next(l for l in essais if l["d_mm"] == d and a_lache(l))
        pente = float(r["effort_max_kg"]) / (int(r["ancrage_bauge_mm"]) / 10)
        zz = z[pente * z <= PLUS_HAUT_MESURE]   # la droite s'arrête où s'arrêtent les mesures
        ax.plot(zz, pente * zz, ls="--", lw=1.6, color=COULEUR[d], alpha=0.8,
                label=_(f"Ø{d} extrapolé : ≈ {pente:.0f} kg par cm de vis (non mesuré)",
                        f"Ø{d} extrapolated: ≈ {pente:.0f} kg per cm of screw (not measured)"))

    # mesures
    vus, etiquetes = set(), set()
    for l in essais:
        d, x, f = l["d_mm"], int(l["ancrage_bauge_mm"]) / 10, float(l["effort_max_kg"])
        rompu = a_lache(l)
        if d == "6":
            f = TIENT_O6
        lib = None
        if (d, rompu) not in vus:
            vus.add((d, rompu))
            lib = (_(f"Ø{d} : effort maximal (rupture)", f"Ø{d}: highest load (failure)") if rompu and d != "6" else
                   _(f"Ø{d} : tient {TIENT_O6} kg, glisse à 50 kg", f"Ø{d}: holds {TIENT_O6} kg, slips at 50 kg")
                   if d == "6" else _(f"Ø{d} : a tenu, essai arrêté (résistance au-dessus)",
                                      f"Ø{d}: held, test stopped (strength is higher)"))
        if rompu or d == "6":
            ax.plot([x], [f], MARQUE[d], ms=9, color=COULEUR[d], mec="white", mew=1.2, ls="none", zorder=5, label=lib)
        else:
            ax.plot([x], [f], "^", ms=10, mfc="white", mec=COULEUR[d], mew=2, ls="none", zorder=5, label=lib)
            ax.annotate("", xy=(x, f + 32), xytext=(x, f + 6),
                        arrowprops=dict(arrowstyle="-|>", color=COULEUR[d], lw=1.4), zorder=4)
        if (x, f) in etiquetes:
            continue
        etiquetes.add((x, f))
        n = sum(1 for m in essais if int(m["ancrage_bauge_mm"]) / 10 == x and float(m["effort_max_kg"]) == f)
        gauche = l["essai"] == "C4"
        ax.text(x - 0.35 if gauche else x + 0.35, f - 12, f"{nombre(x, lang)} cm · {f:.0f} kg" + (f" (×{n})" if n > 1 else ""),
                fontsize=7.8, color=ENCRE_2, va="top", ha="right" if gauche else "left",
                bbox=dict(fc=FOND, ec="none", alpha=0.85, pad=1), zorder=6)

    ax.set_xlim(0, x_max)
    ax.set_ylim(0, y_max)
    ax.set_xlabel(_("longueur de vis dans la bauge (cm)", "length of screw in the cob (cm)"))
    ax.set_ylabel(_("effort de côté (kg)", "sideways load (kg)"))
    ax.set_title(_("Effort de côté selon la longueur de vis dans la bauge (vis plaquant un montant en bois)",
                   "Sideways load against length of screw in the cob (screw clamping a timber batten)"),
                 loc="left", fontsize=10.5)
    ax.legend(loc="upper left", bbox_to_anchor=(0, -0.11), fontsize=8.2, ncol=2)
    ax.text(0, -0.30, _("Points : mesures du 30/10/2026, un mur. Tirets : extrapolation, effort supposé proportionnel à "
                        "la longueur ; non mesurée.",
                        "Points: measured on 30 Oct. 2026, one wall. Dashes: extrapolation, load assumed proportional "
                        "to length; not measured."),
            transform=ax.transAxes, fontsize=7.8, color=ENCRE_2, va="top")
    enregistrer(fig, "fig_profondeur", lang)


if __name__ == "__main__":
    for langue in langues():
        figure(langue)
