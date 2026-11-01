"""Change le nom du dépôt AVANT sa création sur GitHub : outils/publication.conf, puis les adresses écrites dans les textes."""

# Usage, depuis la racine du dépôt : python3 outils/renommer.py <nouveau-nom>   (ou : make renommer NOM=<nouveau-nom>)
# Remplace github.com/<compte>/<ancien> et <compte>.github.io/<ancien> par le nouveau nom dans tous les fichiers texte
# publiés (README, papiers, pages du site…), sauf docs/ (refait par make construire). Affiche chaque fichier modifié.
# Refuse si le dépôt a déjà un « origin » : après la création, renommer d'abord sur GitHub (voir la procédure).
# Ensuite : make construire, puis make verifier.

import pathlib
import re
import subprocess
import sys

sys.dont_write_bytecode = True   # aucun __pycache__ dans le dépôt
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import publication as pub  # noqa: E402
from verifier_publication import fichiers_publies  # noqa: E402

TEXTE = {".md", ".txt", ".csv", ".json", ".toml", ".cff", ".py", ".sh", ".lua", ".html", ".css", ".yml", ".yaml"}


def main():
    if len(sys.argv) != 2 or not re.fullmatch(r"[A-Za-z0-9._-]+", sys.argv[1]):
        sys.exit("usage : python3 outils/renommer.py <nouveau-nom>   (lettres, chiffres, « - », « _ », « . »)")
    nouveau, ancien = sys.argv[1], pub.NOM
    if nouveau == ancien:
        sys.exit(f"le dépôt s'appelle déjà « {ancien} » : rien à faire")
    if (pub.RACINE / ".git").exists():
        r = subprocess.run(["git", "-C", str(pub.RACINE), "remote", "get-url", "origin"], capture_output=True, text=True)
        if r.returncode == 0:
            sys.exit(f"le dépôt a déjà un « origin » ({r.stdout.strip()}) : il existe sur GitHub. Le renommer d'abord "
                     "là-bas (gh repo rename), puis relancer ce script. Voir outils/README.md.")
    motifs = [(re.compile(rf"github\.com/{re.escape(pub.COMPTE)}/{re.escape(ancien)}(?![A-Za-z0-9._-])", re.I),
               f"github.com/{pub.COMPTE}/{nouveau}"),
              (re.compile(rf"{re.escape(pub.COMPTE.lower())}\.github\.io/{re.escape(ancien)}(?![A-Za-z0-9._-])"),
               f"{pub.COMPTE.lower()}.github.io/{nouveau}")]
    modifies = []
    for f in fichiers_publies():
        rel = f.relative_to(pub.RACINE).as_posix()
        if rel.startswith("docs/") or (f.suffix.lower() not in TEXTE and f.name != "Makefile"):
            continue
        texte = f.read_text(encoding="utf-8")
        neuf = texte
        for rx, rempl in motifs:
            neuf = rx.sub(rempl, neuf)
        if neuf != texte:
            f.write_text(neuf, encoding="utf-8")
            modifies.append(rel)
    conf = pub.CONF.read_text(encoding="utf-8")
    pub.CONF.write_text(re.sub(r"(?m)^NOM_DEPOT=.*$", f"NOM_DEPOT={nouveau}", conf), encoding="utf-8")
    print(f"Nom du dépôt : {ancien} → {nouveau} (outils/publication.conf)")
    print(f"Adresses réécrites dans {len(modifies)} fichier(s) :")
    for m in modifies:
        print(f"  {m}")
    print("Ensuite : make construire, puis make verifier.")


if __name__ == "__main__":
    main()
