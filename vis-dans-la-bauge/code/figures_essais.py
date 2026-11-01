"""Figures des mesures du 30/10/2026 : fig_efforts, fig_premiere_charge, fig_ressort_freine, en français et en anglais (lit donnees/resultats_calcules.json)."""

# Exécution, depuis la racine du dépôt : python3 vis-dans-la-bauge/code/grandeurs.py puis python3 vis-dans-la-bauge/code/figures_essais.py
# Produit figures/<id>.png/.svg (français) et figures/<id>_en.png/.svg (anglais) ; « --langue fr|en » pour une seule.

import csv
import json

import matplotlib.pyplot as plt
from matplotlib.patches import Patch

from lecture import DONNEES
from style import ENCRE, ENCRE_2, ENCRE_3, SERIES, enregistrer, langues, nombre, traducteur

RES = json.loads((DONNEES / "resultats_calcules.json").read_text(encoding="utf-8"))["essais"]
with open(DONNEES / "essais.csv", newline="", encoding="utf-8") as f:
    META = {l["essai"]: l for l in csv.DictReader(f, delimiter=";")}


def cm(mm, lang):
    return nombre(float(mm) / 10, lang) + " cm"


def etiquette(nom, lang, court=False):
    _ = traducteur(lang)
    m = META[nom]
    piece = _("sans planche", "no board") if nom == "C8" else (_("chêne", "oak") if "chêne" in m["piece_serree"]
                                                                 else _("douglas", "Douglas fir"))
    inox = _(" inox", " stainless") if "inox" in m["vis"] else ""
    if court:
        return f"{nom}  Ø{m['d_mm']}{inox}, {cm(m['ancrage_bauge_mm'], lang)}, {piece}"
    return (f"{nom}  Ø{m['d_mm']} × {m['longueur_mm']}{inox}, {cm(m['ancrage_bauge_mm'], lang)}"
            f"{_(' dans la bauge', ' into the cob')}, {piece}")


# ------------------------------------------------------------------------------------------------------- fig_efforts
def fig_efforts(lang):
    _ = traducteur(lang)
    ordre = sorted(RES, key=lambda n: (-float(META[n]["ancrage_bauge_mm"]), n))
    fig, ax = plt.subplots(figsize=(8.6, 4.2))
    for i, nom in enumerate(ordre):
        g = RES[nom]
        rupt = g["rupture"] is not None
        coul = SERIES[1] if rupt else SERIES[0]
        ax.barh(i, g["effort_max_kg"], height=0.56, color=coul, hatch="//" if nom == "C8" else None,
                edgecolor="white", linewidth=0)
        if rupt:
            ax.plot(g["effort_max_kg"], i, marker="X", ms=10, color=ENCRE, mec="white", mew=1.5, zorder=3)
            txt = f"{g['effort_max_kg']:.0f} kg" + _(" : rupture", ": failure")
        else:
            ax.annotate("", xy=(g["effort_max_kg"] + 38, i), xytext=(g["effort_max_kg"] + 4, i),
                        arrowprops=dict(arrowstyle="-|>", color=ENCRE_2, lw=1.4))
            txt = f"{g['effort_max_kg']:.0f} kg" + _(", pas de rupture : essai arrêté", ", no failure: test stopped")
        ax.text(g["effort_max_kg"] + 44 if not rupt else g["effort_max_kg"] + 12, i, txt, va="center",
                fontsize=9, color=ENCRE)
    ax.set_yticks(range(len(ordre)), [etiquette(n, lang) for n in ordre], fontsize=9)
    ax.invert_yaxis()
    ax.set_xlim(0, 640)
    ax.set_xlabel(_("effort de côté le plus haut atteint (kg, lu au peson)",
                    "highest sideways load reached (kg, read on the crane scale)"))
    ax.grid(axis="y", visible=False)
    ax.legend(handles=[Patch(color=SERIES[0], label=_("vis qui a tenu (l'effort réel de rupture est plus haut)",
                                                      "screw that held (the real failure load is higher)")),
                       Patch(color=SERIES[1], label=_("vis qui a cédé", "screw that gave way")),
                       Patch(facecolor=SERIES[0], hatch="//", edgecolor="white",
                             label=_("vis seule, sans planche", "screw alone, no board"))],
              loc="lower right", fontsize=8.5)
    ax.set_title(_("Effort maximal par essai, 30/10/2026", "Highest load per test, 30 Oct. 2026"), loc="left")
    enregistrer(fig, "fig_efforts", lang)


# ----------------------------------------------------------------------------------------------- fig_premiere_charge
def fig_premiere_charge(lang):
    _ = traducteur(lang)
    series = ["C2", "C3", "C4", "C7", "C5", "C6", "C8"]
    fig, ax = plt.subplots(figsize=(8.6, 5.0))
    for k, nom in enumerate(series):
        g = RES[nom]
        m = g["montees"][0]
        pts = [(0.0, m["origine_mm"])] + [(f, d) for f, d in m["points"]]
        # C7 : zéro non noté, la courbe part de la 1re lecture valable ; le palier 174 → 137 kg est montré à part.
        if m["statut"] == "zéro non noté":
            pts = pts[1:]
        if nom == "C7":
            pts = [p for p in pts if p[0] != 137.0]
        x, y = [p[1] for p in pts], [p[0] for p in pts]
        style = dict(ls="--", lw=1.6) if nom == "C8" else {}
        ax.plot(x, y, marker="o", ms=4.5, color=SERIES[k], label=etiquette(nom, lang, court=True)
                + (_(" (contexte)", " (context)") if nom == "C8" else ""), **style)
        if g["rupture"] and g["rupture"]["montee"] == 1:
            fr = g["rupture"]["effort_kg"]
            ax.plot([x[-1], x[-1]], [y[-1], fr], color=SERIES[k], lw=1.2, ls=":")
            ax.plot(x[-1], fr, marker="X", ms=9, color=ENCRE, mec="white", mew=1.2)
    ax.axhspan(0, 100, color="#f1efe9", zorder=0)
    ax.text(2.95, 55, _("sous 100 kg, les Ø10 de 5,5 à 26 cm\nlisent presque la même chose",
                        "below 100 kg, the Ø10 screws from 5.5 to 26 cm\nread almost the same"), ha="right",
            va="center", fontsize=8.5, color=ENCRE_2)
    ax.text(2.95, 140, _("✕ rupture ; pointillé : déplacement non lu\njusqu'à la rupture",
                         "✕ failure; dotted: movement not read\nup to failure"), ha="right", fontsize=8.5,
            color=ENCRE_2)
    ax.set_xlim(0, 3.0)
    ax.set_ylim(0, 360)
    ax.set_xlabel(_("déplacement lu au comparateur (mm)", "movement read on the dial gauge (mm)"))
    ax.set_ylabel(_("effort de côté (kg)", "sideways load (kg)"))
    ax.legend(loc="upper left", fontsize=8)
    ax.set_title(_("Première charge de chaque essai (C1 écarté : une manille frottait)",
                   "First loading of each test (C1 discarded: a shackle was rubbing)"), loc="left")
    enregistrer(fig, "fig_premiere_charge", lang)


# ------------------------------------------------------------------------------------------------ fig_ressort_freine
def fig_ressort_freine(lang):
    _ = traducteur(lang)
    fig, (a, b) = plt.subplots(2, 1, figsize=(8.6, 8.6), gridspec_kw={"height_ratios": [1.5, 1]})
    # (a) C7, tous les cycles
    decalage = 0.0
    for i, m in enumerate(RES["C7"]["montees"]):
        pts = [(d + decalage, f) for f, d in m["points"]]
        palier = [p for p in pts if p[1] == 137.0]
        pts = [p for p in pts if p[1] != 137.0]
        coul = SERIES[0] if i == 0 else SERIES[2]
        a.plot([p[0] for p in pts], [p[1] for p in pts], marker="o", ms=4, color=coul,
               label=_("1re charge", "first loading") if i == 0 else (_("rechargements", "reloadings") if i == 1
                                                                       else None))
        pic = pts[-1]
        if palier:
            a.annotate("", xy=(palier[0][0], 137), xytext=(pic[0], pic[1]),
                       arrowprops=dict(arrowstyle="-|>", color=ENCRE, lw=1.4))
            a.annotate(_("palier : 174 → 137 kg en 30 s,\ncomparateur immobile à 0,8 mm",
                         "step: 174 → 137 kg in 30 s,\ndial gauge still at 0.8 mm"), xy=(palier[0][0], 150),
                       xytext=(0.03, 285), fontsize=8.3, color=ENCRE,
                       arrowprops=dict(arrowstyle="-", color=ENCRE_3, lw=0.8))
        if m["residuel_mm"] is not None:
            fin = decalage + m["residuel_mm"]
            a.plot([pic[0], fin], [pic[1] if not palier else 137, 0], color=ENCRE_3, ls="--", lw=1.2,
                   label=_("décharge (seul le point d'arrivée est lu)", "unloading (only the end point is read)")
                   if i == 0 else None)
            decalage = fin
    a.set_xlim(0, 2.6)
    a.set_ylim(0, 330)
    a.set_xlabel(_("déplacement cumulé (mm)", "cumulative movement (mm)"))
    a.set_ylabel(_("effort de côté (kg)", "sideways load (kg)"))
    a.set_title(_("C7 : Ø10 × 260, 21,5 cm, planche de douglas", "C7: Ø10 × 260, 21.5 cm, Douglas fir board"),
                loc="left")
    a.legend(loc="lower right", fontsize=8)
    a.text(0.0, -0.16, _("Après chaque remise à zéro, la courbe repart du déplacement lu à la décharge précédente.",
                         "After each reset of the dial gauge, the curve restarts from the movement read at the "
                         "previous unloading."),
           transform=a.transAxes, fontsize=7.8, color=ENCRE_2)
    # (b) part du déplacement rendue à la décharge complète
    lignes = [("C2", False, _("1re charge, 315 kg", "first loading, 315 kg")),
              ("C7", False, _("1re charge, 174 kg", "first loading, 174 kg")),
              ("C7", True, _("rechargement, 300 kg", "reloading, 300 kg")),
              ("C8", False, _("1re charge, 300 kg (contexte)", "first loading, 300 kg (context)")),
              ("C6", False, _("1re charge, 50 kg (inox)", "first loading, 50 kg (stainless)"))]
    vals = []
    for nom, recharge, lib in lignes:
        g = RES[nom]
        if recharge:
            v = next(r["part_rendue_a_la_decharge"] for r in g["rechargements"] if r.get("part_rendue_a_la_decharge"))
        else:
            v = g["premiere_charge"]["part_rendue_a_la_decharge"]
        vals.append((f"{nom}, {lib}", v))
    y = range(len(vals))
    b.barh(list(y), [v * 100 for _l, v in vals], height=0.55, color=SERIES[0])
    for i, (_l, v) in enumerate(vals):
        b.text(v * 100 + 2, i, f"{v * 100:.0f}" + _(" %", "%"), va="center", fontsize=9, color=ENCRE)
    b.set_yticks(list(y), [l for l, _v in vals], fontsize=8.5)
    b.invert_yaxis()
    b.set_xlim(0, 115)
    b.set_xticks([0, 25, 50, 75, 100])
    b.set_xlabel(_("part du déplacement rendue en déchargeant à 0 kg (%)",
                   "share of the movement given back when unloading to 0 kg (%)"))
    b.grid(axis="y", visible=False)
    b.set_title(_("Déchargé à zéro, il revient presque", "Unloaded to zero, it almost comes back"), loc="left")
    # Retour qu'aurait donné un ressort sans frottement à la baisse du palier de C7 (174 → 137 kg), calculé avec la
    # raideur moyenne de décharge de l'assemblage (resultats_calcules.json) ; le chiffre de raideur n'est pas affiché :
    # c'est celui de tout le montage, pas de la bauge.
    k = RES["C7"]["premiere_charge"]["raideur_moyenne_de_decharge_assemblage_kg_par_mm"]
    retour = nombre((174 - 137) / k, lang, ".2f")
    b.text(0.0, -0.32, _(f"Au palier de C7, un ressort qui rendrait le déplacement en proportion de l'effort aurait "
                         f"rendu {retour} mm ; lu : 0.",
                         f"At the C7 step, a spring giving back movement in proportion to the load would have given "
                         f"back {retour} mm; read: 0."),
           transform=b.transAxes, fontsize=7.8, color=ENCRE_2)
    fig.suptitle(_("Un ressort freiné : il revient quand on décharge tout, pas quand l'effort baisse un peu",
                   "A braked spring: it comes back when fully unloaded, not when the load drops a little"),
                 x=0.01, ha="left", fontsize=11.5, fontweight="bold", color=ENCRE)
    fig.tight_layout()
    enregistrer(fig, "fig_ressort_freine", lang)


if __name__ == "__main__":
    for langue in langues():
        fig_efforts(langue)
        fig_premiere_charge(langue)
        fig_ressort_freine(langue)
