"""Figures du sujet « Humidité de la bauge » : fig_protocole, fig_ecarts, fig_bruit, fig_profils, fig_isotherme (FR et EN)."""

# Depuis la racine du dépôt : python3 humidite-de-la-bauge/code/figures_humidite.py [--langue fr|en]
# Lit donnees/*.csv et donnees/resultats_calcules.json (produit par grandeurs.py, à lancer avant).

import json
import math

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

from lecture import DONNEES, POTS, courbe_sechage, lire_etapes, lire_isothermes, lire_pesees, lire_prelevements, milieu
from style import COUL, ENCRE, ENCRE_2, ENCRE_3, GRILLE, enregistrer, langues, nombre, traducteur

SOLS = {"A": "#6250d6", "B": "#eda100"}   # les deux sols publiés de la thèse citée (pas ceux du mur)


def resultats():
    return json.loads((DONNEES / "resultats_calcules.json").read_text(encoding="utf-8"))


def noms_murs(_):
    return {"F": _("Façade sud (0-20 cm)", "South façade (0-20 cm)"), "C": _("Combles (0-13 cm)", "Attic (0-13 cm)"),
            "A": _("Cabanon (0-20 cm)", "Garden shed (0-20 cm)")}


def fig_protocole(lang):
    """Frise des six pesées : état thermique du pot, passages au four, ordre de pesée des deux séries chaudes."""
    _ = traducteur(lang)
    ordre = {e["etape"]: e["ordre_de_pesee"] for e in lire_etapes() if e["ordre_de_pesee"]}
    fig, ax = plt.subplots(figsize=(10, 3.4))
    ax.grid(False)
    etapes = [("E0", _("tel quel", "as sampled"), "froid"), ("E1", _("sortie de four\n1er séchage", "out of the oven\n1st drying"), "chaud"),
              ("E2", _("30 min après", "30 min later"), "tiède"), ("E3", _("sortie de four\n2e séchage", "out of the oven\n2nd drying"), "chaud"),
              ("E4", _("pot vide lavé,\nessuyé", "empty pot washed,\nwiped"), "froid"), ("E5", _("pot vide lavé,\nséché au four", "empty pot washed,\noven-dried"), "chaud")]
    mot = {"froid": _("pot froid", "cold pot"), "tiède": _("pot tiède", "warm pot"), "chaud": _("pot chaud", "hot pot")}
    fond = {"froid": "#dfe9f5", "tiède": "#f3e6d6", "chaud": "#f6cdb4"}
    entre = {0: _("four 1 h\n130 °C", "oven 1 h\n130 °C"), 2: _("four", "oven"), 3: _("vider,\nrincer", "empty,\nrinse"), 4: _("four", "oven")}
    pas, larg = 1.7, 1.15
    for i, (code, lib, th) in enumerate(etapes):
        x = i * pas
        ax.add_patch(FancyBboxPatch((x, 0.45), larg, 0.9, boxstyle="round,pad=0.02,rounding_size=0.08", fc=fond[th], ec=ENCRE_3, lw=0.8))
        ax.text(x + larg / 2, 1.13, code, ha="center", va="center", fontsize=11, weight="bold", color=ENCRE)
        ax.text(x + larg / 2, 0.75, lib, ha="center", va="center", fontsize=7.5, color=ENCRE)
        ax.text(x + larg / 2, 0.33, mot[th], ha="center", va="top", fontsize=7, color=ENCRE_3)
        if i < len(etapes) - 1:
            xa, xb = x + larg + 0.03, x + pas - 0.03
            ax.annotate("", (xb, 0.9), (xa, 0.9), arrowprops={"arrowstyle": "-|>", "color": ENCRE_3, "lw": 1})
            if i in entre:
                ax.text((xa + xb) / 2, 1.0, entre[i], ha="center", va="bottom", fontsize=6.5, color=ENCRE_3)
    ax.text(1 * pas + larg / 2, -0.05, _("ordre : ", "order: ") + ordre["E1"] + _("\n11h50 → 12h20 (série lente)", "\n11:50 → 12:20 (slow series)"),
            ha="center", va="top", fontsize=7, color=ENCRE)
    ax.text(3 * pas + larg / 2, -0.05, _("ordre : ", "order: ") + ordre["E3"] + _("\n(série rapide, fond des pots\nrefroidi à l'éponge humide)", "\n(fast series, pot bottoms\ncooled with a damp sponge)"),
            ha="center", va="top", fontsize=7, color=ENCRE)
    ax.text(5 * pas + larg / 2, -0.05, _("sur un intercalaire\nd'environ 5 g taré", "on a spacer of about\n5 g, tared"), ha="center", va="top", fontsize=7, color=ENCRE)
    ax.set_xlim(-0.1, 5 * pas + larg + 0.1)
    ax.set_ylim(-0.75, 1.55)
    ax.axis("off")
    enregistrer(fig, "fig_protocole", lang)


def fig_ecarts(lang):
    """Écarts de masse bruts entre pesées successives, par pot : aucune convention, seulement des différences lues."""
    _ = traducteur(lang)
    d = lire_pesees()
    noms = POTS + ["T"]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(10, 3.8), gridspec_kw={"width_ratios": [1, 1.5]})
    x = list(range(len(noms)))
    perte = [d[(n, "E1")]["moy"] - d[(n, "E0")]["moy"] for n in noms]
    a1.bar(x, perte, color=[COUL[n[0]] for n in noms], width=0.62)
    a1.axhline(0, color=ENCRE_3, lw=0.8)
    a1.set_title(_("E1 − E0 : masse perdue au premier séchage", "E1 − E0: mass lost in the first drying"), loc="left", fontsize=9)
    a1.set_ylabel("g")
    for i, p in enumerate(perte):
        a1.text(i, p - 0.03, nombre(p, lang, ".2f"), ha="center", va="top", fontsize=6.5, color=ENCRE)
    a1.set_ylim(min(perte) - 0.2, 0.15)
    w = 0.36
    nan = float("nan")
    e21 = [d[(n, "E2")]["moy"] - d[(n, "E1")]["moy"] if d[(n, "E2")]["moy"] is not None else nan for n in noms]
    e32 = [d[(n, "E3")]["moy"] - d[(n, "E2")]["moy"] if d[(n, "E2")]["moy"] is not None else nan for n in noms]
    a2.bar([i - w / 2 for i in x], e21, width=w, color="#4a4a4a", label=_("E2 − E1 : 30 min de refroidissement à l'air", "E2 − E1: 30 min cooling in air"))
    a2.bar([i + w / 2 for i in x], e32, width=w, color="#b8b8b2", label=_("E3 − E2 : après le reséchage", "E3 − E2: after the second drying"))
    a2.axhline(0, color=ENCRE_3, lw=0.8)
    a2.text(len(noms) - 1, 0.004, _("T : pas de\npesée en E2", "T: not weighed\nin E2"), ha="center", va="bottom", fontsize=6.5, color=ENCRE_3)
    a2.set_title(_("Écarts entre les pesées suivantes", "Differences between the following weighings"), loc="left", fontsize=9)
    a2.legend(loc="lower left", fontsize=7)
    a2.set_ylim(-0.12, 0.12)
    for a in (a1, a2):
        a.set_xticks(x)
        a.set_xticklabels(noms)
        a.set_axisbelow(True)
    fig.tight_layout()
    enregistrer(fig, "fig_ecarts", lang)


def fig_bruit(lang):
    """Incertitude de la teneur en eau due aux seules pesées, selon la masse de terre sèche du pot."""
    _ = traducteur(lang)
    R = resultats()
    sigma = R["bruit"]["par_pesee_sigma_g"]
    fig, ax = plt.subplots(figsize=(8.5, 3.9))
    ms = [0.3 * 1.05 ** k for k in range(120)]
    ax.plot(ms, [math.sqrt(2 * sigma ** 2 * (1 + 0.05 ** 2)) / m * 100 for m in ms], color=ENCRE, lw=1.5)
    for p in POTS:
        r = R["pots"][p]
        ax.plot(r["terre_seche_g"], r["incertitude_pct"], "o", ms=8, color=COUL[p[0]], mec="white", mew=1.5, zorder=3)
        ax.text(r["terre_seche_g"] * 1.07, r["incertitude_pct"] * 1.06, p, fontsize=7.5, color=ENCRE)
    ax.axhline(0.5, color=ENCRE_3, lw=0.8, ls=(0, (3, 3)))
    ax.axvline(10, color=ENCRE_3, lw=0.8, ls=(0, (1, 2)))
    ax.text(10.6, 9, _("10 g de terre sèche", "10 g of dry earth"), fontsize=7.5, color=ENCRE_3)
    ax.text(0.32, 0.55, _("± 0,5 point", "± 0.5 point"), fontsize=7.5, color=ENCRE_3, va="bottom")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(0.3, 40)
    ax.set_ylim(0.1, 15)
    ax.set_xticks([0.5, 1, 2, 5, 10, 20])
    ax.set_xticklabels([nombre(v, lang, "g") for v in (0.5, 1, 2, 5, 10, 20)])
    ax.set_yticks([0.2, 0.5, 1, 2, 5, 10])
    ax.set_yticklabels([nombre(v, lang, "g") for v in (0.2, 0.5, 1, 2, 5, 10)])
    ax.set_xlabel(_("terre sèche dans le pot (g)", "dry earth in the pot (g)"))
    ax.set_ylabel(_("± 1 écart-type sur la teneur en eau\n(points de %)", "± 1 standard deviation on water content\n(percentage points)"))
    enregistrer(fig, "fig_bruit", lang)


def fig_profils(lang):
    """Teneur en eau par tranche et par mur, repères de la littérature ; aucune conversion en humidité relative ici."""
    _ = traducteur(lang)
    R = resultats()
    pre = lire_prelevements()
    murs = noms_murs(_)
    fig, ax = plt.subplots(figsize=(8.5, 5.2))
    ax.axvspan(1, 3, color="#000000", alpha=0.05, lw=0)
    ax.axvspan(3, 5, color="#000000", alpha=0.10, lw=0)
    ax.axvline(7.5, color=ENCRE_3, lw=0.8, ls=(0, (3, 3)))
    for x, t in ((2.0, _("pisé sain\nen service\n1-3 %", "healthy rammed\nearth in use\n1-3 %")),
                 (4.0, _("pied de mur de\nbauge « normal »\n3-5 % (BRE)", "cob wall base\n“quite normal”\n3-5 % (BRE)")),
                 (8.8, _("au-delà de 7,5-10 % :\nremontée d'eau\nprobable (BRE)", "above 7.5-10 %:\nrising damp\nlikely (BRE)"))):
        ax.text(x, -0.6, t, ha="center", va="bottom", fontsize=7, color=ENCRE_3, clip_on=False)
    places = {"F": (9.3, 14.2, "left"), "C": (0.15, 11.0, "left"), "A": (10.3, 3.2, "center")}
    for mur, nom in murs.items():
        es = [e for e in POTS if e.startswith(mur)]
        y = [milieu(pre[e]["profondeur_cm"]) for e in es]
        ax.errorbar([R["pots"][e]["w_pct"] for e in es], y, xerr=[R["pots"][e]["incertitude_pct"] for e in es], color=COUL[mur],
                    lw=2, marker="o", ms=8, mec="white", mew=2, capsize=0, elinewidth=1.2, zorder=3)
        px, py, ha = places[mur]
        ax.text(px, py, nom, color=ENCRE, fontsize=8, ha=ha)
    fac = R["facade_0_20_cm"]
    ax.errorbar([fac["w_pct"]], [10], xerr=[fac["incertitude_pct"]], yerr=[10], color=COUL["F"], marker="s", ms=9, mfc="white",
                mew=2, lw=0, elinewidth=1, capsize=3, zorder=4)
    ax.text(fac["w_pct"] + 0.35, 11.4, _("4 tranches regroupées", "4 slices pooled"), fontsize=7.5, color=ENCRE)
    ax.set_ylim(22, 0)
    ax.set_xlim(0, 16)
    ax.set_xlabel(_("Teneur en eau (% de la masse de terre sèche)", "Water content (% of dry earth mass)"))
    ax.set_ylabel(_("Profondeur depuis la face percée (cm)", "Depth from the drilled face (cm)"))
    ax.text(15.9, 21.3, _("barres : ± 1 écart-type dû aux pesées", "bars: ± 1 standard deviation from weighing"), fontsize=7, color=ENCRE_3, ha="right")
    enregistrer(fig, "fig_profils", lang)


def fig_isotherme(lang):
    """Courbes d'équilibre de deux sols publiés (autres terres que ce mur) et teneurs en eau mesurées reportées dessus."""
    _ = traducteur(lang)
    R = resultats()
    iso = lire_isothermes()
    fig, ax = plt.subplots(figsize=(9.5, 4.9))
    for sol, c in SOLS.items():
        courbe = courbe_sechage(iso[sol])
        bas = [p for p in courbe if p[0] <= 90]
        haut = [p for p in courbe if p[0] >= 93]
        ax.plot(*zip(*bas), color=c, lw=2, marker="o", ms=3, label=_(f"Sol {sol} (Phung 2018)", f"Soil {sol} (Phung 2018)"))
        ax.plot(*zip(*haut), color=c, lw=2, marker="o", ms=3)
        ax.plot([bas[-1][0], haut[0][0]], [bas[-1][1], haut[0][1]], color=c, lw=1.2, ls=(0, (1, 2)))
    fac = R["facade_0_20_cm"]
    ax.axhspan(fac["w_pct"] - fac["incertitude_pct"], fac["w_pct"] + fac["incertitude_pct"], color=COUL["F"], alpha=0.15, lw=0)
    ax.axhline(fac["w_pct"], color=COUL["F"], lw=1.4)
    ax.text(31, fac["w_pct"] + 0.15, _(f"façade sud, 0-20 cm regroupé : {nombre(fac['w_pct'], lang)} ± {nombre(fac['incertitude_pct'], lang)} %",
                                      f"south façade, 0-20 cm pooled: {nombre(fac['w_pct'], lang)} ± {nombre(fac['incertitude_pct'], lang)} %"),
            fontsize=7.5, color=ENCRE, va="bottom")
    a1 = R["pots"]["A1"]
    ax.axhline(a1["w_pct"], color=COUL["A"], lw=1.4)
    ax.text(31, a1["w_pct"] + 0.15, _(f"cabanon, 0-10 cm : {nombre(a1['w_pct'], lang)} ± {nombre(a1['incertitude_pct'], lang)} %",
                                      f"garden shed, 0-10 cm: {nombre(a1['w_pct'], lang)} ± {nombre(a1['incertitude_pct'], lang)} %"),
            fontsize=7.5, color=ENCRE, va="bottom")
    sec = [R["pots"][e]["w_pct"] for e in ("C1", "C2", "A2")]
    ax.axhspan(min(sec), max(sec), color=COUL["C"], alpha=0.25, lw=0)
    lo, hi = nombre(min(sec), lang), nombre(max(sec), lang)
    ax.text(31, max(sec) + 0.15, _(f"combles et cabanon 10-20 cm : {lo} à {hi} %", f"attic and shed 10-20 cm: {lo} to {hi} %"), fontsize=7.5, color=ENCRE, va="bottom")
    ax.annotate(_("de 80 à 90 % d'humidité relative,\nseulement + 0,5 point d'eau", "from 80 to 90 % relative humidity,\nonly + 0.5 point of water"),
                (85, 3.1), (66, 6.2), fontsize=7.5, color=ENCRE, arrowprops={"arrowstyle": "-", "color": ENCRE_3, "lw": 0.8})
    ax.set_xlim(30, 100)
    ax.set_ylim(0, 13)
    ax.set_xlabel(_("Humidité relative d'équilibre (%)", "Equilibrium relative humidity (%)"))
    ax.set_ylabel(_("Teneur en eau (% masse sèche)", "Water content (% dry mass)"))
    ax.legend(loc="upper left", fontsize=8)
    ax.set_axisbelow(True)
    enregistrer(fig, "fig_isotherme", lang)


def main():
    for lang in langues():
        fig_protocole(lang)
        fig_ecarts(lang)
        fig_bruit(lang)
        fig_profils(lang)
        fig_isotherme(lang)


if __name__ == "__main__":
    main()
