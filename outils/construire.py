"""Construit tout depuis les sources : chiffres et figures de chaque sujet, papiers .docx (FR, EN), site statique (docs/), CITATION.cff et .zenodo.json."""

# Usage, depuis la racine du dépôt : python3 outils/construire.py [--sans-code]   (ou : make construire)
#   --sans-code : ne relance pas le code des sujets (figures et chiffres déjà à jour).
# Dépendances : Python 3 avec matplotlib et numpy (code des sujets), Pillow (photos), pandoc (≥ 3). Aucune action
# distante.
# Nom du dépôt et adresses : outils/publication.conf (lu par outils/publication.py). Sujets : dossiers à sujet.toml.
# Un papier est facultatif : sans <sujet>/papier/fr/papier.md (ou en/paper.md), la page du papier dit « en
# préparation » et aucun .docx n'est produit pour cette langue.
# Figures : figures/<id>.png et .svg (libellés en français), figures/<id>_en.png et .svg (en anglais), produites par
# le code du sujet ; les pages anglaises et le papier anglais prennent les secondes.
# PDF du papier : exportés à la main depuis le .docx et rangés dans <sujet>/papier/pdf/ (<sujet>_papier_fr.pdf,
# <sujet>_paper_en.pdf) ; copiés dans docs/<sujet>/telechargements/ à chaque construction (docs/ est vidé à chaque fois).
# Contact : la clé CONTACT de outils/publication.conf (vide = les issues GitHub seules) ; si elle est remplie, elle
# paraît dans le pied de toutes les pages et dans la rubrique « Vos retours » des accueils.
#
# Plan du site produit (docs/, servi tel quel par GitHub Pages) :
#   index.html, en/index.html                     accueil du projet et liste des sujets (FR, EN)
#   <sujet>/{index,papier,donnees,photos}.html   pages du sujet en français ; figures/, photos/, telechargements/
#   en/<sujet>/{index,paper,data,photos}.html    pages du sujet en anglais (les images restent sous <sujet>/)

import csv
import html
import importlib.util
import json
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True   # aucun __pycache__ dans le dépôt
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import publication as pub  # noqa: E402

RACINE = pub.RACINE
DOCS = RACINE / "docs"
SITE = RACINE / "site"
DEPOT, ADRESSE_SITE = pub.DEPOT, pub.SITE

# Champs facultatifs de publication.conf repris dans les métadonnées (vides tant que Rémi ne les a pas remplis).
CONF = pub.lire_conf()
DOI = CONF.get("DOI", "")
ORCID = CONF.get("ORCID", "")
CONTACT = CONF.get("CONTACT", "").strip()


def lien_contact(c):
    """Lien HTML vers le contact choisi par l'auteur : adresse e-mail ou adresse web."""
    cible = c if re.match(r"^https?://", c) else f"mailto:{c}" if "@" in c else c
    return f'<a href="{html.escape(cible)}">{html.escape(c)}</a>'

PROJET = {
    "fr": {"nom": "Rénovation en terre crue", "titre": "Rénover le bâti en terre crue : retours d'expérience",
           "description": "Retours d'expérience d'un particulier sur la rénovation du bâti en terre crue : essais, "
                          "relevés, code et photos."},
    "en": {"nom": "Earth building renovation", "titre": "Renovating earth buildings: field notes",
           "description": "A homeowner's field notes on renovating earth (cob) buildings: tests, readings, code and "
                          "photos."},
}
TITRE_DEPOT = "Rénovation du bâti en terre crue : retours d'expérience / Renovating earth buildings: field notes"
MOTS_CLES = ["earth construction", "cob", "bauge", "earthen construction", "screws", "shear", "renovation"]

LANGUES = {
    "fr": {
        "code": "fr", "autre": "en", "autre_label": "English", "menu": "Menu principal", "sommaire": "Sommaire",
        "pages": {"accueil": "index.html", "papier": "papier.html", "donnees": "donnees.html", "photos": "photos.html"},
        "labels": {"accueil": "Présentation", "papier": "Le papier", "donnees": "Données et code", "photos": "Photos"},
        "papier": ("papier", "fr", "papier.md"), "resume": ("papier", "fr", "resume.md"),
        "docx": "{s}_papier_fr.docx", "pdf": "{s}_papier_fr.pdf", "lang_docx": "fr-FR", "accueil_projet": "Accueil",
        "suffixe_figure": "",
        "licence": "Texte, données, figures et photos : CC BY 4.0. Code : MIT. Rémi Cura, 2026.",
        "retour": f"Retours bienvenus : <a href=\"{DEPOT}/issues\">issues GitHub</a> · "
                  f"<a href=\"{DEPOT}\">dépôt</a>" + (f" · {lien_contact(CONTACT)}" if CONTACT else ""),
        "contact": f" ou écrivez à {lien_contact(CONTACT)}" if CONTACT else "",
        "telecharger": "Télécharger le papier (.docx)", "telecharger_pdf": "Télécharger le papier (.pdf)",
        "lire": "Lire le papier", "voir_donnees": "Données et code",
        "voir_photos": "Photos", "resume_absent": "Le résumé est en préparation.",
        "photos_intro": "Photos des essais, réduites, sans EXIF ni position ; la date de prise de vue figure dans "
                        "chaque légende. Licence CC BY 4.0.",
        "citation": "Rémi Cura (2026). *{titre}.* Dans : *Rénover le bâti en terre crue : retours d'expérience*, "
                    "dépôt de données et de code, {depot}. {doi}",
        "doi_absent": "Identifiant DOI (Zenodo) : à venir.",
    },
    "en": {
        "code": "en", "autre": "fr", "autre_label": "Français", "menu": "Main menu", "sommaire": "Contents",
        "pages": {"accueil": "index.html", "papier": "paper.html", "donnees": "data.html", "photos": "photos.html"},
        "labels": {"accueil": "Overview", "papier": "The paper", "donnees": "Data and code", "photos": "Photos"},
        "papier": ("papier", "en", "paper.md"), "resume": ("papier", "en", "abstract.md"),
        "docx": "{s}_paper_en.docx", "pdf": "{s}_paper_en.pdf", "lang_docx": "en-GB", "accueil_projet": "Home",
        "suffixe_figure": "_en",
        "licence": "Text, data, figures and photos: CC BY 4.0. Code: MIT. Rémi Cura, 2026.",
        "retour": f"Feedback welcome: <a href=\"{DEPOT}/issues\">GitHub issues</a> · "
                  f"<a href=\"{DEPOT}\">repository</a>" + (f" · {lien_contact(CONTACT)}" if CONTACT else ""),
        "contact": f" or write to {lien_contact(CONTACT)}" if CONTACT else "",
        "telecharger": "Download the paper (.docx)", "telecharger_pdf": "Download the paper (.pdf)",
        "lire": "Read the paper", "voir_donnees": "Data and code",
        "voir_photos": "Photos", "resume_absent": "The abstract is in preparation.",
        "photos_intro": "Photos from the tests, resized, with no EXIF data and no location; the date each was taken "
                        "is in its caption. Licence CC BY 4.0.",
        "citation": "Rémi Cura (2026). *{titre}.* In: *Renovating earth buildings: field notes*, data and code "
                    "repository, {depot}. {doi}",
        "doi_absent": "DOI (Zenodo): to come.",
    },
}


def lancer(cmd):
    """Lance une commande depuis la racine ; affiche l'outil et ses fichiers d'entrée et de sortie, en chemins relatifs."""
    def court(c):
        c = str(c)
        if c.startswith(str(RACINE) + "/") and ":" not in c:
            return pathlib.Path(c).relative_to(RACINE).as_posix()
        return pathlib.Path(c).name
    vus = [court(c) for c in cmd if not str(c).startswith("-")]
    fichiers = [v for v in vus[1:] if v.endswith((".md", ".py", ".html", ".docx"))]
    print("  " + " ".join([pathlib.Path(vus[0]).name] + fichiers[:4]))
    subprocess.run(cmd, check=True, cwd=RACINE)


def pandoc(entrees, sortie, meta, format_html=True, toc=False, ressources=()):
    """Appelle pandoc avec le filtre d'images ; meta est écrit dans un fichier YAML (JSON est du YAML valide)."""
    with tempfile.NamedTemporaryFile("w", suffix=".yaml", delete=False, encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False)
        fichier_meta = f.name
    cmd = ["pandoc", *[str(e) for e in entrees], "-f", "markdown", "-o", str(sortie),
           "--lua-filter", str(SITE / "images.lua"), "--metadata-file", fichier_meta]
    if ressources:
        cmd += ["--resource-path", ":".join(str(r) for r in ressources)]
    if format_html:
        cmd += ["--template", str(SITE / "gabarit.html"), "--standalone"]
    else:
        cmd += ["-t", "docx"]
        ref = SITE / "reference.docx"
        if ref.exists():
            cmd += ["--reference-doc", str(ref)]
    if toc:
        cmd += ["--toc", "--toc-depth=2"]
    try:
        lancer(cmd)
    finally:
        pathlib.Path(fichier_meta).unlink()


def remplir(texte, **valeurs):
    for k, v in valeurs.items():
        texte = texte.replace("{{" + k + "}}", v)
    return texte


# ------------------------------------------------------------------------------------------------------ un sujet
class Sujet:
    def __init__(self, dossier, d):
        self.dossier, self.d, self.id = dossier, d, d["id"]

    def chemin(self, lang, cle):
        return self.dossier.joinpath(*LANGUES[lang][cle])

    def a_papier(self, lang):
        return self.chemin(lang, "papier").exists()

    def sources_papier(self, lang):
        """Le papier, suivi de papier/references.md s'il existe et si le papier ne le cite pas déjà par son nom."""
        p = self.chemin(lang, "papier")
        refs = self.dossier / "papier" / "references.md"
        return [p] + ([refs] if refs.exists() and "references.md" not in p.read_text(encoding="utf-8") else [])

    def docx(self, lang):
        return LANGUES[lang]["docx"].format(s=self.id)

    def pdf(self, lang):
        """Le PDF exporté du papier, s'il a été déposé dans <sujet>/papier/pdf/ ; sinon None."""
        f = self.dossier / "papier" / "pdf" / LANGUES[lang]["pdf"].format(s=self.id)
        return f if f.exists() else None

    def titre_papier(self, lang):
        """Le titre écrit dans l'en-tête YAML du papier ; à défaut, le titre du sujet (sujet.toml)."""
        if self.a_papier(lang):
            m = re.search(r'(?m)^title:\s*"?(.*?)"?\s*$', self.chemin(lang, "papier").read_text(encoding="utf-8"))
            if m:
                return m.group(1)
        return self.d[lang]["titre"]

    def resume(self, lang):
        """Le résumé, sans son titre ni sa ligne d'auteur (la page du sujet a déjà les siens)."""
        f = self.chemin(lang, "resume")
        if not f.exists():
            return f"*{LANGUES[lang]['resume_absent']}*"
        lignes = f.read_text(encoding="utf-8").splitlines()
        if lignes and lignes[0].startswith("# "):
            lignes = lignes[1:]
        while lignes and not lignes[0].strip():
            lignes = lignes[1:]
        if lignes and lignes[0].startswith("Rémi Cura"):
            lignes = lignes[1:]
        return "\n".join(lignes).strip() + "\n"

    def tuiles(self, lang):
        module = self.d.get("chiffres")
        if not module:
            return ""
        spec = importlib.util.spec_from_file_location(f"chiffres_{self.id}", self.dossier / "code" / module)
        m = importlib.util.module_from_spec(spec)
        sys.path.insert(0, str(self.dossier / "code"))
        try:
            spec.loader.exec_module(m)
            cases = "".join(f'<div class="chiffre"><span class="valeur">{html.escape(a)}</span>'
                            f'<span class="sens">{html.escape(b)}</span></div>' for a, b in m.tuiles(lang))
        finally:
            sys.path.pop(0)
        return f'<div class="chiffres">\n{cases}\n</div>'


def sujets():
    return [Sujet(dossier, d) for dossier, d in pub.sujets()]


# ------------------------------------------------------------------------------------------------- liens relatifs
def prefixe_racine(lang, dans_sujet):
    """Préfixe qui ramène de la page à docs/."""
    return {("fr", False): "", ("en", False): "../", ("fr", True): "../", ("en", True): "../../"}[(lang, dans_sujet)]


def prefixe_sujet(s, lang):
    """Préfixe qui mène d'une page du sujet au dossier docs/<sujet>/ (figures, photos, téléchargements)."""
    return "" if lang == "fr" else f"../../{s.id}/"


def meta_commune(lang, titre_page, dans_sujet):
    L = LANGUES[lang]
    return {
        "lang": L["code"], "pagetitle": titre_page, "site_nom": PROJET[lang]["nom"],
        "nom_dans_titre": dans_sujet,   # onglet « page · site » ; l'accueil porte déjà le nom du site
        "description": PROJET[lang]["description"], "racine": prefixe_racine(lang, dans_sujet),
        "accueil": "../index.html" if dans_sujet else "index.html",
        "autre_code": L["autre"], "autre_label": L["autre_label"], "menu_label": L["menu"],
        "sommaire_label": L["sommaire"], "pied_licence": L["licence"], "pied_retour": L["retour"],
    }


def meta_sujet(s, lang, cle, titre_page):
    L, A = LANGUES[lang], LANGUES[LANGUES[lang]["autre"]]
    m = meta_commune(lang, titre_page, True)
    m["autre_langue"] = (f"../en/{s.id}/" if lang == "fr" else f"../../{s.id}/") + A["pages"][cle]
    m["nav"] = [{"href": L["pages"][k], "label": L["labels"][k], **({"actif": True} if k == cle else {})}
                for k in ("accueil", "papier", "donnees", "photos")]
    m["fil"] = s.d[lang]["titre"]
    m["fil_accueil"] = L["accueil_projet"]
    m["prefixe_sujet"] = prefixe_sujet(s, lang)
    m["lien_references"] = f"{DEPOT}/blob/main/{s.id}/papier/references.md"
    return m


# --------------------------------------------------------------------------------------------------------- étapes
def etape_code(liste):
    print("1. Chiffres et figures des sujets")
    for s in liste:
        for script in s.d.get("scripts", []):
            lancer([sys.executable, "-B", str(s.dossier / "code" / script)])


def preparer_docs(liste):
    """Vide docs/ et y copie ce que le site sert tel quel : style, figures, photos ; .nojekyll désactive Jekyll."""
    print("2. Dossier docs/ vidé, style, figures et photos copiés")
    if DOCS.exists():
        shutil.rmtree(DOCS)
    DOCS.mkdir()
    (DOCS / ".nojekyll").write_text("", encoding="utf-8")
    (DOCS / "README.md").write_text(
        "# Site construit / Built website\n\n"
        "Site statique servi par GitHub Pages, construit par `make construire` (`outils/construire.py`) depuis "
        "`site/` et les dossiers des sujets. Ne pas le modifier à la main : il est vidé et refait à chaque "
        "construction.\n\n*Static site served by GitHub Pages, rebuilt from the sources by `make construire`; do not "
        "edit by hand.*\n", encoding="utf-8")
    shutil.copy(SITE / "style.css", DOCS / "style.css")
    for s in liste:
        for sous, motifs in (("figures", ("fig_*.svg", "fig_*.png")), ("photos", ("*.jpg",))):
            (DOCS / s.id / sous).mkdir(parents=True)
            for motif in motifs:
                for f in sorted((s.dossier / sous).glob(motif)):
                    shutil.copy(f, DOCS / s.id / sous / f.name)
        for lang in LANGUES:
            if s.pdf(lang):
                (DOCS / s.id / "telechargements").mkdir(parents=True, exist_ok=True)
                shutil.copy(s.pdf(lang), DOCS / s.id / "telechargements" / s.pdf(lang).name)
                print(f"  PDF exporté copié : {s.pdf(lang).relative_to(RACINE)}")


def etape_docx(liste):
    print("3. Papiers .docx")
    produits = {}
    for s in liste:
        for lang in LANGUES:
            if not s.a_papier(lang):
                print(f"  {s.chemin(lang, 'papier').relative_to(RACINE)} absent : pas de .docx ({lang})")
                continue
            sortie = DOCS / s.id / "telechargements" / s.docx(lang)
            sortie.parent.mkdir(parents=True, exist_ok=True)
            meta = {"lang": LANGUES[lang]["lang_docx"], "prefixe_sujet": "",
                    "lien_references": f"{DEPOT}/blob/main/{s.id}/papier/references.md"}
            pandoc(s.sources_papier(lang), sortie, meta, format_html=False,
                   ressources=(s.dossier, s.dossier / "papier" / lang))
            produits[(s.id, lang)] = sortie
    return produits


def carte_sujet(s, lang):
    L, d = LANGUES[lang], s.d[lang]
    base = f"{s.id}/"
    liens = []
    if s.a_papier(lang):
        liens.append(f'<a class="bouton principal" href="{base}{L["pages"]["papier"]}">{L["lire"]}</a>')
    liens.append(f'<a class="bouton" href="{base}{L["pages"]["donnees"]}">{L["voir_donnees"]}</a>')
    liens.append(f'<a class="bouton" href="{base}{L["pages"]["photos"]}">{L["voir_photos"]}</a>')
    return (f'<article class="sujet">\n<h3><a href="{base}index.html">{html.escape(d["titre"])}</a></h3>\n'
            f'<p>{html.escape(d["accroche"])}</p>\n<p class="etat">{html.escape(d["etat"])}</p>\n'
            f'<div class="boutons">{"".join(liens)}</div>\n</article>')


def etape_accueil(liste, tmp):
    print("4. Accueil du projet")
    for lang in LANGUES:
        L, A = LANGUES[lang], LANGUES[LANGUES[lang]["autre"]]
        cartes = '<div class="sujets">\n' + "\n".join(carte_sujet(s, lang) for s in liste) + "\n</div>"
        src = remplir((SITE / f"accueil.{lang}.md").read_text(encoding="utf-8"), sujets=cartes, depot=DEPOT,
                      contact=L["contact"])
        md = tmp / f"accueil_projet.{lang}.md"
        md.write_text(src, encoding="utf-8")
        meta = meta_commune(lang, PROJET[lang]["nom"], False)
        meta["title"] = PROJET[lang]["titre"]
        meta["autre_langue"] = "en/index.html" if lang == "fr" else "../index.html"
        meta["nav"] = ([{"href": "index.html", "label": L["accueil_projet"], "actif": True}] +
                       [{"href": f"{s.id}/index.html", "label": s.d[lang]["titre"]} for s in liste])
        sortie = DOCS / ("" if lang == "fr" else "en") / "index.html"
        sortie.parent.mkdir(parents=True, exist_ok=True)
        pandoc([md], sortie, meta)


def boutons_sujet(s, lang, docx):
    L, ps = LANGUES[lang], prefixe_sujet(s, lang)
    b = []
    if s.a_papier(lang):
        b.append(f'<a class="bouton principal" href="{L["pages"]["papier"]}">{L["lire"]}</a>')
    if (s.id, lang) in docx:
        b.append(f'<a class="bouton" href="{ps}telechargements/{s.docx(lang)}" download>{L["telecharger"]}</a>')
    if s.pdf(lang):
        b.append(f'<a class="bouton" href="{ps}telechargements/{s.pdf(lang).name}" download>{L["telecharger_pdf"]}</a>')
    b.append(f'<a class="bouton" href="{L["pages"]["donnees"]}">{L["voir_donnees"]}</a>')
    b.append(f'<a class="bouton" href="{DEPOT}/tree/main/{s.id}">GitHub</a>')
    return '<div class="boutons">' + "".join(b) + "</div>"


def page_photos(s, lang):
    with open(s.dossier / "photos" / "legendes.csv", newline="", encoding="utf-8") as f:
        lignes = list(csv.DictReader(f, delimiter=";"))
    cle, ps = f"legende_{lang}", prefixe_sujet(s, lang)

    def date(iso):
        a, m, j = iso.split("-")
        return f"{j}/{m}/{a}" if lang == "fr" else iso

    items = "".join(
        f'<figure><a href="{ps}photos/{l["fichier"]}"><img src="{ps}photos/{l["fichier"]}" '
        f'alt="{html.escape(l[cle])}" loading="lazy"></a><figcaption>{html.escape(l[cle])} '
        f'{"Photo du" if lang == "fr" else "Photo taken"} {date(l["date"])}.</figcaption></figure>\n'
        for l in lignes)
    return f"{LANGUES[lang]['photos_intro']}\n\n<div class=\"galerie\">\n{items}</div>\n"


def etape_sujets(liste, docx, tmp):
    print("5. Pages des sujets")
    for s in liste:
        for lang in LANGUES:
            L, d = LANGUES[lang], s.d[lang]
            dossier = DOCS / ("" if lang == "fr" else "en") / s.id
            dossier.mkdir(parents=True, exist_ok=True)
            pages = s.dossier / "site"
            # présentation du sujet
            src = remplir((pages / f"accueil.{lang}.md").read_text(encoding="utf-8"), chiffres=s.tuiles(lang),
                          boutons=boutons_sujet(s, lang, docx), resume=s.resume(lang), depot=DEPOT,
                          contact=L["contact"])
            md = tmp / f"{s.id}.accueil.{lang}.md"
            md.write_text(src, encoding="utf-8")
            meta = meta_sujet(s, lang, "accueil", d["titre"])
            meta["title"] = d["titre"]
            pandoc([md], dossier / L["pages"]["accueil"], meta, ressources=(s.dossier,))
            # papier
            meta = meta_sujet(s, lang, "papier", L["labels"]["papier"])
            if s.a_papier(lang):
                ps = prefixe_sujet(s, lang)
                liens = ([f'<a class="bouton" href="{ps}telechargements/{s.docx(lang)}" download>{L["telecharger"]}</a>']
                         if (s.id, lang) in docx else [])
                if s.pdf(lang):
                    liens.append(f'<a class="bouton" href="{ps}telechargements/{s.pdf(lang).name}" download>'
                                 f'{L["telecharger_pdf"]}</a>')
                lien = f'\n\n<p class="boutons">{"".join(liens)}</p>\n' if liens else ""
                pre = tmp / f"{s.id}.lien.{lang}.md"
                pre.write_text(lien, encoding="utf-8")
                pandoc([*s.sources_papier(lang), pre], dossier / L["pages"]["papier"], meta, toc=True,
                       ressources=(s.dossier, s.dossier / "papier" / lang))
            else:
                md = tmp / f"{s.id}.prep.{lang}.md"
                md.write_text(remplir((SITE / f"en_preparation.{lang}.md").read_text(encoding="utf-8"),
                                      page_donnees=L["pages"]["donnees"], page_photos=L["pages"]["photos"]),
                              encoding="utf-8")
                meta["title"] = L["labels"]["papier"]
                pandoc([md], dossier / L["pages"]["papier"], meta)
            # données et code
            suffixe = L["suffixe_figure"]
            figures = "\n\n".join(f"![{f[lang]} (`{f['id']}{suffixe}`)]({prefixe_sujet(s, lang)}figures/"
                                  f"{f['id']}{suffixe}.svg)" for f in s.d.get("figures", []))
            doi = f"DOI : {DOI}" if DOI and lang == "fr" else (f"DOI: {DOI}" if DOI else L["doi_absent"])
            citation = L["citation"].format(titre=s.titre_papier(lang), depot=DEPOT, doi=doi)
            md = tmp / f"{s.id}.donnees.{lang}.md"
            md.write_text(remplir((pages / f"donnees.{lang}.md").read_text(encoding="utf-8"), depot=DEPOT,
                                  arbre_sujet=f"{DEPOT}/tree/main/{s.id}", fichier_sujet=f"{DEPOT}/blob/main/{s.id}",
                                  figures=figures, citation=citation), encoding="utf-8")
            meta = meta_sujet(s, lang, "donnees", L["labels"]["donnees"])
            meta["title"] = L["labels"]["donnees"]
            pandoc([md], dossier / L["pages"]["donnees"], meta)
            # photos
            md = tmp / f"{s.id}.photos.{lang}.md"
            md.write_text(page_photos(s, lang), encoding="utf-8")
            meta = meta_sujet(s, lang, "photos", L["labels"]["photos"])
            meta["title"] = L["labels"]["photos"]
            pandoc([md], dossier / L["pages"]["photos"], meta)


def etape_metadonnees(liste):
    """CITATION.cff (citation sur GitHub) et .zenodo.json (fiche Zenodo) : écrits ici pour ne porter le nom du dépôt,
    l'adresse du site et le DOI qu'à partir de outils/publication.conf."""
    print("6. CITATION.cff et .zenodo.json")
    resume_en = ("Field notes from a homeowner renovating a cob (earth) house near Rennes, France: tests made with "
                 "ordinary tools, raw readings, code that rebuilds every number and figure, photos, and the advice "
                 "drawn from them. Topics: " + "; ".join(s.d["en"]["titre"] for s in liste) + ".")
    resume_fr = ("Retours d'expérience d'un particulier sur la rénovation d'une maison en bauge (terre crue) près de "
                 "Rennes : essais faits avec du matériel courant, relevés bruts, code qui refait chaque chiffre et "
                 "chaque figure, photos, et les conseils qu'on en tire. Sujets : "
                 + " ; ".join(s.d["fr"]["titre"] for s in liste) + ".")
    auteur = {"family-names": "Cura", "given-names": "Rémi"}
    if ORCID:
        auteur["orcid"] = f"https://orcid.org/{ORCID}"
    lignes = [
        "# Écrit par outils/construire.py (make construire) : le modifier là, ou dans outils/publication.conf.",
        "cff-version: 1.2.0",
        'message: "Pour citer ce dépôt, utilisez ces informations. / To cite this repository, please use this '
        'information."',
        f"title: {json.dumps(TITRE_DEPOT, ensure_ascii=False)}",
        "type: dataset",
        "authors:",
        f"  - family-names: {auteur['family-names']}",
        f"    given-names: {json.dumps(auteur['given-names'], ensure_ascii=False)}",
    ]
    if ORCID:
        lignes.append(f"    orcid: {json.dumps(auteur['orcid'])}")
    lignes += [
        f"repository-code: {json.dumps(DEPOT)}",
        f"url: {json.dumps(ADRESSE_SITE)}",
        "license:", "  - CC-BY-4.0", "  - MIT",
        "keywords:", *[f"  - {json.dumps(k)}" for k in MOTS_CLES],
        f"abstract: {json.dumps(resume_en, ensure_ascii=False)}",
    ]
    if DOI:
        lignes.append(f"doi: {json.dumps(DOI)}")
    (RACINE / "CITATION.cff").write_text("\n".join(lignes) + "\n", encoding="utf-8")

    zenodo = {
        "title": TITRE_DEPOT,
        "upload_type": "dataset",
        "description": f"<p>{html.escape(resume_fr, quote=False)}</p><p>{html.escape(resume_en, quote=False)}</p>"
                       f"<p>Site : <a href=\"{ADRESSE_SITE}\">{ADRESSE_SITE}</a></p>",
        "creators": [{"name": "Cura, Rémi", **({"orcid": ORCID} if ORCID else {})}],
        "license": "cc-by-4.0",
        "access_right": "open",
        "keywords": MOTS_CLES,
        "language": "fra",
    }
    (RACINE / ".zenodo.json").write_text(json.dumps(zenodo, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main():
    sys.stdout.reconfigure(line_buffering=True)   # nos lignes et celles des scripts lancés, dans l'ordre
    if shutil.which("pandoc") is None:
        sys.exit("pandoc introuvable : l'installer (https://pandoc.org) puis relancer.")
    liste = sujets()
    if not liste:
        sys.exit("aucun sujet : aucun dossier de la racine ne contient de sujet.toml")
    print(f"Dépôt : {DEPOT}\nSite : {ADRESSE_SITE}\nSujets : {', '.join(s.id for s in liste)}\n")
    if "--sans-code" not in sys.argv:
        etape_code(liste)
    for s in liste:
        manquantes = [f["id"] + suf for f in s.d.get("figures", []) for suf in ("", "_en")
                      if not (s.dossier / "figures" / f"{f['id']}{suf}.svg").exists()]
        if manquantes:
            sys.exit(f"{s.id} : figures manquantes : {', '.join(manquantes)} ; relancer sans --sans-code")
    preparer_docs(liste)
    docx = etape_docx(liste)
    tmp = pathlib.Path(tempfile.mkdtemp())
    try:
        etape_accueil(liste, tmp)
        etape_sujets(liste, docx, tmp)
    finally:
        shutil.rmtree(tmp)
    etape_metadonnees(liste)
    pages = sorted(p.relative_to(DOCS).as_posix() for p in DOCS.rglob("*.html"))
    print(f"\nSite construit dans docs/ : {len(pages)} pages")
    for p in pages:
        print(f"  {p}")
    print(f".docx : {', '.join(p.relative_to(RACINE).as_posix() for p in docx.values()) or 'aucun (papier absent)'}")
    print(f"Adresse une fois publié : {ADRESSE_SITE}")


if __name__ == "__main__":
    main()
