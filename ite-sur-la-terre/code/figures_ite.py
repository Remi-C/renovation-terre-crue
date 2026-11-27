"""Figures du sujet « ITE sur la terre » : fig_parements, fig_accroche, fig_regimes (FR et EN), schémas sans données propres."""

# Depuis la racine du dépôt : python3 ite-sur-la-terre/code/figures_ite.py [--langue fr|en]
# Schémas de principe, pas à l'échelle. Les seuls chiffres tracés (fig_regimes) sont recopiés ici avec leur source :
# pesées publiées du sujet « Humidité de la bauge », et correspondances teneur en eau / humidité relative des calculs de
# l'auteur (non publiés, terre du mur non caractérisée).

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyArrowPatch, Polygon, Rectangle  # noqa: E402

SUJET = Path(__file__).resolve().parent.parent
FIGURES = SUJET / "figures"

ENCRE, ENCRE_2, ENCRE_3 = "#0b0b0b", "#52514e", "#8a8984"
GRILLE = "#e4e3df"
FOND = "#fcfcfb"
# Couleurs des matières (identité, pas rang) ; textes toujours en encre neutre.
TERRE, TERRE_FONCE = "#c9a27a", "#8a6440"
ROCHE, BOIS_LAINE, BOIS = "#e8d77a", "#d9b48a", "#b07a45"
ENDUIT, LAME, BARDAGE = "#efece6", "#ffffff", "#7d8b99"
MACON, CHARPENTE = "#a7a39b", "#6f4a2a"
EAU = "#2a78d6"
# Rampe séquentielle d'une seule teinte, du sec (clair) à l'humide (foncé), pour fig_regimes.
BANDES = ("#e3eefb", "#a9c8ef", "#5f97dc")

plt.rcParams.update({
    "font.family": "sans-serif", "font.sans-serif": ["DejaVu Sans"], "font.size": 12, "axes.edgecolor": ENCRE_3, "axes.labelcolor": ENCRE_2,
    "xtick.color": ENCRE_2, "ytick.color": ENCRE_2, "axes.grid": False, "lines.linewidth": 2,
    "figure.facecolor": FOND, "axes.facecolor": FOND, "savefig.facecolor": FOND, "svg.fonttype": "none",
    "svg.hashsalt": "ite-sur-la-terre", "axes.spines.top": False, "axes.spines.right": False,
    "axes.titleweight": "bold", "axes.titlesize": 13, "axes.titlecolor": ENCRE,
})

LANGUES = ("fr", "en")


def langues():
    if "--langue" not in sys.argv:
        return LANGUES
    i = sys.argv.index("--langue")
    lang = sys.argv[i + 1] if i + 1 < len(sys.argv) else ""
    if lang not in LANGUES:
        sys.exit("usage : --langue fr  ou  --langue en  (sans l'option : les deux)")
    return (lang,)


def traducteur(lang):
    return lambda fr, en: fr if lang == "fr" else en


def nombre(x, lang, fmt=".1f"):
    t = format(x, fmt)
    return t.replace(".", ",") if lang == "fr" else t


def enregistrer(fig, ident, lang):
    FIGURES.mkdir(exist_ok=True)
    nom = ident if lang == "fr" else f"{ident}_{lang}"
    fig.savefig(FIGURES / f"{nom}.png", dpi=200, bbox_inches="tight", metadata={"Software": None})
    fig.savefig(FIGURES / f"{nom}.svg", bbox_inches="tight", metadata={"Date": None, "Creator": None})
    plt.close(fig)
    print(f"figures/{nom}.png, .svg")


def fleche(ax, a, b, couleur=EAU, lw=1.6, style="-|>", ls="-"):
    ax.add_patch(FancyArrowPatch(a, b, arrowstyle=style, mutation_scale=11, color=couleur, lw=lw, linestyle=ls, zorder=5))


def couche(ax, x, y, l, h, fc, hatch=None, ec=ENCRE_3, lw=0.8):
    ax.add_patch(Rectangle((x, y), l, h, fc=fc, ec=ec, lw=lw, hatch=hatch))


# ------------------------------------------------------------------------------------------------ fig_parements
def fig_parements(lang):
    """Les deux familles de parement, en coupe horizontale : enduit posé sur l'isolant, ou isolant puis lame d'air
    ventilée et bardage ; chemin de la vapeur venue de la bauge et endroits où l'eau peut s'accumuler."""
    _ = traducteur(lang)
    fig, axes = plt.subplots(2, 1, figsize=(9, 9.2))
    h = 3.0
    xb, xi = 2.4, 2.2            # largeur dessinée de la bauge, de l'isolant
    xe = xb + xi                 # face extérieure de l'isolant

    def bauge(ax):
        couche(ax, 0, 0, xb, h, TERRE)
        for yy in (0.5, 1.3, 2.1):
            ax.plot([0.2, xb - 0.25], [yy, yy + 0.25], color=TERRE_FONCE, lw=0.6, alpha=0.5)
        ax.text(xb / 2, h + 0.18, _("bauge\n50 à 70 cm", "cob\n50 to 70 cm"), ha="center", va="bottom", fontsize=11, color=ENCRE)
        ax.text(-0.15, h / 2, _("intérieur", "inside"), rotation=90, ha="right", va="center", fontsize=10.5, color=ENCRE_3)
        ax.text(xb + xi / 2, h + 0.18, _("isolant\nlaine de roche\nou de bois", "insulation\nstone wool\nor wood fibre"), ha="center", va="bottom", fontsize=11, color=ENCRE)
        for yy in (0.7, 1.5, 2.3):
            fleche(ax, (xb - 0.8, yy), (xe - 0.08, yy))

    def note(ax, point, xy, texte):
        ax.annotate(texte, point, xy, fontsize=10.5, color=ENCRE, ha="left", va="top",
                    arrowprops={"arrowstyle": "-", "color": ENCRE_3, "lw": 0.8})

    # A. enduit sur isolant
    ax = axes[0]
    bauge(ax)
    couche(ax, xb, 0, xi, h, ROCHE, hatch="////")
    couche(ax, xe, 0, 0.22, h, ENDUIT, ec=ENCRE_2, lw=1.0)
    ax.text(xe + 0.35, h + 0.18, _("enduit\nà la chaux", "lime\nrender"), ha="left", va="bottom", fontsize=11, color=ENCRE)
    ax.text(xe + 0.5, h / 2, _("dehors", "outside"), rotation=90, ha="left", va="center", fontsize=10.5, color=ENCRE_3)
    ax.add_patch(Rectangle((xe - 0.18, 0.15), 0.18, h - 0.3, fc=EAU, alpha=0.25, lw=0))
    ax.add_patch(Rectangle((xb, 0.15), 0.14, h - 0.3, fc=EAU, alpha=0.18, lw=0))
    note(ax, (xb + 0.07, 0.35), (0.0, -0.45), _("① contre la terre : air très humide\nsi le mur l'est (moisissure)", "① against the earth: very humid air\nif the wall is (mould)"))
    note(ax, (xe - 0.09, 0.35), (xe - 0.6, -0.45), _("② l'hiver, la vapeur arrive sur la\nface froide : l'eau s'y accumule", "② in winter the vapour reaches the\ncold face: water builds up there"))
    ax.set_title(_("A. Enduit posé sur l'isolant", "A. Render applied on the insulation"), loc="left")
    ax.set_xlim(-0.5, 8.0)
    ax.set_ylim(-1.6, h + 1.4)
    ax.axis("off")

    # B. parement ventilé
    ax = axes[1]
    bauge(ax)
    couche(ax, xb, 0, xi, h, BOIS_LAINE, hatch="\\\\\\\\")
    couche(ax, xe, 0, 0.06, h, "#cfd8e3", ec=ENCRE_3, lw=0.6)
    couche(ax, xe + 0.06, 0, 0.5, h, LAME, ec=GRILLE, lw=0.6)
    couche(ax, xe + 0.56, 0, 0.2, h, BARDAGE, ec=ENCRE_2, lw=1.0)
    xl = xe + 0.31
    ax.text(xl, h + 0.18, _("lame\nd'air", "air\ngap"), ha="center", va="bottom", fontsize=11, color=ENCRE)
    ax.text(xe + 1.0, h + 0.18, _("bardage bois\nou plaque minérale", "timber cladding\nor mineral board"), ha="left", va="bottom", fontsize=11, color=ENCRE)
    ax.text(xe + 1.0, h / 2, _("dehors", "outside"), rotation=90, ha="left", va="center", fontsize=10.5, color=ENCRE_3)
    fleche(ax, (xl, 0.1), (xl, h - 0.1), couleur=ENCRE_2, lw=1.4)
    note(ax, (xe + 0.03, 0.3), (0.0, -0.45), _("pare-pluie ouvert à la vapeur", "membrane open to vapour"))
    note(ax, (xl, 0.5), (xe - 0.6, -0.45), _("l'air de la lame, renouvelé par le bas et\nle haut, emporte la vapeur à mesure qu'elle sort", "air in the gap, renewed from bottom and\ntop, carries the vapour away as it comes out"))
    ax.set_title(_("B. Isolant, lame d'air ventilée, bardage", "B. Insulation, ventilated air gap, cladding"), loc="left")
    ax.set_xlim(-0.5, 8.0)
    ax.set_ylim(-1.6, h + 1.4)
    ax.axis("off")

    fig.text(0.01, -0.02, _("Coupes horizontales de principe, pas à l'échelle. Flèches bleues : la vapeur d'eau que la bauge rend en séchant.",
                            "Schematic horizontal sections, not to scale. Blue arrows: the water vapour the cob gives off as it dries."),
             fontsize=10.5, color=ENCRE_3)
    enregistrer(fig, "fig_parements", lang)


# ------------------------------------------------------------------------------------------------- fig_accroche
def fig_accroche(lang):
    """Quatre façons de tenir l'isolation, en coupe verticale : vissée dans la bauge, ossature suspendue à la charpente,
    ossature autoportante sur une maçonnerie en pied, ossature accrochée à la bauge."""
    _ = traducteur(lang)
    fig, grille = plt.subplots(2, 2, figsize=(9, 10.5))
    axes = grille.ravel()
    H = 4.0

    def mur(ax, avec_toit=True):
        couche(ax, 0, 0, 1.4, H, TERRE)
        couche(ax, -0.2, -0.5, 1.8, 0.5, MACON)          # soubassement / fondation
        ax.plot([-0.4, 3.4], [-0.5, -0.5], color=ENCRE_3, lw=0.8)
        if avec_toit:
            ax.add_patch(Polygon([(-0.3, H), (3.3, H - 0.9), (3.3, H - 0.6), (-0.3, H + 0.3)], closed=True, fc=CHARPENTE, ec=ENCRE_2, lw=0.8))
        ax.text(0.7, H / 2, _("bauge", "cob"), rotation=90, ha="center", va="center", fontsize=11, color=ENCRE)

    def vis(ax, x0, x1, y):
        ax.plot([x0, x1], [y, y], color=ENCRE, lw=1.8, solid_capstyle="butt")
        ax.plot([x1, x1], [y - 0.07, y + 0.07], color=ENCRE, lw=1.8)

    def charge(ax, x, y):
        fleche(ax, (x, y), (x, y - 0.55), couleur=EAU, lw=1.6)

    # a. isolant vissé ou chevillé dans la bauge
    ax = axes[0]
    mur(ax)
    couche(ax, 1.4, 0.05, 0.9, H - 0.95, ROCHE, hatch="////")
    couche(ax, 2.3, 0.05, 0.08, H - 0.95, ENDUIT, ec=ENCRE_2, lw=1.0)
    for y in (0.6, 1.5, 2.4):
        vis(ax, 0.7, 2.38, y)
        ax.add_patch(Rectangle((2.3, y - 0.17), 0.08, 0.34, fc=ENCRE_2, lw=0))
    charge(ax, 1.85, 1.95)
    ax.set_title(_("a. Isolant fixé\ndans la bauge", "a. Insulation fixed\ninto the cob"), loc="left", fontsize=12.5)
    ax.text(0, -0.75, _("vis ou chevilles à rosace :\nla bauge porte tout", "screws or plug anchors:\nthe cob carries everything"), ha="left", va="top", fontsize=10.5, color=ENCRE)

    # b. ossature suspendue à la charpente
    ax = axes[1]
    mur(ax)
    couche(ax, 1.4, 0.05, 0.95, H - 0.95, BOIS_LAINE, hatch="\\\\\\\\")
    couche(ax, 2.35, 0.05, 0.16, H - 0.6, BOIS, ec=ENCRE_2)
    couche(ax, 2.51, 0.05, 0.1, H - 0.95, BARDAGE, ec=ENCRE_2)
    ax.plot([2.43, 2.43], [H - 0.55, H - 0.25], color=ENCRE, lw=2.2)
    fleche(ax, (2.43, 1.2), (2.43, H - 0.6), couleur=EAU, lw=1.6)
    ax.text(2.75, H - 1.45, _("suspente", "hanger"), ha="left", va="center", fontsize=10, color=ENCRE_2)
    ax.set_title(_("b. Ossature suspendue\nà la charpente", "b. Frame hung from\nthe roof structure"), loc="left", fontsize=12.5)
    ax.text(0, -0.75, _("le poids remonte à la charpente ;\nla bauge ne tient que le vent", "the weight goes up to the roof;\nthe cob only takes the wind"), ha="left", va="top", fontsize=10.5, color=ENCRE)

    # c. ossature autoportante sur maçonnerie en pied
    ax = axes[2]
    mur(ax)
    couche(ax, 1.6, -0.5, 1.1, 0.75, MACON, ec=ENCRE_2)
    ax.text(2.15, -0.12, _("muret", "plinth"), ha="center", va="center", fontsize=10, color=ENCRE)
    couche(ax, 1.4, 0.25, 0.95, H - 1.15, BOIS_LAINE, hatch="\\\\\\\\")
    couche(ax, 2.35, 0.25, 0.16, H - 1.15, BOIS, ec=ENCRE_2)
    couche(ax, 2.51, 0.25, 0.1, H - 1.15, BARDAGE, ec=ENCRE_2)
    fleche(ax, (2.43, 2.6), (2.43, 0.3), couleur=EAU, lw=1.6)
    vis(ax, 0.9, 2.45, H - 1.25)
    ax.text(2.75, H - 1.25, _("liaison\nau vent", "wind\ntie"), ha="left", va="center", fontsize=10, color=ENCRE_2)
    ax.set_title(_("c. Ossature autoportante\nsur maçonnerie en pied", "c. Self-supporting frame\non a masonry plinth"), loc="left", fontsize=12.5)
    ax.text(0, -0.75, _("le poids descend au sol ;\nla bauge ne tient que le vent", "the weight goes down to the ground;\nthe cob only takes the wind"), ha="left", va="top", fontsize=10.5, color=ENCRE)

    # d. ossature accrochée à la bauge
    ax = axes[3]
    mur(ax)
    couche(ax, 1.4, 0.05, 0.95, H - 0.95, BOIS_LAINE, hatch="\\\\\\\\")
    couche(ax, 2.35, 0.05, 0.16, H - 0.95, BOIS, ec=ENCRE_2)
    couche(ax, 2.51, 0.05, 0.1, H - 0.95, BARDAGE, ec=ENCRE_2)
    for y in (0.5, 1.4, 2.3, 3.0):
        vis(ax, 0.55, 2.47, y)
    charge(ax, 2.43, 1.95)
    ax.set_title(_("d. Ossature accrochée\nà la bauge", "d. Frame screwed\nto the cob"), loc="left", fontsize=12.5)
    ax.text(0, -0.75, _("longues vis dans la terre :\nla bauge porte tout", "long screws into the earth:\nthe cob carries everything"), ha="left", va="top", fontsize=10.5, color=ENCRE)

    for ax in axes:
        ax.set_xlim(-0.5, 3.5)
        ax.set_ylim(-1.7, H + 0.5)
        ax.set_aspect("equal")
        ax.axis("off")
    fig.text(0.01, 0.0, _("Coupes verticales de principe, pas à l'échelle. Flèches bleues : où va le poids de l'isolation et de son parement.",
                          "Schematic vertical sections, not to scale. Blue arrows: where the weight of the insulation and its cladding goes."),
             fontsize=10.5, color=ENCRE_3)
    enregistrer(fig, "fig_accroche", lang)


# ------------------------------------------------------------------------------------------------- fig_regimes
# Pesées publiées du sujet « Humidité de la bauge » (18/11/2026), en % de la masse de terre sèche : (libellé, valeur,
# incertitude, profondeur).
PESEES = [
    (("Combles, refend", "Attic, cross wall"), 1.4, 0.3, "0-5 cm"),
    (("Combles, refend", "Attic, cross wall"), 1.8, 0.5, "5-13 cm"),
    (("Cabanon, cœur", "Garden shed, core"), 1.7, 0.2, "10-20 cm"),
    (("Façade sud, regroupée", "South façade, pooled"), 5.3, 1.6, "0-20 cm"),
]
# Correspondances des calculs de l'auteur (courbe de rétention d'une bauge de laboratoire, non mesurée sur ces murs) :
# teneur en eau (%) à l'équilibre avec une humidité relative donnée.
EQUIVALENTS = [(1.9, 65), (2.3, 70), (3.0, 80), (3.3, 90)]


def fig_regimes(lang):
    """Les trois régimes des pistes de l'auteur selon l'eau moyenne du mur, avec les pesées publiées et les humidités
    relatives que donne la courbe de rétention des calculs."""
    _ = traducteur(lang)
    fig, ax = plt.subplots(figsize=(10, 4.8))
    bornes = [(0, 2.0), (2.0, 3.0), (3.0, 7.5)]
    titres = [
        _("Assez sec\nsous enduit, ça passe", "Dry enough\nunder render, it works"),
        _("Un peu\nau-dessus\nsécher l'été,\nisoler en fin\nd'été", "Somewhat\nabove\ndry it in\nsummer, insulate\nat summer's end"),
        _("Trop humide, ou remontées d'eau\nparement ventilé (bardage bois ou minéral)", "Too wet, or rising damp\nventilated cladding (timber or mineral)"),
    ]
    for (a, b), c, t in zip(bornes, BANDES, titres):
        ax.add_patch(Rectangle((a, 0), b - a, 1, fc=c, ec=FOND, lw=2))
        ax.text((a + b) / 2, 0.95, t, ha="center", va="top", fontsize=10.5 if a == 2.0 else 11, color=ENCRE, weight="bold" if a == 0 else None)
    for x in (2.0, 3.0):
        ax.plot([x, x], [0, 1], color=FOND, lw=0)
    # pesées
    ys = [0.36, 0.24, 0.48, 0.36]
    for (lib, v, inc, prof), y in zip(PESEES, ys):
        ax.errorbar(v, y, xerr=inc, fmt="o", ms=7, color=ENCRE, ecolor=ENCRE_2, elinewidth=1.2, capsize=3,
                    mec=FOND, mew=1.5)
        cote = "left" if v < 3 else "left"
        ax.text(v + inc + 0.08, y, f"{lib[0] if lang == 'fr' else lib[1]} ({prof})", ha=cote, va="center", fontsize=10, color=ENCRE)
    # équivalents en humidité relative, en marques sous l'axe
    for w, hr in EQUIVALENTS:
        ax.plot([w, w], [0, 0.05], color=ENCRE_2, lw=1)
        ax.text(w, 0.07, f"{hr} %", ha="center", va="bottom", fontsize=9.5, color=ENCRE_2, rotation=90)
    ax.text(3.45, 0.07, _("← humidité relative d'équilibre\n    dans nos calculs ⚠", "← equilibrium relative humidity\n    in our calculations ⚠"),
            ha="left", va="bottom", fontsize=9.5, color=ENCRE_2)
    ax.set_xlim(0, 7.5)
    ax.set_ylim(0, 1)
    ax.set_yticks([])
    ax.spines["left"].set_visible(False)
    ax.set_xlabel(_("Eau dans le mur (% de la masse de terre sèche)", "Water in the wall (% of dry earth mass)"))
    ax.set_xticks(range(0, 8))
    ax.set_xticklabels([nombre(x, lang, ".0f") for x in range(0, 8)])
    fig.text(0.01, -0.07, _("Bandes : moyenne dans l'épaisseur du mur ; limites approximatives. Points : pesées du 18/11/2026, chacune à sa profondeur,\n"
                            "barres = incertitude. Humidités relatives : courbe de rétention d'une bauge de laboratoire, non mesurée sur ces murs.",
                            "Bands: average over the wall thickness; approximate limits. Dots: weighings of 18 Nov. 2026, each at its depth,\n"
                            "bars = uncertainty. Relative humidities: retention curve of a laboratory cob, not measured on these walls."),
             fontsize=10, color=ENCRE_3)
    enregistrer(fig, "fig_regimes", lang)


if __name__ == "__main__":
    for lang in langues():
        fig_parements(lang)
        fig_accroche(lang)
        fig_regimes(lang)
