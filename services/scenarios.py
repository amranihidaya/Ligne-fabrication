"""
Application des 4 scénarios d'amélioration sur la ligne de base.
Chaque fonction retourne un tuple (postes_modifies, parametres_modifies).
Les calculs eux-mêmes sont faits par services.calculs.simuler.
"""
import copy
from typing import List, Tuple
from .domain import Poste, Parametres


def scenario_baseline(postes: List[Poste], params: Parametres) -> Tuple[List[Poste], Parametres]:
    """Aucune modification."""
    return copy.deepcopy(postes), copy.deepcopy(params)


def scenario_s1_lean(postes: List[Poste], params: Parametres) -> Tuple[List[Poste], Parametres]:
    """
    S1 — Lean Manufacturing.
    Réduction des arrêts (TPM/SMED) et des rebuts (autocontrôle).
    PDF : arrêts 10% → 5%, rebut 5% → 2%.
    """
    new_params = copy.deepcopy(params)
    new_params.taux_arret_machine = 0.05
    new_params.taux_rebut = 0.02
    return copy.deepcopy(postes), new_params


def scenario_s2_machine(postes: List[Poste], params: Parametres) -> Tuple[List[Poste], Parametres]:
    """
    S2 — Ajout d'une machine au poste goulot.
    On dédouble le poste avec le temps opératoire le plus élevé.
    PDF : 2 tours en parallèle → t_goulot devient 6/2 = 3 min.
    """
    new_postes = copy.deepcopy(postes)
    # Identifier le poste avec le temps brut le plus long
    goulot_idx = max(range(len(new_postes)), key=lambda i: new_postes[i].temps_min_par_piece / new_postes[i].nb_machines)
    new_postes[goulot_idx].nb_machines += 1
    return new_postes, copy.deepcopy(params)


def scenario_s3_reequilibrage(postes: List[Poste], params: Parametres) -> Tuple[List[Poste], Parametres]:
    """
    S3 — Rééquilibrage de ligne.
    Transfert de tâches du goulot (Tour) vers postes sous-utilisés.
    PDF : Tour 6 → 4 min, Scie 2 → 3.5 min, Contrôle 2 → 2.5 min.
    """
    new_postes = copy.deepcopy(postes)
    # Trouver le poste goulot et lui retirer 2 min
    goulot_idx = max(range(len(new_postes)), key=lambda i: new_postes[i].temps_min_par_piece / new_postes[i].nb_machines)
    new_postes[goulot_idx].temps_min_par_piece -= 2.0

    # Trouver les 2 postes les moins utilisés et leur ajouter du temps
    autres = [(i, p) for i, p in enumerate(new_postes) if i != goulot_idx]
    autres.sort(key=lambda x: x[1].temps_min_par_piece)
    if len(autres) >= 2:
        new_postes[autres[0][0]].temps_min_par_piece += 1.5
        new_postes[autres[1][0]].temps_min_par_piece += 0.5

    return new_postes, copy.deepcopy(params)


def scenario_s4_industrie40(postes: List[Poste], params: Parametres) -> Tuple[List[Poste], Parametres]:
    """
    S4 — Industrie 4.0 : S3 + IoT (maintenance prédictive) + vision qualité.
    PDF : rééquilibrage + arrêts 10% → 3% + rebut 5% → 1%.
    """
    new_postes, _ = scenario_s3_reequilibrage(postes, params)
    new_params = copy.deepcopy(params)
    new_params.taux_arret_machine = 0.03
    new_params.taux_rebut = 0.01
    return new_postes, new_params


SCENARIOS = {
    "Baseline": scenario_baseline,
    "S1 - Lean": scenario_s1_lean,
    "S2 - Machine": scenario_s2_machine,
    "S3 - Rééquilibrage": scenario_s3_reequilibrage,
    "S4 - Industrie 4.0": scenario_s4_industrie40,
}


# Investissements et coûts (PDF section 7)
INVESTISSEMENTS = {
    "Baseline": 0,
    "S1 - Lean": 3500,
    "S2 - Machine": 107000,
    "S3 - Rééquilibrage": 8000,
    "S4 - Industrie 4.0": 40000,
}


def calculer_economie(pieces_conformes_baseline: float, pieces_conformes_scenario: float,
                      params: Parametres, investissement: float) -> dict:
    """
    Calcule gain annuel, ROI et délai de retour pour un scénario.
    """
    delta = pieces_conformes_scenario - pieces_conformes_baseline
    marge = params.prix_vente_unitaire - params.cout_variable_unitaire
    gain_annuel = delta * marge * params.jours_ouvres_an
    if investissement > 0 and gain_annuel > 0:
        roi_pct = (gain_annuel - investissement) / investissement * 100
        retour_jours = investissement / (gain_annuel / params.jours_ouvres_an)
    else:
        roi_pct = 0
        retour_jours = 0
    return {
        "delta_pieces": delta,
        "gain_annuel": gain_annuel,
        "investissement": investissement,
        "roi_pct": roi_pct,
        "retour_jours": retour_jours,
        "gain_3_ans": gain_annuel * 3 - investissement,
    }
