"""Couple de pose selon la profondeur dans la bauge, sans et avec pré-trou, face aux limites de la vis : écrit figures/fig_pre_trou (français) et fig_pre_trou_en (anglais)."""

# Exécution, depuis la racine du dépôt : python3 vis-dans-la-bauge/code/figure_pre_trou.py   (« --langue fr|en » pour une seule)
# Deux campagnes, deux constats distincts :
# - sans pré-trou (combles, 10/10/2026) : la Ø10 bloque la visseuse à 18–20 N·m vers 10 cm de bauge (plafond vérifié
#   à la clé ; donnees/couple_pose.csv). Prolongement calculé : couple proportionnel à la profondeur (hypothèse).
# - avec pré-trou (cabanon, 30/10/2026) : presque tout posé à 20 N·m au plus (réglage 10 de la visseuse), jusqu'à
#   21,5 cm de bauge (Rémi, 01/11/2026) ; C7 finie au couple maximal à cause d'un caillou. Deux pré-trous différents
#   (donnees/essais.csv) : 6 mm sur presque toute la longueur (C1, C2, C7) ; 5 mm avec un foret de 80 mm, donc partiel
#   (C3, C4 ; C5 pour la Ø8). Aucun couple par cm n'est tiré des réglages notés ce jour-là.
# Limites : résistance à la torsion de la vis (ETA-21/0751) et limite de pose = résistance / 1,5.

import csv

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle

from lecture import DONNEES
from style import ENCRE, ENCRE_2, FOND, SERIES, enregistrer, langues, nombre, traducteur

PART_BOIS_COMBLES = 1.0   # N·m au plus, part de la planche dans les 18–20 N·m des combles (pré-percée, pré-vissée)
PLAFOND_AVEC_PRE_TROU = 20.0   # N·m : réglage 10 de la visseuse, plafond de presque toutes les poses du 30/10 (Rémi)
SANS, AVEC = SERIES[1], SERIES[0]
PRE_TROU_LONG, PRE_TROU_PARTIEL = ("C2", "C1"), ("C4", "C3")   # 6 mm sur la longueur ; 5 mm, foret de 80 mm


def lire(nom):
    with open(DONNEES / nom, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f, delimiter=";"))


def figure(lang):
    _ = traducteur(lang)
    poses = lire("couple_pose.csv")
    essais = {l["essai"]: l for l in lire("essais.csv")}
    vis10 = next(l for l in lire("vis.csv") if l["d_filet_mm"] == "10")
    lim, rup = float(vis10["limite_de_pose_Nm"]), float(vis10["resistance_torsion_Nm"])

    combles = next(l for l in poses if l["essai"] == "essai 01")
    z0 = float(combles["filet_dans_la_bauge_mm"]) / 10                                      # cm
    t_min, t_max = float(combles["couple_min_Nm"]), float(combles["couple_max_Nm"])
    pentes = ((t_min - PART_BOIS_COMBLES) / z0, t_max / z0)                                  # N·m par cm
    z = np.linspace(0, 30, 121)

    fig, ax = plt.subplots(figsize=(8.6, 6.4))
    # limites de la Ø10
    ax.axhline(lim, color=ENCRE_2, ls="--", lw=1.3)
    ax.axhline(rup, color=ENCRE_2, ls=":", lw=1.6)
    ax.text(30.3, lim, _("Ø10 : limite de pose\n", "Ø10: driving limit\n") + f"{nombre(lim, lang)} N·m", va="center",
            fontsize=8.3, color=ENCRE)
    ax.text(30.3, rup, _("Ø10 : la vis casse\n", "Ø10: the screw breaks\n") + f"{nombre(rup, lang)} N·m", va="center",
            fontsize=8.3, color=ENCRE)

    # 1. sans pré-trou : mesure des combles et prolongement calculé
    h_calc = ax.fill_between(z, pentes[0] * z, pentes[1] * z, color=SANS, alpha=0.20, lw=0,
                             label=_("Ø10 sans pré-trou : prolongement calculé (couple proportionnel à la profondeur)",
                                     "Ø10 without a pilot hole: calculated extension (torque proportional to depth)"))
    h_mes = ax.errorbar([z0], [(t_min + t_max) / 2], yerr=[[(t_max - t_min) / 2]], fmt="s", ms=8, color=SANS,
                        mec="white", ecolor=ENCRE, capsize=4, zorder=5,
                        label=_("Ø10 sans pré-trou, mesuré : la visseuse bloque (combles, 10/10)",
                                "Ø10 without a pilot hole, measured: the drill-driver stalls (attic, 10 Oct.)"))
    z_lim = (lim / pentes[1], lim / pentes[0])
    z_rup = (rup / pentes[1], rup / pentes[0])
    for (za, zb), y, txt in ((z_lim, lim, _("limite de pose", "driving limit")), (z_rup, rup, _("casse", "breaking"))):
        ax.plot([za, zb], [y, y], color=SANS, lw=4, solid_capstyle="butt", zorder=4)
        # libellé à gauche du trait, au-dessus de la ligne : la marge de droite porte les limites de la vis
        x, ha, va, dy = za - 0.6, "right", "bottom", 0.8
        ax.text(x, y + dy, _(f"sans pré-trou : {txt}\nvers {za:.0f}–{zb:.0f} cm (calculé)",
                             f"without a pilot hole: {txt}\nat about {za:.0f}–{zb:.0f} cm (calculated)"),
                ha=ha, va=va, fontsize=8.2, color=ENCRE, bbox=dict(fc=FOND, ec="none", alpha=0.85, pad=1))

    # 2. avec pré-trou : poses du cabanon, toutes sous 20 N·m (sauf C7)
    ax.add_patch(Rectangle((0, 0), 21.5, PLAFOND_AVEC_PRE_TROU, facecolor=AVEC, alpha=0.10, edgecolor="none",
                           zorder=1))
    ax.plot([0, 21.5], [PLAFOND_AVEC_PRE_TROU] * 2, color=AVEC, lw=1.4, zorder=3)
    poignees = []
    for noms, plein, lib in ((PRE_TROU_LONG, True,
                              _("Ø10, pré-trou de 6 mm sur presque toute la longueur (C1, C2) : posée à 20 N·m au plus "
                                "(cabanon, 30/10)",
                                "Ø10, 6 mm pilot hole over most of the length (C1, C2): driven at 20 N·m at most "
                                "(shed, 30 Oct.)")),
                             (PRE_TROU_PARTIEL, False,
                              _("Ø10, pré-trou partiel de 5 mm (C3, C4) : posée à 20 N·m au plus (cabanon, 30/10)",
                                "Ø10, partial 5 mm pilot hole (C3, C4): driven at 20 N·m at most (shed, 30 Oct.)"))):
        xs = [int(essais[n]["ancrage_bauge_mm"]) / 10 for n in noms]
        h, = ax.plot(xs, [PLAFOND_AVEC_PRE_TROU] * len(xs), "v", ms=9, mfc=AVEC if plein else "white", mec=AVEC,
                     mew=2, ls="none", zorder=5, label=lib)
        poignees.append(h)
        for n, x in zip(noms, xs):
            ax.text(x, PLAFOND_AVEC_PRE_TROU - 2.2, n, ha="center", va="top", fontsize=8, color=ENCRE_2)
    c5 = next(l for l in poses if l["essai"] == "C5")
    h_c5, = ax.plot([float(c5["filet_dans_la_bauge_mm"]) / 10], [float(c5["couple_min_Nm"])], "D", ms=7, mfc="white",
                    mec=SERIES[2], mew=2, ls="none", zorder=5,
                    label=_("Ø8, pré-trou partiel de 5 mm : débraye au réglage 4, ≈ 7 N·m (C5)",
                            "Ø8, partial 5 mm pilot hole: clutch slips at setting 4, ≈ 7 N·m (C5)"))
    ax.text(13.5, PLAFOND_AVEC_PRE_TROU / 2, _("avec pré-trou : presque tout posé\nà 20 N·m au plus (réglage 10)",
                                               "with a pilot hole: almost everything driven\nat 20 N·m at most "
                                               "(setting 10)"),
            ha="center", va="center", fontsize=8.5, color=ENCRE)
    zc7 = int(essais["C7"]["ancrage_bauge_mm"]) / 10
    ax.annotate("", xy=(zc7 + 0.5, 33), xytext=(zc7 + 0.5, PLAFOND_AVEC_PRE_TROU + 0.5),
                arrowprops=dict(arrowstyle="-|>", color=AVEC, lw=1.6))
    ax.text(zc7 + 1.0, 30.5, _("C7 : finie au couple\nmaximal (caillou)", "C7: finished at maximum\ntorque (stone)"),
            ha="left", va="center", fontsize=8.3, color=ENCRE)

    ax.set_xlim(0, 30)
    ax.set_ylim(0, 45)
    ax.set_xlabel(_("longueur de vis entrée dans la bauge (cm)", "length of screw driven into the cob (cm)"))
    ax.set_ylabel(_("couple de vissage (N·m)", "driving torque (N·m)"))
    handles = [h_mes, h_calc, *poignees, h_c5]
    ax.legend(handles, [h.get_label() for h in handles], loc="upper left", bbox_to_anchor=(0, -0.12), fontsize=8,
              frameon=False)
    ax.set_title(_("Couple de pose selon la profondeur, sans et avec pré-trou",
                   "Driving torque against depth, without and with a pilot hole"), loc="left")
    ax.text(0, -0.38, _("Deux campagnes sur deux murs. Sans pré-trou : un point mesuré, prolongé par le calcul. Avec "
                        "pré-trou : couple plafonné par le réglage de la visseuse.\nTirets : limite de pose (résistance à "
                        "la torsion / 1,5) ; pointillés : rupture en torsion (ETA-21/0751).",
                        "Two campaigns on two walls. Without a pilot hole: one measured point, extended by calculation. "
                        "With a pilot hole: torque capped by the drill-driver setting.\nDashes: driving limit (torsional "
                        "strength / 1.5); dots: torsional failure (ETA-21/0751)."),
            transform=ax.transAxes, fontsize=7.8, color=ENCRE_2, va="top")
    enregistrer(fig, "fig_pre_trou", lang)


if __name__ == "__main__":
    for langue in langues():
        figure(langue)
