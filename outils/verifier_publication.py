"""Contrôle de confidentialité et de cohérence du dépôt avant toute publication ; code de retour 1 si un contrôle échoue."""

# Usage, depuis la racine du dépôt : python3 outils/verifier_publication.py   (ou : make verifier)
#
# Contrôle les fichiers qui partiraient sur GitHub (ceux que git n'ignore pas), leur contenu ET leur nom :
# - types de fichiers : liste blanche d'extensions ; tout fichier PDF (repéré par son contenu, quelle que soit son
#   extension) hors des PDF exportés du papier ; fichiers de plus de 10 Mo ;
# - confidentialité : chemins absolus et chemins du dossier de travail, adresses e-mail (même masquées), numéros de
#   téléphone, coordonnées GPS écrites en texte, et la liste locale outils/termes_interdits.txt (noms des autres
#   personnes et entreprises, adresse et cadastre du bien, montants, dossiers du projet), jamais publiée ;
# - contenu caché : textes illisibles en UTF-8 (lus quand même), fichiers Office et OpenDocument (zip) ouverts et lus,
#   chaînes de caractères des fichiers binaires, métadonnées des images (EXIF, GPS, XMP, commentaires) ;
# - cohérence : espaces réservés non remplis, marqueurs internes, commentaires HTML, adresse du dépôt conforme à
#   outils/publication.conf, liens internes du site, site construit à jour, métadonnées Zenodo et citation.
# Avertissements (à lire, ne bloquent pas) : montants en euros, nombres à quatre décimales ou plus.
# La seule adresse e-mail permise est celle de la clé CONTACT de outils/publication.conf, si elle est remplie.
# Aucune action distante, aucune écriture. Ce fichier est lui-même contrôlé, sauf le bloc des motifs ci-dessous.

import codecs
import html.parser
import io
import json
import pathlib
import re
import subprocess
import sys
import unicodedata
import zipfile

sys.dont_write_bytecode = True   # aucun __pycache__ dans le dépôt
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import publication as pub  # noqa: E402

RACINE = pub.RACINE
CONTACT = pub.lire_conf().get("CONTACT", "").strip()
TAILLE_MAX = 10 * 1024 * 1024
TERMES = RACINE / "outils" / "termes_interdits.txt"

# Liste blanche : ce que le dépôt publie. Toute autre extension fait échouer le contrôle (la convertir ou l'ajouter ici
# en connaissance de cause).
EXT_TEXTE = {".md", ".txt", ".csv", ".json", ".toml", ".cff", ".py", ".sh", ".lua", ".html", ".css", ".svg", ".yml",
             ".yaml", ".conf"}
EXT_IMAGES = {".jpg", ".jpeg", ".png"}
EXT_OFFICE = {".docx"}
SANS_EXTENSION = {"Makefile", "LICENSE", "LICENSE-code", ".gitignore", ".nojekyll"}
PDF_PERMIS = (re.compile(r"^[^/]+/papier/pdf/[^/]+\.pdf$"), re.compile(r"^docs/[^/]+/telechargements/[^/]+\.pdf$"))
INFO_PERMISE = {"dpi", "gamma", "transparency", "srgb", "progressive", "progression", "jfif", "jfif_version",
                "jfif_unit", "jfif_density", "adobe", "adobe_transform", "aspect", "interlace", "duration", "loop",
                "background", "version", "optimize"}
ATTENDUS = ("README.md", "LICENSE", "LICENSE-code", "CITATION.cff", ".zenodo.json", ".gitignore", "Makefile",
            "docs/index.html", "docs/en/index.html", "docs/.nojekyll", "outils/publication.conf")

# <motifs> — lignes non contrôlées dans ce fichier (elles écrivent ce que le contrôle cherche) ; aucun nom propre ici.
ABSOLU = re.compile(r"(/Users/|/home/|/private/|/Volumes/|/tmp/|[A-Za-z]:\\\\|GoogleDrive|CloudStorage|"
                    r"\.shortcut-targets|(?<![\w.])~/|\$HOME/|file://)")
CHEMIN_PROJET = re.compile(r"(?<![\w./-])\d_[A-Za-z][\w-]*/")
EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
EMAIL_MASQUE = re.compile(r"[\w.+-]+\s*[\[({<]\s*(?:at|arobase|chez)\s*[\])}>]\s*[\w-]+(?:\s*[\[({<]\s*(?:dot|point)"
                          r"\s*[\])}>]\s*\w+|\.\w+)", re.I)
TELEPHONE = re.compile(r"(?<![\d.,])(?:\+33 ?|0033 ?|0)[1-9](?:[ .-]?\d{2}){4}(?![\d.,])")
GPS = re.compile(r"(?<![\d.,])-?\d{1,2}[.,]\d{4,}\s*°?\s*(?:[NS]\s*[,;/]?|[,;/])\s*-?\d{1,3}[.,]\d{4,}")
GPS_DMS = re.compile(r"\d{1,3}\s*°\s*\d{1,2}\s*['′’]\s*(?:\d{1,2}(?:[.,]\d+)?\s*[\"″”]\s*)?[NSEOW]\b")
RESERVE = re.compile(r"\[[^\]\n]{0,60}(?:à compléter|a completer|to be completed|à remplir|to be filled|TODO|TBD)"
                     r"[^\]\n]{0,60}\]", re.I)
MONTANT = re.compile(r"€|\bk€|\bEUR\b")
DECIMALES = re.compile(r"(?<![\w.])\d+[.,](?!0+\b)\d{4,}(?![\d/])")
MARQUEURS = ("【U】", "【C】")
C_MARQUEURS = "Marqueurs internes du projet (【U】, 【C】)"
VOCABULAIRE = (("load cell", "« crane scale » partout pour le peson"), ("années 1950", "« au moins 50 ans »"),
               ("1950s", "« at least 50 years old »"))
# </motifs>
DEBUT_MOTIFS, FIN_MOTIFS = "# <" + "motifs>", "# </" + "motifs>"
COMMENTAIRE = re.compile(r"<!--(.*?)-->", re.S)
CHEMIN_DANS_COMMENTAIRE = re.compile(r"[\w.-]+/[\w.-]+|\\|\.(md|docx|xlsx|py|pdf|json|csv)\b")
GITHUB = re.compile(r"github\.com/([A-Za-z0-9-]+)/([A-Za-z0-9._-]+)")
PAGES = re.compile(r"([a-z0-9-]+)\.github\.io/([A-Za-z0-9._-]+)")

C_TYPES = "Types de fichiers (liste blanche d'extensions)"
C_NOMS = "Noms d'autres personnes, entreprises, adresse du bien, montants"
C_CHEMINS = "Chemins internes du dossier de projet"
C_ILLISIBLE = "Textes illisibles en UTF-8"


# ------------------------------------------------------------------------------------------------- les résultats
class Rapport:
    def __init__(self):
        self.controles = {}   # nom -> (gravité, [constats])

    def declarer(self, nom, gravite="ERREUR"):
        self.controles.setdefault(nom, (gravite, []))

    def ajouter(self, nom, ou, quoi):
        self.controles[nom][1].append((ou, quoi))

    def afficher(self):
        erreurs = avert = 0
        for nom, (gravite, constats) in self.controles.items():
            if not constats:
                print(f"[OK]        {nom}")
                continue
            if gravite == "ERREUR":
                erreurs += 1
                print(f"[ÉCHEC]     {nom} : {len(constats)}")
            else:
                avert += 1
                print(f"[ATTENTION] {nom} : {len(constats)}")
            for ou, quoi in constats[:25]:
                print(f"            {ou}  {quoi}")
            if len(constats) > 25:
                print(f"            … et {len(constats) - 25} de plus")
        print()
        if erreurs:
            print(f"Résultat : ÉCHEC — {erreurs} contrôle(s) en échec, {avert} avertissement(s). "
                  "Ne rien publier avant correction.")
        else:
            print(f"Résultat : OK — aucun contrôle en échec, {avert} avertissement(s) à lire.")
        return erreurs


# --------------------------------------------------------------------------------------------- fichiers publiés
def fichiers_publies():
    """Les fichiers que git publierait : git ls-files s'il y a un dépôt git, sinon parcours avec .gitignore."""
    if (RACINE / ".git").exists():
        r = subprocess.run(["git", "-C", str(RACINE), "ls-files", "-co", "--exclude-standard", "-z"],
                           capture_output=True, text=True, check=True)
        return sorted(RACINE / p for p in r.stdout.split("\0") if p and (RACINE / p).is_file())
    motifs = []
    gi = RACINE / ".gitignore"
    if gi.exists():
        motifs = [l.strip() for l in gi.read_text(encoding="utf-8").splitlines()
                  if l.strip() and not l.startswith("#")]
    def ignore(rel):
        parties = rel.split("/")
        for m in motifs:
            if m.endswith("/") and m[:-1] in parties[:-1]:
                return True
            if "/" in m.rstrip("/") and pathlib.PurePosixPath(rel).match(m):
                return True
            if "/" not in m and any(pathlib.PurePosixPath(p).match(m) for p in parties):
                return True
        return False
    return sorted(p for p in RACINE.rglob("*") if p.is_file() and ".git" not in p.relative_to(RACINE).parts
                  and not ignore(p.relative_to(RACINE).as_posix()))


def normaliser(t):
    """Sans accents et en minuscules : la forme sur laquelle se cherchent les termes interdits."""
    return "".join(c for c in unicodedata.normalize("NFKD", t) if not unicodedata.combining(c)).lower()


class Termes:
    """La liste locale outils/termes_interdits.txt, en trois sections : [noms], [motifs], [chemins]."""

    def __init__(self, rapport):
        self.noms, self.motifs, self.chemins = [], [], []
        if not TERMES.exists():
            rapport.ajouter(C_NOMS, "outils/termes_interdits.txt",
                            "liste absente : contrôle impossible (la recréer, voir outils/README.md)")
            return
        section = "noms"
        for no, brut in enumerate(TERMES.read_text(encoding="utf-8").splitlines(), 1):
            l = brut.strip()
            if not l or l.startswith("#"):
                continue
            m = re.fullmatch(r"\[(noms|motifs|chemins)\]", l)
            if m:
                section = m.group(1)
                continue
            if section == "noms":
                mots = [re.escape(normaliser(p)) for p in re.split(r"[\s_.\-]+", l) if p]
                self.noms.append((l, re.compile(r"(?<![a-z0-9])" + r"[\s_.\-]*".join(mots) + r"(?![a-z0-9])")))
            elif section == "motifs":
                try:
                    self.motifs.append((f"motif l. {no}", re.compile(l, re.I)))
                except re.error as e:
                    rapport.ajouter(C_NOMS, f"outils/termes_interdits.txt:{no}", f"motif illisible ({e})")
            else:
                self.chemins.append(normaliser(l))

    def chercher(self, texte):
        """(contrôle, terme trouvé) pour chaque terme de la liste présent dans le texte."""
        n = normaliser(texte)
        for t, rx in self.noms:
            if rx.search(n):
                yield C_NOMS, t
        for t, rx in self.motifs:
            if rx.search(n):
                yield C_NOMS, t
        for t in self.chemins:
            if t in n:
                yield C_CHEMINS, t


# ------------------------------------------------------------------------------------------------ lecture des fichiers
def decoder(octets):
    """Texte d'un fichier, et la raison s'il n'est pas en UTF-8 (lu alors en UTF-16 ou en Windows-1252)."""
    if octets.startswith(codecs.BOM_UTF16_LE) or octets.startswith(codecs.BOM_UTF16_BE):
        return octets.decode("utf-16", "replace"), "UTF-16"
    try:
        return octets.decode("utf-8-sig"), None
    except UnicodeDecodeError:
        return octets.decode("cp1252", "replace"), "ni UTF-8 ni UTF-16 (lu en Windows-1252)"


def chaines(octets):
    """Chaînes lisibles d'un fichier binaire (comme la commande strings), pour y chercher les termes."""
    return [m.group(0).decode("latin-1") for m in re.finditer(rb"[\x20-\x7e\xa0-\xff]{4,}", octets)]


def lire_zip(octets):
    """Texte des fichiers XML d'un zip Office ou OpenDocument, par paragraphe ; noms des parties ; images embarquées."""
    lignes, images = [], []
    with zipfile.ZipFile(io.BytesIO(octets)) as z:
        for nom in z.namelist():
            lignes.append((f"{nom} (nom de partie)", nom))
            contenu = z.read(nom)
            if re.search(r"\.(png|jpe?g|gif|tiff?|bmp|webp|emf|wmf)$", nom, re.I):
                images.append((nom, contenu))
            elif re.search(r"\.(xml|rels|txt|csv|json|html?)$", nom, re.I) or "." not in nom.rsplit("/", 1)[-1]:
                brut, _ = decoder(contenu)
                brut = re.sub(r"</(w:p|text:p|text:h|a:p|si|row|table:table-row)>", "\n", brut)
                brut = re.sub(r"<[^>]+>", " ", brut)
                for i, l in enumerate(brut.splitlines(), 1):
                    if l.strip():
                        lignes.append((f"{nom}:{i}", l))
            else:
                lignes += [(f"{nom} (binaire)", s) for s in chaines(contenu)]
    return lignes, images


# ------------------------------------------------------------------------------------------------ contrôles texte
def controler_texte(rapport, rel, lignes, termes, svg=False):
    for ou, l in lignes:
        lieu = f"{rel}:{ou}"
        for m in ABSOLU.finditer(l):
            rapport.ajouter("Chemins absolus", lieu, f"« {l[max(0, m.start() - 20):m.end() + 30].strip()} »")
        for m in CHEMIN_PROJET.finditer(l):
            rapport.ajouter(C_CHEMINS, lieu, f"« {l[m.start():m.end() + 30].strip()} »")
        for m in EMAIL.finditer(l):
            adr = m.group(0)
            if adr.endswith("users.noreply.github.com") or (CONTACT and adr.lower() == CONTACT.lower()):
                continue   # adresse anonyme de GitHub ; adresse de contact choisie par l'auteur (publication.conf)
            rapport.ajouter("Adresses e-mail", lieu, f"« {adr} »")
        for m in EMAIL_MASQUE.finditer(l):
            rapport.ajouter("Adresses e-mail", lieu, f"« {m.group(0)} » (adresse masquée)")
        for m in TELEPHONE.finditer(l):
            rapport.ajouter("Numéros de téléphone", lieu, f"« {m.group(0)} »")
        if not svg:   # les SVG et CSS portent des coordonnées de dessin, pas des positions
            for rx in (GPS, GPS_DMS):
                for m in rx.finditer(l):
                    rapport.ajouter("Coordonnées GPS écrites en texte", lieu, f"« {m.group(0)} »")
            for m in DECIMALES.finditer(l):
                rapport.ajouter("Nombres à quatre décimales ou plus (coordonnées ?)", lieu, f"« {m.group(0)} »")
        for m in MONTANT.finditer(l):
            rapport.ajouter("Montants en euros", lieu, f"« {l[max(0, m.start() - 25):m.end() + 5].strip()} »")
        for m in RESERVE.finditer(l):
            rapport.ajouter("Espaces réservés non remplis", lieu, f"« {m.group(0)} »")
        if termes:
            for controle, t in termes.chercher(l):
                rapport.ajouter(controle, lieu, f"« {t} »")
        for t in MARQUEURS:
            if t in l:
                rapport.ajouter(C_MARQUEURS, lieu, f"« {t} »")
        for m in GITHUB.finditer(l):
            compte, nom = m.group(1), re.sub(r"\.git$", "", m.group(2).rstrip("."))
            if compte.lower() == pub.COMPTE.lower() and nom != pub.NOM:
                rapport.ajouter("Adresse du dépôt conforme à outils/publication.conf", lieu,
                                f"« github.com/{compte}/{nom} » au lieu de « {pub.NOM} »")
        for m in PAGES.finditer(l):
            if m.group(1) == pub.COMPTE.lower() and (m.group(2) != pub.NOM or pub.DOMAINE != m.group(0).split("/")[0]):
                rapport.ajouter("Adresse du dépôt conforme à outils/publication.conf", lieu,
                                f"« {m.group(0)} » au lieu de « {pub.DOMAINE}/{pub.NOM} »")
        for t, consigne in VOCABULAIRE:
            if t in l:
                rapport.ajouter("Vocabulaire harmonisé (peson, âge du mur)", lieu, f"« {t} » : {consigne}")


def controler_nom_de_fichier(rapport, rel, termes):
    """Le chemin du fichier lui-même : noms, chemins du projet."""
    lieu = f"{rel} (nom du fichier)"
    if termes:
        for controle, t in termes.chercher(rel):
            rapport.ajouter(controle, lieu, f"« {t} »")
    if CHEMIN_PROJET.search(rel):
        rapport.ajouter(C_CHEMINS, lieu, "dossier numéroté du dossier de projet")


def controler_commentaires(rapport, rel, texte, est_site):
    for m in COMMENTAIRE.finditer(texte):
        contenu = " ".join(m.group(1).split())
        ligne = texte.count("\n", 0, m.start()) + 1
        if CHEMIN_DANS_COMMENTAIRE.search(contenu):
            rapport.ajouter("Commentaires HTML qui citent un chemin", f"{rel}:{ligne}", f"« <!-- {contenu[:80]} --> »")
        elif est_site:
            rapport.ajouter("Commentaires de travail visibles dans le code du site", f"{rel}:{ligne}",
                            f"« <!-- {contenu[:80]} --> »")


def lignes_a_controler(rel, texte):
    """Lignes numérotées d'un texte ; dans ce script, le bloc des motifs est sauté (il écrit ce que l'on cherche)."""
    lignes, dedans = [], False
    for i, l in enumerate(texte.splitlines(), 1):
        if rel == "outils/verifier_publication.py":
            if l.startswith(DEBUT_MOTIFS):
                dedans = True
            if dedans:
                if l.startswith(FIN_MOTIFS):
                    dedans = False
                continue
        lignes.append((str(i), l))
    return lignes


# ---------------------------------------------------------------------------------------------- contrôles images
def controler_image(rapport, rel, source):
    from PIL import Image
    try:
        with Image.open(source) as im:
            exif = im.getexif()
            if len(exif):
                gps = exif.get_ifd(0x8825)
                rapport.ajouter("Métadonnées des images (EXIF, GPS, XMP)", rel,
                                f"EXIF présent ({len(exif)} champs{', dont position GPS' if gps else ''})")
            autres = sorted(k for k in im.info if k.lower() not in INFO_PERMISE and k != "icc_profile")
            if autres:
                rapport.ajouter("Métadonnées des images (EXIF, GPS, XMP)", rel, f"métadonnées : {', '.join(autres)}")
    except Exception as e:  # noqa: BLE001
        rapport.ajouter("Métadonnées des images (EXIF, GPS, XMP)", rel, f"illisible, non contrôlée ({e.__class__.__name__})")


# ----------------------------------------------------------------------------------------------- liens du site
class Liens(html.parser.HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.liens, self.titre, self.lang, self._dans_titre = [], "", None, False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "html":
            self.lang = a.get("lang")
        if tag == "title":
            self._dans_titre = True
        for cle in ("href", "src"):
            if a.get(cle):
                self.liens.append(a[cle])

    def handle_endtag(self, tag):
        if tag == "title":
            self._dans_titre = False

    def handle_data(self, data):
        if self._dans_titre:
            self.titre += data


def controler_site(rapport):
    docs = RACINE / "docs"
    for page in sorted(docs.rglob("*.html")):
        rel = page.relative_to(RACINE).as_posix()
        p = Liens()
        p.feed(page.read_text(encoding="utf-8"))
        p.close()
        if not p.titre.strip() or not p.lang:
            rapport.ajouter("Pages du site lisibles (titre, langue)", rel, "titre ou attribut lang manquant")
        for lien in p.liens:
            if re.match(r"^(https?:|mailto:|#|data:)", lien):
                continue
            cible = (page.parent / lien.split("#")[0].split("?")[0]).resolve()
            if cible.is_dir():
                cible = cible / "index.html"
            if not cible.exists() or docs.resolve() not in cible.parents and cible != docs.resolve():
                rapport.ajouter("Liens internes du site", rel, f"« {lien} » ne mène à aucun fichier de docs/")


def controler_a_jour(rapport, liste):
    """Toute source du site (site/, outils de construction, configuration, fichiers des sujets, code compris) doit être
    plus ancienne que la plus ancienne page construite."""
    pages = list((RACINE / "docs").rglob("*.html"))
    if not pages:
        rapport.ajouter("Site construit à jour (make construire)", "docs/", "aucune page : lancer make construire")
        return
    plus_ancienne = min(p.stat().st_mtime for p in pages)
    sources = [*(RACINE / "site").rglob("*"), RACINE / "outils" / "construire.py", RACINE / "outils" / "publication.conf"]
    for f in liste:
        rel = f.relative_to(RACINE).parts
        if len(rel) > 1 and (RACINE / rel[0] / "sujet.toml").exists():
            sources.append(f)
    for s in sources:
        if s.is_file() and s.name != ".DS_Store" and s.stat().st_mtime > plus_ancienne + 1:
            rapport.ajouter("Site construit à jour (make construire)", s.relative_to(RACINE).as_posix(),
                            "modifié après la dernière construction : relancer make construire")


# ------------------------------------------------------------------------------------------------------------ main
def main():
    rapport = Rapport()
    for nom in ("Fichiers attendus", C_TYPES, "Fichiers de plus de 10 Mo", "PDF",
                "Métadonnées des images (EXIF, GPS, XMP)", C_ILLISIBLE, "Chemins absolus", "Adresses e-mail",
                "Numéros de téléphone", "Coordonnées GPS écrites en texte", C_NOMS, C_CHEMINS,
                "Espaces réservés non remplis", C_MARQUEURS,
                "Commentaires HTML qui citent un chemin", "Adresse du dépôt conforme à outils/publication.conf",
                "Liens internes du site", "Pages du site lisibles (titre, langue)", "Site construit à jour (make construire)",
                "Métadonnées Zenodo et citation lisibles"):
        rapport.declarer(nom)
    for nom in ("Montants en euros", "Nombres à quatre décimales ou plus (coordonnées ?)",
                "Commentaires de travail visibles dans le code du site", "Vocabulaire harmonisé (peson, âge du mur)",
                "PDF exportés du papier (à vérifier)"):
        rapport.declarer(nom, "ATTENTION")
    termes = Termes(rapport)
    liste = fichiers_publies()
    n = {"texte": 0, "image": 0, "docx": 0, "autre": 0}

    for a in ATTENDUS:
        if not (RACINE / a).exists():
            rapport.ajouter("Fichiers attendus", a, "absent")
    try:
        json.loads((RACINE / ".zenodo.json").read_text(encoding="utf-8"))
        cff = (RACINE / "CITATION.cff").read_text(encoding="utf-8")
        if "cff-version" not in cff or "title:" not in cff:
            rapport.ajouter("Métadonnées Zenodo et citation lisibles", "CITATION.cff", "champs cff-version ou title absents")
    except (OSError, ValueError) as e:
        rapport.ajouter("Métadonnées Zenodo et citation lisibles", ".zenodo.json / CITATION.cff", str(e))

    for f in liste:
        rel = f.relative_to(RACINE).as_posix()
        ext = f.suffix.lower()
        est_site = rel.startswith("docs/")
        octets = f.read_bytes()
        controler_nom_de_fichier(rapport, rel, termes)
        if len(octets) > TAILLE_MAX:
            rapport.ajouter("Fichiers de plus de 10 Mo", rel, f"{len(octets) / 1e6:.1f} Mo")
        connue = ext in EXT_TEXTE | EXT_IMAGES | EXT_OFFICE or f.name in SANS_EXTENSION
        # PDF : repéré par son contenu, quelle que soit l'extension
        if octets.lstrip()[:5] == b"%PDF-" or ext == ".pdf":
            n["autre"] += 1
            if ext == ".pdf" and any(rx.match(rel) for rx in PDF_PERMIS):
                rapport.ajouter("PDF exportés du papier (à vérifier)", rel, "vérifier que c'est bien l'export du papier")
            else:
                rapport.ajouter("PDF", rel, "PDF hors des exports du papier (<sujet>/papier/pdf/) : références seulement")
            controler_texte(rapport, rel, [("chaînes", s) for s in chaines(octets)], termes)
            continue
        if not connue:
            rapport.ajouter(C_TYPES, rel, f"extension « {ext or f.name} » non prévue : la convertir, ou l'ajouter à "
                            "la liste blanche de outils/verifier_publication.py en connaissance de cause")
        # zip Office ou OpenDocument : ouvert et lu, quelle que soit l'extension
        if octets[:4] == b"PK\x03\x04":
            try:
                lignes, images = lire_zip(octets)
            except zipfile.BadZipFile:
                lignes, images = [("binaire", s) for s in chaines(octets)], []
            n["docx" if ext == ".docx" else "autre"] += 1
            controler_texte(rapport, rel, lignes, termes)
            for nom, contenu in images:
                controler_image(rapport, f"{rel}!{nom}", io.BytesIO(contenu))
            continue
        if ext in EXT_IMAGES or octets[:4] in (b"\x89PNG", b"RIFF", b"GIF8") or octets[:3] == b"\xff\xd8\xff":
            n["image"] += 1
            controler_image(rapport, rel, io.BytesIO(octets))
            continue
        if b"\x00" in octets[:4096] and not octets.startswith((codecs.BOM_UTF16_LE, codecs.BOM_UTF16_BE)):
            n["autre"] += 1
            controler_texte(rapport, rel, [("chaînes", s) for s in chaines(octets)], termes)
            continue
        texte, probleme = decoder(octets)
        if probleme:
            rapport.ajouter(C_ILLISIBLE, rel, f"{probleme} : le réenregistrer en UTF-8")
        n["texte" if connue else "autre"] += 1
        controler_texte(rapport, rel, lignes_a_controler(rel, texte), termes, svg=ext in (".svg", ".css"))
        if ext in (".md", ".html", ".htm"):
            controler_commentaires(rapport, rel, texte, est_site)

    controler_site(rapport)
    controler_a_jour(rapport, liste)

    print(f"Contrôle de publication — dépôt {pub.DEPOT}\n                          site  {pub.SITE}")
    print(f"Fichiers qui partiraient sur GitHub : {len(liste)} ({n['texte']} textes, {n['image']} images, "
          f"{n['docx']} .docx, {n['autre']} autres)"
          f"{'' if (RACINE / '.git').exists() else ' — pas encore de dépôt git : liste tirée de .gitignore'}")
    print(f"Contact publié : {CONTACT or 'aucun (les issues GitHub seules)'}\n")
    sys.exit(1 if rapport.afficher() else 0)


if __name__ == "__main__":
    main()
