"""Style commun des figures, langue des libellés, enregistrement en PNG (.docx) et SVG (site) ; module partagé par code/."""

# Langue : chaque script de figures produit les deux versions, figures/<id>.png/.svg (libellés en français) et
# figures/<id>_en.png/.svg (en anglais) ; « --langue fr » ou « --langue en » n'en produit qu'une.

import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from lecture import FIGURES  # noqa: E402

# Palette catégorielle (ordre fixe, jamais recyclé) ; textes en encre neutre, jamais à la couleur d'une série.
SERIES = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6", "#e34948"]
ENCRE, ENCRE_2, ENCRE_3 = "#0b0b0b", "#52514e", "#8a8984"
GRILLE = "#e4e3df"
FOND = "#fcfcfb"
BAUGE, BAUGE_TRAIT = "#e8dcc2", "#a08a63"
BOIS, ACIER, CORDE = "#c99a5b", "#7d8590", "#6b6b6b"

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 10, "axes.edgecolor": ENCRE_3, "axes.labelcolor": ENCRE_2,
    "xtick.color": ENCRE_2, "ytick.color": ENCRE_2, "axes.grid": True, "grid.color": GRILLE, "grid.linewidth": 0.8,
    "axes.spines.top": False, "axes.spines.right": False, "lines.linewidth": 2, "figure.facecolor": FOND,
    "axes.facecolor": FOND, "savefig.facecolor": FOND, "svg.fonttype": "none", "svg.hashsalt": "vis-dans-la-bauge",
    "legend.frameon": False, "axes.titleweight": "bold", "axes.titlesize": 11, "axes.titlecolor": ENCRE,
})


LANGUES = ("fr", "en")


def langues():
    """Langues à produire : celle de « --langue fr|en » sur la ligne de commande, sinon les deux."""
    if "--langue" not in sys.argv:
        return LANGUES
    i = sys.argv.index("--langue")
    lang = sys.argv[i + 1] if i + 1 < len(sys.argv) else ""
    if lang not in LANGUES:
        sys.exit("usage : --langue fr  ou  --langue en  (sans l'option : les deux)")
    return (lang,)


def traducteur(lang):
    """Fonction _(français, anglais) qui rend le libellé de la langue demandée."""
    return lambda fr, en: fr if lang == "fr" else en


def nombre(x, lang, fmt="g"):
    """Nombre écrit à la française (virgule décimale) ou à l'anglaise (point)."""
    t = format(x, fmt)
    return t.replace(".", ",") if lang == "fr" else t


def enregistrer(fig, ident, lang="fr"):
    """Écrit figures/<ident>.png (200 dpi) et .svg, suffixe _en pour l'anglais, sans métadonnées de date ni de logiciel."""
    FIGURES.mkdir(exist_ok=True)
    nom = ident if lang == "fr" else f"{ident}_{lang}"
    fig.savefig(FIGURES / f"{nom}.png", dpi=200, bbox_inches="tight", metadata={"Software": None})
    fig.savefig(FIGURES / f"{nom}.svg", bbox_inches="tight", metadata={"Date": None, "Creator": None})
    plt.close(fig)
    print(f"figures/{nom}.png, .svg")
