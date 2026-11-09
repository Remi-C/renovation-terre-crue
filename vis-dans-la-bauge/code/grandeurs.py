"""Grandeurs tirées des relevés sans aucun modèle (cisaillement : efforts, déplacements, raideurs de l'assemblage ; arrachement : charge par longueur de vis) ; écrit donnees/resultats_calcules.json."""

# Exécution, depuis la racine du dépôt : python3 vis-dans-la-bauge/code/grandeurs.py
# Arithmétique seule sur les relevés : aucune hypothèse sur ce que mesure le comparateur. Les déplacements sous 50 kg
# sont lus au 0,1 mm près sur la fiche ; les valeurs à 25, 50 et 100 kg sont des interpolations entre deux lectures.
# Les raideurs (kg/mm) sont celles de tout l'assemblage tel que le comparateur le lit (vis, planche, montage, platine
# de réaction qui recule), pas une raideur de la bauge : d'où « assemblage » dans le nom des clés.

import csv
import json

from lecture import DEPLACEMENTS_CONTEXTE, DONNEES, MOTS_RUINE, essais_decoupes, interp

SORTIE = DONNEES / "resultats_calcules.json"
RELEVES_ARRACHEMENT = DONNEES / "releves_arrachement_2026_11_07.csv"
PRIS_DANS_LA_PLATINE = 15         # mm de vis pris dans la platine de traction (07/11/2026)
# A8 : 60 mm notés sur le moment ; le filet de cette vis s'arrête à ≈ 50 mm de la pointe (mesuré sur photo, 49,4 à
# 50,0 mm) et seul le filet était dans la bauge (l'auteur, 08/11/2026) : ≈ 50 mm retenus.
PROFONDEUR_RETENUE = {"A8": 50.0}
EFFORTS_LUS = (25, 50, 100)       # kg : déplacement lu à ces efforts sur la 1re charge (valeurs rondes)
BAISSE_PALIER = 0.10              # baisse d'effort au palier, ≈ 10 % (observation de l'auteur pendant les essais)


def r(x, n=3):
    return None if x is None else round(x, n)


def premiere_charge(ms):
    """1re montée non écartée depuis le zéro du protocole ; None si la 1re charge a été écartée (C1)."""
    m = ms[0]
    return None if m["ecartee"] else m


def grandeurs_essai(nom, e):
    ms = e["montees"]
    lues = [m for m in ms if not m["ecartee"]]
    efforts = [p[0] for m in ms for p in m["points"]] + [f for m in ms for f, _ in m["evenements"]]
    ruine = next(((f, o, m["n"]) for m in ms for f, o in m["evenements"] if any(k in o.lower() for k in MOTS_RUINE)),
                 None)
    g = {
        "essai": nom,
        "effort_max_kg": max(efforts),
        "rupture": None if ruine is None else {"effort_kg": ruine[0], "mot_note": ruine[1], "montee": ruine[2]},
        "deplacements": "contexte" if nom in DEPLACEMENTS_CONTEXTE else "lus",
        "montees": [{"n": m["n"], "statut": m["statut"], "ecartee": m["ecartee"], "origine_mm": m["origine"],
                     "points": m["points"], "residuel_mm": m["residuel"]} for m in ms],
    }
    m1 = premiere_charge(ms)
    if m1:
        pic = max(m1["points"])
        g["premiere_charge"] = {
            "statut": m1["statut"],
            **{f"deplacement_a_{f}kg_mm": r(interp(m1["points"], m1["origine"], f)) for f in EFFORTS_LUS},
            "pic_kg": pic[0], "deplacement_au_pic_mm": pic[1], "residuel_mm": m1["residuel"],
        }
        g["premiere_charge"].update(decharge(pic, m1["residuel"]))
    g["rechargements"] = [rechargement(m, m1) for m in lues if m is not m1 and len(m["points"]) >= 2]
    return g


def decharge(pic, residuel):
    """Retour à la décharge complète : part du déplacement rendue, raideur moyenne de décharge de l'assemblage, retour attendu à un palier."""
    if residuel is None:
        return {}
    rendu = pic[1] - residuel
    k = pic[0] / rendu if rendu > 0 else None
    return {
        "part_rendue_a_la_decharge": r(rendu / pic[1]),
        "raideur_moyenne_de_decharge_assemblage_kg_par_mm": r(k, 1),
        "retour_attendu_pour_une_baisse_de_10pc_mm": r(BAISSE_PALIER * pic[0] / k) if k else None,
    }


def rechargement(m, m1):
    """Raideur sécante de l'assemblage sur un rechargement (1er au plus haut point lu) et sur la 1re charge, même plage."""
    (fa, da), (fb, db) = m["points"][0], max(m["points"])
    k = (fb - fa) / (db - da) if db > da else None
    k1 = None
    if m1:
        d1a, d1b = interp(m1["points"], m1["origine"], fa), interp(m1["points"], m1["origine"], fb)
        k1 = (fb - fa) / (d1b - d1a) if d1a is not None and d1b is not None and d1b > d1a else None
    sortie = {"n": m["n"], "statut": m["statut"], "plage_kg": [fa, fb], "deplacement_au_plus_haut_mm": db,
              "raideur_secante_assemblage_kg_par_mm": r(k, 1),
              "raideur_secante_assemblage_1re_charge_meme_plage_kg_par_mm": r(k1, 1),
              "residuel_mm": m["residuel"]}
    sortie.update({k_: v for k_, v in decharge((fb, db), m["residuel"]).items()})
    return sortie


def arrachement():
    """Paliers des essais d'arrachement du 07/11/2026 : longueur de vis dans la bauge, charge, tenue ou rupture.

    Longueur dans la bauge = longueur de la vis − 15 mm pris dans la platine − longueur dévissée − filet resté dans
    l'air (mur pas plan), sauf quand une profondeur a été notée sur le moment, ou retenue par l'auteur (A8).
    """
    paliers = []
    with open(RELEVES_ARRACHEMENT, newline="", encoding="utf-8") as f:
        for l in csv.DictReader(f, delimiter=";"):
            nom = l["essai"]
            if nom in PROFONDEUR_RETENUE:
                prof = PROFONDEUR_RETENUE[nom]
            elif l["prof_notee_mm"]:
                prof = float(l["prof_notee_mm"])
            else:
                prof = float(l["longueur_mm"]) - PRIS_DANS_LA_PLATINE - float(l["devisse_mm"]) - float(l["air_mm"])
            paliers.append({"essai": nom, "d_mm": int(l["d_mm"]), "rang": int(l["rang"]), "bauge_mm": prof,
                            "F_bas_kg": float(l["F_bas_kg"]), "F_haut_kg": float(l["F_haut_kg"]),
                            "cede": l["issue"] == "cede", "mode": l["mode"]})
    # pour chaque essai et chaque longueur, la charge la plus haute tenue (tenue = minimum : la rupture est au-dessus)
    retenus = {}
    for p in paliers:
        k = (p["essai"], p["bauge_mm"])
        if p["cede"] or k not in retenus or (not retenus[k]["cede"] and p["F_haut_kg"] > retenus[k]["F_haut_kg"]):
            retenus[k] = p
    return {"source": "donnees/releves_arrachement_2026_11_07.csv",
            "regle": "par essai et par longueur dans la bauge : la rupture, sinon la charge la plus haute tenue",
            "paliers": sorted(retenus.values(), key=lambda p: (p["essai"], -p["bauge_mm"]))}


def main():
    essais = essais_decoupes()
    res = {nom: grandeurs_essai(nom, e) for nom, e in essais.items()}
    arr = arrachement()
    SORTIE.write_text(json.dumps({"source": "donnees/releves_cisaillement_2026_10_30.csv",
                                  "script": "code/grandeurs.py", "essais": res, "arrachement": arr},
                                 ensure_ascii=False, indent=1),
                      encoding="utf-8")
    print("arrachement (07/11/2026) : essai, longueur dans la bauge, charge, issue")
    for p in arr["paliers"]:
        F = f"{p['F_bas_kg']:.0f}" if p["F_bas_kg"] == p["F_haut_kg"] else f"{p['F_bas_kg']:.0f}–{p['F_haut_kg']:.0f}"
        print(f"  {p['essai']} Ø{p['d_mm']:<2} {p['bauge_mm'] / 10:5.1f} cm  {F:>7} kg  "
              + ("cède" if p["cede"] else "tenu"))
    print(f"{'essai':5} {'max kg':>6} {'rupture':<22} {'δ25':>5} {'δ50':>5} {'δ100':>5} {'résid.':>6} {'rendu':>5}")
    for nom, g in res.items():
        p = g.get("premiere_charge", {})
        rup = f"{g['rupture']['effort_kg']:.0f} kg « {g['rupture']['mot_note'][:12]} »" if g["rupture"] else "aucune"
        cell = lambda x, n=2: "  —  " if x is None else f"{x:5.{n}f}"  # noqa: E731
        print(f"{nom:5} {g['effort_max_kg']:6.0f} {rup:<22} {cell(p.get('deplacement_a_25kg_mm'))} "
              f"{cell(p.get('deplacement_a_50kg_mm'))} {cell(p.get('deplacement_a_100kg_mm'))} "
              f"{cell(p.get('residuel_mm'))} {cell(p.get('part_rendue_a_la_decharge'))}"
              + ("  (déplacements : contexte)" if g["deplacements"] == "contexte" else ""))
        for rc in g["rechargements"]:
            print(f"      rechargement {rc['n']} : {rc['plage_kg'][0]:.0f}–{rc['plage_kg'][1]:.0f} kg, "
                  f"{rc['deplacement_au_plus_haut_mm']} mm au plus haut, raideur de l'assemblage {rc['raideur_secante_assemblage_kg_par_mm']} kg/mm"
                  + (f" (1re charge : {rc['raideur_secante_assemblage_1re_charge_meme_plage_kg_par_mm']})"
                     if rc["raideur_secante_assemblage_1re_charge_meme_plage_kg_par_mm"] else ""))
    print(f"\nécrit : {SORTIE.relative_to(SORTIE.parents[1])}")


if __name__ == "__main__":
    main()
