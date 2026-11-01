"""Prépare les photos publiées d'un sujet : réduites à 1600 px, redressées, toutes métadonnées retirées (EXIF, GPS, XMP, ICC)."""

# Usage, depuis la racine du dépôt :
#   python3 outils/preparer_photos.py <sujet> <dossier d'originaux> [<dossier d'originaux> ...]
#   ex. : python3 outils/preparer_photos.py vis-dans-la-bauge <originaux du 30/10/2026> <originaux du 12/10/2026>
# Les originaux ne sont pas dans le dépôt (ils portent la position GPS). La liste des photos retenues et leurs
# légendes sont dans <sujet>/photos/legendes.csv (colonne « original ») ; seules ces photos sont écrites.
# Contrôle ensuite : make verifier (aucune métadonnée ne doit rester).

import csv
import pathlib
import sys

from PIL import Image, ImageOps

RACINE = pathlib.Path(__file__).resolve().parent.parent
COTE_MAX = 1600


def preparer(source, cible):
    with Image.open(source) as im:
        im = ImageOps.exif_transpose(im).convert("RGB")
        im.thumbnail((COTE_MAX, COTE_MAX), Image.LANCZOS)
        propre = Image.new("RGB", im.size)
        propre.paste(im)                                  # copie des pixels seuls : aucune métadonnée ne suit
        propre.save(cible, "JPEG", quality=82, optimize=True, progressive=True)


def main():
    if len(sys.argv) < 3:
        sys.exit("usage : python3 outils/preparer_photos.py <sujet> <dossier d'originaux> [<dossier> ...]")
    photos = RACINE / sys.argv[1] / "photos"
    if not (photos / "legendes.csv").exists():
        sys.exit(f"{photos / 'legendes.csv'} introuvable : le premier argument est le dossier du sujet")
    dossiers = [pathlib.Path(d) for d in sys.argv[2:]]
    with open(photos / "legendes.csv", newline="", encoding="utf-8") as f:
        lignes = list(csv.DictReader(f, delimiter=";"))
    for l in lignes:
        source = next((d / l["original"] for d in dossiers if (d / l["original"]).exists()), None)
        if source is None:
            print(f"introuvable : {l['original']}")
            continue
        preparer(source, photos / l["fichier"])
        print(f"{sys.argv[1]}/photos/{l['fichier']}")


if __name__ == "__main__":
    main()
