"""
Module de calcul des indicateurs industriels.
Toutes les formules viennent du PDF du projet (sections 2 à 4).

Aucune dépendance Streamlit. Testable en isolation.
"""
from typing import List
from .domain import Poste, Parametres, ResultatSimulation


def temps_cycle_global(postes: List[Poste]) -> float:
    """Tc = somme des temps opératoires."""
    return sum(p.temps_min_par_piece for p in postes)


def identifier_goulot(postes: List[Poste]) -> Poste:
    """Goulot = poste avec le temps effectif le plus élevé."""
    return max(postes, key=lambda p: p.temps_effectif)


def temps_disponible_effectif(parametres: Parametres) -> float:
    """T_eff = T_dispo × (1 − taux_arret)."""
    return parametres.temps_travail_min_jour * (1 - parametres.taux_arret_machine)


def capacite_production(t_eff: float, t_goulot: float) -> float:
    """Capacite = T_eff / t_goulot."""
    if t_goulot <= 0:
        raise ValueError("t_goulot doit être > 0")
    return t_eff / t_goulot


def pieces_conformes(capacite: float, taux_rebut: float) -> float:
    """Pièces conformes = capacite × (1 − taux_rebut)."""
    return capacite * (1 - taux_rebut)


def taux_utilisation_postes(postes: List[Poste], capacite: float, t_eff: float) -> dict:
    """U_i = (t_i × Capacite) / T_eff pour chaque poste."""
    if t_eff <= 0:
        raise ValueError("t_eff doit être > 0")
    return {
        p.numero: (p.temps_effectif * capacite) / t_eff
        for p in postes
    }


def trs_complet(t_eff: float, t_dispo: float, capacite: float, t_goulot: float, taux_rebut: float) -> dict:
    """
    Calcule A, P, Q, TRS.
    A = T_eff / T_dispo
    P = (capacite × t_goulot) / T_eff   (plafonné à 1)
    Q = 1 − taux_rebut
    """
    A = t_eff / t_dispo if t_dispo > 0 else 0
    P = min((capacite * t_goulot) / t_eff, 1.0) if t_eff > 0 else 0
    Q = 1 - taux_rebut
    return {
        "disponibilite": A,
        "performance": P,
        "qualite": Q,
        "trs": A * P * Q,
    }


def lead_time(tc_global: float, t_goulot: float, taille_lot: int) -> float:
    """LT = Tc + t_goulot × (taille_lot − 1)."""
    return tc_global + t_goulot * (taille_lot - 1)


def wip_estime(capacite: float, t_eff: float, lt: float) -> float:
    """Loi de Little : WIP = lambda × LT, avec lambda = capacite / T_eff."""
    if t_eff <= 0:
        return 0
    lam = capacite / t_eff
    return lam * lt


def simuler(postes: List[Poste], parametres: Parametres, nom: str = "Baseline") -> ResultatSimulation:
    """
    Calcule tous les indicateurs et retourne un ResultatSimulation complet.
    Le calcul des alertes est délégué à services.alertes.generer_alertes.
    """
    if not postes:
        raise ValueError("Au moins un poste est requis")

    tc = temps_cycle_global(postes)
    goulot = identifier_goulot(postes)
    t_g = goulot.temps_effectif
    t_eff = temps_disponible_effectif(parametres)
    cap = capacite_production(t_eff, t_g)
    conformes = pieces_conformes(cap, parametres.taux_rebut)
    deficit = parametres.demande_client_jour - conformes
    utilisation = taux_utilisation_postes(postes, cap, t_eff)
    trs = trs_complet(t_eff, parametres.temps_travail_min_jour, cap, t_g, parametres.taux_rebut)
    lt = lead_time(tc, t_g, parametres.taille_lot)
    wip = wip_estime(cap, t_eff, lt)

    return ResultatSimulation(
        postes=postes,
        parametres=parametres,
        tc_global=tc,
        t_goulot=t_g,
        poste_goulot=goulot,
        t_eff=t_eff,
        capacite_prod=cap,
        pieces_conformes=conformes,
        deficit=deficit,
        taux_utilisation=utilisation,
        disponibilite=trs["disponibilite"],
        performance=trs["performance"],
        qualite=trs["qualite"],
        trs=trs["trs"],
        lead_time=lt,
        wip=wip,
        nom_scenario=nom,
    )
