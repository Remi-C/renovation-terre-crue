"""Schémas du papier : fig_implantation, fig_montage, fig_theorie, fig_platine, fig_cone, en français et en anglais (dessins, cotes approximatives)."""

# Exécution, depuis la racine du dépôt : python3 vis-dans-la-bauge/code/schemas.py   (« --langue fr|en » pour une seule)
# Implantation et montage : dessinés d'après la description du montage (donnees/README.md) et les photos ; cotes
# approximatives. Théorie et platine : interprétation, non mesurée ; le seul calcul est la déformée d'une vis Ø10 sur
# appui élastique (poutre de Hetényi), donnée pour la forme, pas pour une valeur.

import math

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle, Ellipse, FancyArrowPatch, FancyBboxPatch, Polygon, Rectangle

from style import ACIER, BAUGE, BAUGE_TRAIT, BOIS, CORDE, ENCRE, ENCRE_2, FOND, SERIES, enregistrer, langues, traducteur

ROUGE = SERIES[7]
CADRE = dict(fc=FOND, ec="none", alpha=0.9, pad=1.5)


def texte(ax, x, y, t, **kw):
    """Texte lisible même posé sur la bauge hachurée."""
    kw.setdefault("fontsize", 8.5)
    kw.setdefault("color", ENCRE)
    return ax.text(x, y, t, bbox=CADRE, zorder=8, **kw)


def ligne_libre(x_face, y0, A=3.6, lam=4.0, prof=16.0, tete=3.0):
    """Vis à tête libre : déformée amortie dans la bauge, tête qui bascule dans le prolongement (coupe)."""
    z = np.linspace(0, prof, 80)
    y = y0 - A * np.exp(-z / lam) * np.cos(z / lam)
    zt = np.linspace(-tete, 0, 10)
    yt = y0 - A + (A / lam) * zt
    return np.r_[x_face - zt, x_face - z], np.r_[yt, y]


def ligne_retenue(x_face, y0, A=3.0, long_pli=7.0, prof=16.0, tete=4.5):
    """Vis à tête retenue : tête et planche restent d'aplomb, la vis plie en S dans la bauge (coupe)."""
    z = np.linspace(-tete, prof, 100)
    y = np.where(z < 0, y0, y0 + A * (1 - np.cos(np.pi * np.clip(z, 0, long_pli) / long_pli)) / 2)
    return x_face - z, y


def fleche(ax, xy0, xy1, coul=ROUGE, lw=2.0, style="-|>", ms=14):
    ax.add_patch(FancyArrowPatch(xy0, xy1, arrowstyle=style, mutation_scale=ms, color=coul, lw=lw))


def mur_coupe(ax, x0, x1, y0, y1):
    """Bauge en coupe : à gauche de x1 (face du mur)."""
    ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, facecolor=BAUGE, edgecolor=BAUGE_TRAIT, lw=0,
                           hatch="..", zorder=0))
    ax.plot([x1, x1], [y0, y1], color=BAUGE_TRAIT, lw=1.5)


def vis_droite(ax, x0, y0, x1, y1, d=1.0, coul=ACIER, tete=True, lw=3.0):
    ax.plot([x0, x1], [y0, y1], color=coul, lw=lw, solid_capstyle="butt", zorder=4)
    n = int(math.hypot(x1 - x0, y1 - y0) / (0.9 * d)) or 1
    for t in np.linspace(0.05, 0.95, n):
        x, y = x0 + t * (x1 - x0), y0 + t * (y1 - y0)
        ax.plot([x - 0.15 * d, x + 0.15 * d], [y - 0.45 * d, y + 0.45 * d], color="#5c636b", lw=0.8, zorder=5)


# --------------------------------------------------------------------------------------------------- fig_implantation
def fig_implantation(lang):
    """Vue de face : planches en éventail au-dessus de la platine de réaction, chacune tirée à son tour vers le bas.
    Cotes de Rémi (01/11/2026) : planches à ≈ 1,70 m du sol, platine à ≈ 1,10 m, positions à ≈ 10 cm d'écart ;
    disposition d'après la photo photos/montage_eventail.jpg (1/6 à gauche, 6/6 à droite, planches tournées vers la
    platine)."""
    _ = traducteur(lang)
    fig, ax = plt.subplots(figsize=(7.8, 7.8))
    x0, x1, y0, y1 = -62, 62, 62, 198
    ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, facecolor=BAUGE, edgecolor=BAUGE_TRAIT, lw=1.2, zorder=0))
    ax.text(x0 + 3, y1 - 3, _("mur en bauge, vue de face", "cob wall, front view"), va="top", fontsize=9, color=ENCRE_2)
    cx, cy, rayon, pas = 0.0, 110.0, 60.0, 10.0
    # hauteurs
    for y, t in ((cy, _("≈ 1,10 m", "≈ 1.10 m")), (cy + rayon, _("≈ 1,70 m", "≈ 1.70 m"))):
        ax.plot([x0 - 6, x0], [y, y], color=ENCRE_2, lw=1)
        ax.text(x0 - 7, y, t, ha="right", va="center", fontsize=8.5, color=ENCRE)
    ax.text(x0 - 7, y0 + 2, _("hauteur\ndepuis le sol", "height\nabove ground"), ha="right", va="bottom", fontsize=8, color=ENCRE_2)
    # platine de réaction, vis de fixation, équerre de la tige filetée
    lp, hp = 20.0, 26.0
    ax.add_patch(Rectangle((cx - lp / 2, cy - hp / 2), lp, hp, facecolor="#3a3f45", edgecolor="none", zorder=3))
    for dx, dy in ((-7, -10), (7, -10), (-7, 10), (7, 10)):
        ax.add_patch(Circle((cx + dx, cy + dy), 1.2, color="#c9ccd1", zorder=4))
    ax.add_patch(Rectangle((cx - 2.2, cy - 1.5), 4.4, 3.0, facecolor="#8b9097", edgecolor="none", zorder=4))
    texte(ax, cx + lp / 2 + 2, cy - 4, _("platine de réaction\n4 vis Ø10 × 200", "reaction plate\n4 screws Ø10 × 200"), va="top")

    def angle(r):
        return math.pi / 2 + (3.5 - r) * pas / rayon

    def point(r, d=rayon):
        a = angle(r)
        return cx + d * math.cos(a), cy + d * math.sin(a)

    positions = [(1, "1/6", _("C1, puis C8", "C1, then C8")), (2, "2/6", "C2"), (3, "3/6", "C3"), (4, "4/6", "C4"), (5, "5/6", "C5"),
                 (6, "6/6", "C6")]
    actif = 3
    for r, pos, nom in positions:
        a = angle(r)
        x, y = point(r)
        ax.add_patch(Polygon(_rect_tourne(x, y, 6.0, 13.0, a - math.pi / 2), closed=True, facecolor=BOIS,
                             edgecolor="#6d4f28", lw=1.0, zorder=3))
        ax.add_patch(Circle((x, y), 1.0, color="#3a3f45", zorder=4))
        if r != actif:  # corde au repos : boucle qui pend sous la planche
            ax.add_patch(Ellipse(point(r, rayon - 9.5), 3.2, 6.5, angle=math.degrees(a - math.pi / 2),
                                 facecolor="none", edgecolor=CORDE, lw=1.0, zorder=2))
        xt, yt = point(r, rayon + 11)
        ax.text(xt, yt, f"{pos}\n{nom}", ha="center", va="bottom", fontsize=8.2, color=ENCRE)
    # C7 : vis posée entre 5/6 et 6/6
    x7, y7 = point(5.5)
    ax.add_patch(Circle((x7, y7), 2.6, facecolor="none", edgecolor=ENCRE_2, lw=0.9, ls=(0, (2, 2)), zorder=5))
    ax.add_patch(Circle((x7, y7), 1.0, color="#3a3f45", zorder=5))
    ax.annotate(_("C7 entre 5/6 et 6/6", "C7 between 5/6 and 6/6"), xy=(x7 + 2, y7 - 2), xytext=(x7 + 6, y7 - 16), ha="left", va="top",
                fontsize=8.2, color=ENCRE, arrowprops=dict(arrowstyle="-", color=ENCRE_2, lw=0.8))
    # chaîne de l'essai en cours : corde, peson, manilles, anneau, tige filetée serrée sur la platine
    xa, ya = point(actif, rayon - 6.5)
    xb = cx
    y_peson_haut, y_peson_bas, y_anneau = 152.0, 140.0, 128.0
    xp = xa + (xb - xa) * (ya - y_peson_haut) / (ya - y_anneau)
    ax.plot([xa, xp], [ya, y_peson_haut], color=CORDE, lw=1.6, zorder=4)
    ax.add_patch(Rectangle((xp - 3.5, y_peson_bas), 7, y_peson_haut - y_peson_bas, facecolor=SERIES[1],
                           edgecolor="#8a3a17", lw=0.8, zorder=4))
    ax.plot([xp, xb], [y_peson_bas, y_anneau + 1.3], color="#8b9097", lw=1.6, zorder=4)
    ax.add_patch(Circle((xb, y_anneau), 1.3, facecolor="none", edgecolor="#5c636b", lw=1.4, zorder=5))
    ax.plot([xb, xb], [y_anneau - 1.3, cy - hp / 2 - 14], color="#5c636b", lw=2.2, zorder=5)
    texte(ax, xp - 5, (y_peson_haut + y_peson_bas) / 2, _("peson\n(essai en cours : 3/6)", "crane scale\n(test under way: 3/6)"), ha="right", va="center")
    texte(ax, cx - lp / 2 - 2, cy - hp / 2 - 4, _("tige filetée M12 :\non serre l'écrou\nsur la platine",
                                                      "M12 threaded rod:\nthe nut is tightened\non the plate"), ha="right",
          va="center")
    fleche(ax, (xp + 9, 152), (xp + 9, 128))
    texte(ax, xp + 11, 140, _("traction vers le bas,\nle long du mur", "pull downwards,\nalong the wall"), va="center")
    # cote entre deux positions
    xa1, ya1 = point(1, rayon + 4.5)
    xa2, ya2 = point(2, rayon + 4.5)
    ax.annotate("", xy=(xa1, ya1), xytext=(xa2, ya2), arrowprops=dict(arrowstyle="<->", color=ENCRE_2, lw=0.8))
    ax.text(xa1 - 3.5, ya1, "≈ 10 cm", ha="right", va="center", fontsize=8, color=ENCRE_2)
    ax.text(x0 + 3, y0 + 3, _("planches : douglas de 45 mm ; chêne, épaisseur non notée ; une vis par planche,\n"
                              "une boucle de corde passée dans chaque planche ; chaque essai tire une planche à son tour.",
                              "boards: Douglas fir 45 mm; oak, thickness not noted; one screw per board,\n"
                              "a rope loop through each board; each test pulls one board in turn."),
            fontsize=8, color=ENCRE_2, va="bottom")
    ax.set_xlim(x0 - 24, x1 + 2)
    ax.set_ylim(y0 - 2, y1 + 2)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(_("Implantation des essais du 30/10/2026 (vue de face, cotes approximatives)",
                   "Layout of the tests of 30 Oct. 2026 (front view, approximate dimensions)"), loc="left")
    enregistrer(fig, "fig_implantation", lang)


def _rect_tourne(x, y, l, h, ang):
    c, s = math.cos(ang), math.sin(ang)
    pts = [(-l / 2, -h / 2), (l / 2, -h / 2), (l / 2, h / 2), (-l / 2, h / 2)]
    return [(x + px * c - py * s, y + px * s + py * c) for px, py in pts]


# ------------------------------------------------------------------------------------------------------- fig_montage
def fig_montage(lang):
    """Coupe verticale perpendiculaire au mur : bauge à gauche, effort vers le bas, le long du mur."""
    _ = traducteur(lang)
    fig, ax = plt.subplots(figsize=(7.6, 8.6))
    mur_coupe(ax, -30, 0, 0, 106)
    ey = 82
    # vis essayée et planche
    ax.add_patch(Rectangle((0, ey - 6), 4.5, 12, facecolor=BOIS, edgecolor="#6d4f28", lw=1, zorder=3))
    vis_droite(ax, -16, ey + 2, 4.8, ey + 2, d=1.0)
    ax.add_patch(Rectangle((4.5, ey + 0.6), 0.6, 2.8, color="#5c636b", zorder=5))
    texte(ax, -28, ey + 7, _("vis essayée, ancrée dans la bauge", "screw under test, anchored in the cob"))
    texte(ax, 6.5, ey - 2.5, _("planche serrée contre le mur\n(douglas de 45 mm ;\nchêne, épaisseur non notée)",
                                    "board clamped to the wall\n(Douglas fir 45 mm;\noak, thickness not noted)"))
    # corde, peson, tige
    ax.plot([2.2, 2.2, 3.0], [ey - 6, ey - 12, ey - 15], color=CORDE, lw=2.2)
    texte(ax, 6.5, ey - 14, _("boucle de corde Dyneema\npassée dans la planche",
                                 "Dyneema rope loop\nthrough the board"))
    ax.add_patch(FancyBboxPatch((1.6, ey - 30), 3.0, 11, boxstyle="round,pad=0.3", facecolor=SERIES[1],
                                edgecolor="#8a3a17", lw=1, zorder=3))
    ax.plot([3.0, 3.0], [ey - 15, ey - 18.7], color=CORDE, lw=2.2)
    texte(ax, 6.5, ey - 26, _("peson numérique (1 t), manilles", "digital crane scale (1 t), shackles"))
    ax.plot([3.1, 3.4], [ey - 31, 22], color=ACIER, lw=3)
    texte(ax, 6.5, 40, _("tige filetée M12 : on tend la chaîne\nen serrant l'écrou à la visseuse",
                            "M12 threaded rod: the chain is tensioned\nby tightening the nut with the drill-driver"))
    # platine de réaction
    ax.add_patch(Rectangle((0, 18), 2.0, 16, facecolor="#3a3f45", edgecolor="none", zorder=3))
    vis_droite(ax, -20, 31, 2.2, 31, d=1.0)
    vis_droite(ax, -20, 21, 2.2, 21, d=1.0)
    ax.add_patch(Rectangle((2.0, 24.5), 3.2, 2.5, color="#3a3f45", zorder=3))
    ax.add_patch(Rectangle((2.4, 19.2), 2.0, 1.4, color="#1d2024", zorder=4))
    ax.add_patch(Rectangle((2.4, 17.4), 2.0, 1.4, color="#1d2024", zorder=4))
    texte(ax, 6.5, 22, _("platine de réaction, 4 vis Ø10 × 200 ;\ndouble écrou sous l'équerre",
                            "reaction plate, 4 screws Ø10 × 200;\ndouble nut under the bracket"))
    # comparateur : bras flexible depuis la platine, touche sur le dessus de la planche ; le bras passe à droite des
    # libellés pour ne croiser aucun texte
    ax.plot([2.0, 39.2, 39.4, 12.5], [33, 35.5, 86, 94], color="#2b2b2b", lw=2.4, solid_capstyle="round", zorder=5)
    ax.add_patch(Circle((10.5, 96), 2.6, facecolor="#f2f2f2", edgecolor="#2b2b2b", lw=1.4, zorder=6))
    ax.plot([9.3, 3.6], [93.8, ey + 6.1], color="#2b2b2b", lw=1.3, zorder=6)
    texte(ax, 14.5, 100, _("comparateur au 1/100 mm sur bras flexible,\nporté par la platine de réaction ;\n"
                           "touche sur le dessus de la planche,\ntige inclinée de 25 à 45°",
                           "dial gauge (0.01 mm) on a flexible arm,\nheld by the reaction plate;\n"
                           "tip on the top of the board,\nrod tilted 25 to 45°"), va="center")
    # effort et repères
    fleche(ax, (-3.5, ey + 0.5), (-3.5, ey - 13))
    texte(ax, -4.5, ey - 7, "F", ha="right", fontsize=11, color=ROUGE, fontweight="bold")
    texte(ax, -28, 3, _("bauge (coupe)", "cob (section)"), fontsize=9, color=ENCRE_2)
    texte(ax, -28, ey - 1, _("≈ 1,70 m du sol", "≈ 1.70 m above ground"), color=ENCRE_2)
    texte(ax, -28, 26, _("≈ 1,10 m du sol", "≈ 1.10 m above ground"), color=ENCRE_2)
    ax.set_xlim(-30, 40)
    ax.set_ylim(0, 106)
    ax.axis("off")
    ax.set_title(_("Montage, en coupe (échelle horizontale dilatée)", "Test rig, in section (horizontal scale stretched)"),
                 loc="left")
    enregistrer(fig, "fig_montage", lang)


# ------------------------------------------------------------------------------------------------------- fig_theorie
def deformee(x_mm, k, d_noyau=6.2, E=210_000.0):
    """Déformée relative d'une vis à tête libre sur appui élastique (Hetényi), chargée au nu du mur."""
    EI = E * math.pi * d_noyau ** 4 / 64
    beta = (k / (4 * EI)) ** 0.25
    return np.exp(-beta * x_mm) * np.cos(beta * x_mm)


def fig_theorie(lang):
    _ = traducteur(lang)
    fig, (a, b, c) = plt.subplots(3, 1, figsize=(8.0, 11.4), gridspec_kw={"height_ratios": [1, 1.05, 1.05]})
    # 1. seuls les premiers centimètres travaillent
    x = np.linspace(0, 150, 300)
    for i, k in enumerate((200.0, 500.0)):
        a.plot(x / 10, deformee(x, k), color=SERIES[i],
               label=(_("bauge plus souple", "softer cob") if i == 0 else _("bauge plus raide", "stiffer cob"))
               + f" (k = {k:.0f} N/mm²)")
    a.axvspan(0, 5, color="#f1efe9", zorder=0)
    a.axhline(0, color=ENCRE_2, lw=0.8)
    texte(a, 2.6, 0.75, _("3 à 5 premiers cm :\nla vis pousse sur la terre", "first 3 to 5 cm:\nthe screw pushes on the earth"), fontsize=8.6, va="top")
    a.text(14.8, 0.25, _("au-delà : la vis ne bouge presque plus ;\nla longueur sert à ne pas sortir du mur",
             "beyond: the screw hardly moves;\nlength keeps it from coming out of the wall"),
           ha="right", fontsize=8.6, color=ENCRE)
    a.set_xlim(0, 15)
    a.set_xlabel(_("profondeur dans la bauge (cm)", "depth in the cob (cm)"))
    a.set_ylabel(_("déplacement de la vis\n(1 = au nu du mur)", "screw movement\n(1 = at the wall face)"))
    a.legend(loc="upper right", fontsize=8)
    a.set_title(_("1. Seuls les premiers centimètres travaillent de côté (vis Ø10, poutre sur appui élastique)",
                  "1. Only the first few centimetres work sideways (Ø10 screw, beam on elastic foundation)"),
                loc="left", fontsize=10)
    # 2. tête libre ou retenue
    b.set_title(_("2. La pièce serrée sous la tête change la façon dont la vis plie",
                  "2. The piece clamped under the head changes how the screw bends"), loc="left", fontsize=10)
    for x0, titre in ((0, _("tête libre (vis seule, comme C8)", "free head (screw alone, like C8)")),
                      (42, _("tête retenue (planche serrée)", "restrained head (clamped board)"))):
        mur_coupe(b, x0, x0 + 18, 0, 30)
        if x0 == 0:
            xs, ys = ligne_libre(x0 + 18, 18)
            b.plot(xs, ys, color=ACIER, lw=4, solid_capstyle="round", zorder=4)
            b.plot(xs[0], ys[0], marker="s", ms=7, color="#5c636b", zorder=5)
            fleche(b, (x0 + 24, 17), (x0 + 24, 10))
            texte(b, x0 + 1, 30.5, _("la tête tourne : la vis plie\nen un endroit et bouge beaucoup",
                                    "the head rotates: the screw bends\nat one place and moves a lot"), va="top")
        else:
            b.add_patch(Rectangle((x0 + 18, 8), 4.5, 16, facecolor=BOIS, edgecolor="#6d4f28", lw=1))
            xs, ys = ligne_retenue(x0 + 18, 15)
            b.plot(xs, ys, color=ACIER, lw=4, solid_capstyle="round", zorder=4)
            b.plot(x0 + 22.6, 15, marker="s", ms=7, color="#5c636b", zorder=5)
            fleche(b, (x0 + 25, 17), (x0 + 25, 10))
            texte(b, x0 + 1, 30.5, _("la planche empêche la tête de tourner :\nla vis plie en deux endroits (en S)",
                                    "the board stops the head from rotating:\nthe screw bends at two places (S shape)"),
                  va="top")
        texte(b, x0 + 1, 2, titre, fontsize=9, fontweight="bold")
    b.set_xlim(-1, 84)
    b.set_ylim(0, 31)
    b.set_aspect("equal")
    b.axis("off")
    # 3. effet de corde et frottement
    c.set_title(_("3. La vis qui plie tire la planche contre le mur : le frottement aide",
                  "3. The bending screw pulls the board against the wall: friction helps"), loc="left", fontsize=10)
    mur_coupe(c, 0, 30, 0, 30)
    c.add_patch(Rectangle((30, 6), 6, 20, facecolor=BOIS, edgecolor="#6d4f28", lw=1))
    xs, ys = ligne_retenue(30, 14, A=3.5, long_pli=8, prof=20, tete=6.4)
    c.plot(xs, ys, color=ACIER, lw=4, solid_capstyle="round", zorder=4)
    c.plot(36.5, 14.0, marker="s", ms=8, color="#5c636b", zorder=5)
    fleche(c, (40, 19), (40, 7))
    c.text(41, 12.5, _("F : effort de côté", "F: sideways load"), fontsize=9, color=ENCRE)
    fleche(c, (26.5, 16.8), (21.5, 17.5), coul=SERIES[0], ms=12)
    texte(c, 4, 22.5, _("T : la vis pliée se tend\net tire la tête vers le mur",
                         "T: the bent screw goes into tension\nand pulls the head towards the wall"))
    fleche(c, (46, 23), (37, 23), coul=SERIES[0])
    c.text(47, 23, _("N : la planche est plaquée", "N: the board is pressed on"), fontsize=8.6, color=ENCRE,
           va="center")
    fleche(c, (30.6, 8), (30.6, 17), coul=SERIES[2])
    c.text(37.5, 3.5, _("frottement de la planche sur le mur :\nil s'oppose à F",
                        "friction of the board on the wall:\nit opposes F"), fontsize=8.6, color=ENCRE)
    c.set_xlim(-1, 72)
    c.set_ylim(0, 30)
    c.set_aspect("equal")
    c.axis("off")
    fig.text(0.01, 0.005, _("Interprétation des mesures, pas une mesure : la part de chaque mécanisme n'a pas été "
                            "mesurée.", "An interpretation of the measurements, not a measurement: the share of each "
                            "mechanism was not measured."), fontsize=8, color=ENCRE_2)
    fig.tight_layout(rect=(0, 0.015, 1, 1))
    enregistrer(fig, "fig_theorie", lang)


# ------------------------------------------------------------------------------------------------------- fig_platine
def fig_platine(lang):
    _ = traducteur(lang)
    fig, axes = plt.subplots(1, 2, figsize=(8.6, 4.3))
    cas = ((_("Platine mince : épaisseur ≤ ½ diamètre\n(Ø10 : 5 mm ou moins, ex. tôle de 2,5 mm)",
              "Thin plate: thickness ≤ ½ diameter\n(Ø10: 5 mm or less, e.g. 2.5 mm sheet)"), 0.6, "libre"),
           (_("Platine épaisse : épaisseur ≥ diamètre\n(Ø10 : 10 mm ou plus)",
              "Thick plate: thickness ≥ diameter\n(Ø10: 10 mm or more)"), 2.4, "retenue"))
    for ax, (titre, ep, forme) in zip(axes, cas):
        mur_coupe(ax, 0, 20, 0, 30)
        ax.add_patch(Rectangle((20, 5), ep, 22, facecolor="#3a3f45", edgecolor="none", zorder=2))
        if forme == "libre":
            xs, ys = ligne_libre(20, 18, tete=ep + 1.2)
            txt = _("la tête peut basculer dans la tôle :\nproche de la vis seule (C8),\nplus de mouvement",
                    "the head can tilt in the sheet:\nclose to the screw alone (C8),\nmore movement")
        else:
            xs, ys = ligne_retenue(20, 15, tete=ep + 0.8)
            txt = _("la tête est tenue :\nproche de la planche serrée\n(C1 à C7)",
                    "the head is held:\nclose to the clamped board\n(C1 to C7)")
        ax.plot(xs, ys, color=ACIER, lw=4, solid_capstyle="round", zorder=4)
        fleche(ax, (26, 22), (26, 10))
        texte(ax, 1, 1.5, txt, fontsize=8.4)
        ax.set_title(titre, loc="left", fontsize=9.5)
        ax.set_xlim(0, 30)
        ax.set_ylim(0, 30)
        ax.set_aspect("equal")
        ax.axis("off")
    fig.text(0.01, 0.01, _("Extrapolation non mesurée. Seuils « mince » et « épaisse » : règle des assemblages "
                           "bois-métal de l'Eurocode 5.\nEntre les deux : comportement intermédiaire. Le frottement de "
                           "l'acier sur la bauge n'est pas celui du bois.",
                           "Extrapolation, not measured. “Thin” and “thick” thresholds: Eurocode 5 rule for "
                           "timber-to-steel joints.\nIn between: intermediate behaviour. The friction of steel on cob is "
                           "not that of timber."), fontsize=7.8, color=ENCRE_2)
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    enregistrer(fig, "fig_platine", lang)


def _cone_et_filet(ax, L, prof_cone, cone_visible, _):
    """Coupe d'une vis tirée hors du mur : cône de bauge arraché en surface, filet qui glisse au-delà."""
    face, y0, r = 20.0, 15.0, 4.0                       # face du mur (cm), axe de la vis, rayon du cône en surface
    mur_coupe(ax, 0, face, 6, 24)
    # cône de surface, décalé vers la sortie : il part avec la vis
    dx = 0.7
    pts = [(face + dx, y0 - r), (face + dx, y0 + r), (face - prof_cone + dx, y0 + 0.9), (face - prof_cone + dx, y0 - 0.9)]
    ax.add_patch(Polygon(pts, closed=True, facecolor="#c9b48f", edgecolor=ROUGE, lw=1.4,
                         ls="-" if cone_visible else (0, (3, 2)), zorder=2, alpha=1 if cone_visible else 0.55))
    # vis : de la tête (dehors) à la pointe
    vis_droite(ax, face + 3.2 + dx, y0, face - L + dx, y0, d=1.0)
    ax.add_patch(Rectangle((face + 3.0 + dx, y0 - 1.3), 0.5, 2.6, facecolor=ACIER, edgecolor="none", zorder=5))
    fleche(ax, (face + 3.6 + dx, y0), (face + 8.5, y0))
    texte(ax, face + 4.3, y0 + 1.6, _("on tire", "pull"), fontsize=8.4, color=ROUGE)
    # le filet au-delà du cône : la bauge le retient en frottant (flèches vers l'intérieur du mur)
    xs = np.arange(face - prof_cone - 1.0, face - L + 0.8, -1.6)
    for x in xs:
        for s in (-1, 1):
            fleche(ax, (x + 0.6, y0 + s * 1.5), (x - 0.6, y0 + s * 1.5), coul=SERIES[0], lw=1.3, ms=8)
    return face, y0, r


def fig_cone(lang):
    _ = traducteur(lang)
    fig, axes = plt.subplots(1, 2, figsize=(8.6, 3.9))
    # (a) vis courte, cône visible ; (b) vis longue, cône qui ne grandit plus (peut-être invisible)
    for ax, (titre, L, prof_cone, visible) in zip(axes, (
            (_("(a) Vis courte (7 à 9 cm) : observé", "(a) Short screw (7 to 9 cm): observed"), 8.0, 2.4, True),
            (_("(b) Vis longue (au-delà de 12 cm) : hypothèse", "(b) Long screw (beyond 12 cm): hypothesis"),
             16.0, 2.4, False))):
        face, y0, r = _cone_et_filet(ax, L, prof_cone, visible, _)
        ax.annotate("", xy=(face + 1.5, y0 + r), xytext=(face + 1.5, y0),
                    arrowprops=dict(arrowstyle="<->", color=ENCRE_2, lw=0.9))
        if visible:
            texte(ax, face + 1.9, y0 + r + 0.8, _("rayon ≈ 4 cm\n(mesuré au réglet)", "radius ≈ 4 cm\n(measured with a rule)"),
                  fontsize=7.8)
            texte(ax, 0.6, 21.0, _("cône de bauge arraché, peu profond :\npente bien plus faible que 45° (à l'œil)",
                                   "torn-out cone of cob, shallow:\nslope well under 45° (by eye)"), fontsize=7.8)
            texte(ax, 0.6, 7.0, _("au-delà, le filet glisse\ndans la bauge", "beyond it, the thread slides\nin the cob"),
                  fontsize=7.8, color=SERIES[0])
        else:
            texte(ax, face + 1.9, y0 + r + 0.8, _("cône peut-être toujours là,\ninvisible (A4 sonnait creux\nsur 8 cm de rayon)",
                                                  "cone perhaps still there,\ninvisible (A4 sounded hollow\nover an 8 cm radius)"),
                  fontsize=7.6)
            texte(ax, 0.6, 21.0, _("le cône ne grandit plus…", "the cone stops growing…"), fontsize=7.8)
            texte(ax, 0.6, 7.0, _("…et chaque cm de filet en plus\najoute une part à peu près fixe",
                                  "…and each extra cm of thread\nadds a roughly fixed share"), fontsize=7.8, color=SERIES[0])
        ax.set_title(titre, loc="left", fontsize=9.5)
        ax.set_xlim(0, 30)
        ax.set_ylim(6, 24)
        ax.set_aspect("equal")
        ax.axis("off")
    fig.text(0.01, 0.01, _("Coupe, cotes approximatives. Mesuré : charge qui fait céder une Ø10 ≈ 10 kg par cm de vis à "
                           "7 cm, 19 kg par cm à 11,5 cm : elle croît plus vite\nque la longueur. (b) est l'hypothèse de "
                           "l'auteur, non vérifiée : un cône qui grandirait sans fin décrit les quatre ruptures aussi bien.",
                           "Section, approximate dimensions. Measured: load at which a Ø10 gives way ≈ 10 kg per cm of "
                           "screw at 7 cm, 19 kg per cm at 11.5 cm: it grows faster\nthan length. (b) is the author's "
                           "hypothesis, not checked: a cone that kept growing describes the four failures just as well."),
             fontsize=7.6, color=ENCRE_2)
    fig.tight_layout(rect=(0, 0.1, 1, 1))
    enregistrer(fig, "fig_cone", lang)


if __name__ == "__main__":
    for langue in langues():
        fig_implantation(langue)
        fig_montage(langue)
        fig_theorie(langue)
        fig_platine(langue)
        fig_cone(langue)
