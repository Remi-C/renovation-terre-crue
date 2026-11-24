"""Teneur en eau de chaque pot, budget de bruit de pesée, reprise d'humidité, humidité relative d'équilibre sur deux sols publiés → donnees/resultats_calcules.json."""

# Depuis la racine du dépôt : python3 humidite-de-la-bauge/code/grandeurs.py
# Entrées : donnees/pesees.csv, prelevements.csv, isotherme_phung_2018.csv. Aucun fichier extérieur au sujet.

import json
import math
import statistics

from lecture import (DONNEES, FACADE, POTS, SEC, SERIES_SECHES, TARE, TEL_QUEL, courbe_sechage, hr_depuis_w,
                     lire_isothermes, lire_pesees, lire_prelevements)

# Masse volumique sèche supposée de la bauge, pour passer d'une teneur en eau à des kg d'eau par m² de mur.
# Hypothèse, non mesurée sur ce mur : 1 700 kg/m³ au centre, 1 500 à 1 800 pour l'encadrer (les éprouvettes de la thèse
# de Phung vont de 1 460 à 1 840 kg/m³).
RHO_SEC = {"bas": 1500.0, "central": 1700.0, "haut": 1800.0}


def bruit(d):
    """Écart-type de pesée : répétabilité (lectures répétées d'une même pesée) + dérive du témoin entre séries."""
    carres, n_pesees = [], 0
    for v in d.values():
        if len(v["lectures"]) >= 2:
            carres += [(x - v["moy"]) ** 2 for x in v["lectures"]]
            n_pesees += 1
    sigma_rep = math.sqrt(sum(carres) / (len(carres) - n_pesees))
    t0 = d[("T", TEL_QUEL)]["moy"]
    derive = {s: d[("T", s)]["moy"] - t0 for s in ["E1", "E3", "E4", "E5"] if d[("T", s)]["moy"] is not None}
    sigma_serie = math.sqrt(statistics.fmean([derive[s] ** 2 for s in SERIES_SECHES]))
    return {"repetabilite_sigma_g": sigma_rep, "derive_temoin_g": derive, "entre_series_sigma_g": sigma_serie,
            "par_pesee_sigma_g": math.sqrt(sigma_rep ** 2 + sigma_serie ** 2)}


def teneur(eau, sec, sigma, n=1):
    """Teneur en eau w (% de la masse sèche) et son écart-type (propagation au premier ordre, pesées indépendantes) ;
    n tranches regroupées : toute l'eau sur toute la terre sèche."""
    w = eau / sec * 100
    dw = math.sqrt(n * 2 * sigma ** 2 + n * 2 * sigma ** 2 * (w / 100) ** 2) / sec * 100
    return w, dw


def hr_deux_sols(w, dw, courbes):
    """Humidité relative d'équilibre (%) de w, de w − dw et de w + dw, sur chacun des deux sols publiés ; None si hors courbe."""
    sortie = {}
    for sol, c in courbes.items():
        sortie[sol] = {"centre": hr_depuis_w(w, c), "basse": hr_depuis_w(w - dw, c), "haute": hr_depuis_w(w + dw, c)}
    return sortie


def arrondi(x, n=2):
    return None if x is None else round(x, n)


def main():
    d = lire_pesees()
    pre = lire_prelevements()
    sig = bruit(d)
    sigma = sig["par_pesee_sigma_g"]
    iso = lire_isothermes()
    courbes = {sol: courbe_sechage(iso[sol]) for sol in iso}

    pots = {}
    for e in POTS:
        m0, m1, tare = d[(e, TEL_QUEL)]["moy"], d[(e, SEC)]["moy"], d[(e, TARE)]["moy"]
        eau, sec = m0 - m1, m1 - tare
        w, dw = teneur(eau, sec, sigma)
        pots[e] = {"mur": pre[e]["mur"], "profondeur_cm": pre[e]["profondeur_cm"], "terre_seche_g": arrondi(sec, 3),
                   "eau_g": arrondi(eau, 3), "w_pct": arrondi(w), "incertitude_pct": arrondi(dw),
                   "hr_pct": {s: {k: arrondi(v, 1) for k, v in h.items()} for s, h in hr_deux_sols(w, dw, courbes).items()}}

    def groupe(noms):
        eau = sum(pots[e]["eau_g"] for e in noms)
        sec = sum(pots[e]["terre_seche_g"] for e in noms)
        w, dw = teneur(eau, sec, sigma, n=len(noms))
        return {"pots": noms, "terre_seche_g": arrondi(sec, 3), "w_pct": arrondi(w), "incertitude_pct": arrondi(dw),
                "hr_pct": {s: {k: arrondi(v, 1) for k, v in h.items()} for s, h in hr_deux_sols(w, dw, courbes).items()}}

    # Écarts bruts entre pesées successives, sans aucune convention.
    e1_e0 = {e: arrondi(d[(e, "E1")]["moy"] - d[(e, "E0")]["moy"], 3) for e in POTS + ["T"]}
    reprise = {e: arrondi(d[(e, "E2")]["moy"] - d[(e, "E1")]["moy"], 3) for e in POTS}
    reprise_pct = {e: arrondi(reprise[e] / pots[e]["terre_seche_g"] * 100, 2) for e in POTS}
    e3_e2 = {e: arrondi(d[(e, "E3")]["moy"] - d[(e, "E2")]["moy"], 3) for e in POTS}

    # Sensibilité de la conversion : gain de teneur en eau entre 80 et 90 % d'humidité relative, par sol.
    pente = {}
    for sol, c in courbes.items():
        w = dict(c)
        pente[sol] = {"w_80_pct": w[80.0], "w_90_pct": w[90.0], "gain_points": arrondi(w[90.0] - w[80.0])}

    # Une même teneur en eau (3 %), lue sur chacun des deux sols : l'humidité relative qu'elle représente change beaucoup.
    meme_w = {"w_pct": 3.0, **{f"hr_pct_sol_{sol}": arrondi(hr_depuis_w(3.0, c), 1) for sol, c in courbes.items()}}

    # Eau en excès dans la peau du mur du cabanon, par m² de mur : (w de 0-10 cm − w de 10-20 cm) × masse sèche de 10 cm.
    exces = (pots["A1"]["w_pct"] - pots["A2"]["w_pct"]) / 100
    bilan = {"hypothese": "masse volumique sèche supposée, non mesurée ; épaisseur de la peau prise égale à la tranche A1 (10 cm)",
             "rho_sec_kg_m3": RHO_SEC,
             "eau_en_exces_kg_par_m2": {k: arrondi(exces * r * 0.10, 1) for k, r in RHO_SEC.items()}}

    sortie = {
        "conventions": {"teneur_en_eau": "w = (E0 − E1) / (E1 − E5), en % de la masse de terre sèche",
                        "sec": SEC, "tare": TARE, "tel_quel": TEL_QUEL,
                        "isotherme": "désorption de 5 à 90 % d'humidité relative puis courbe de rétention de 93 % à la "
                                     "saturation, pour chacun des deux sols A et B de Phung (2018) ; interpolation linéaire"},
        "bruit": {k: (arrondi(v, 3) if not isinstance(v, dict) else {a: arrondi(b, 3) for a, b in v.items()})
                  for k, v in sig.items()},
        "pots": pots,
        "facade_0_20_cm": groupe(FACADE), "facade_0_10_cm": groupe(["F1", "F2"]),
        "ecarts_bruts_g": {"E1_moins_E0": e1_e0, "E2_moins_E1": reprise, "E3_moins_E2": e3_e2},
        "reprise_E2_moins_E1_pct_de_terre_seche": reprise_pct,
        "pente_isotherme_80_90": pente,
        "meme_teneur_deux_sols": meme_w,
        "bilan_eau_peau_cabanon": bilan,
    }
    (DONNEES / "resultats_calcules.json").write_text(json.dumps(sortie, ensure_ascii=False, indent=2) + "\n",
                                                     encoding="utf-8")
    print("donnees/resultats_calcules.json")


if __name__ == "__main__":
    main()
