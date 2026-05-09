"""
Génération des alertes basées sur les résultats de simulation.
Règles déclaratives. Chaque alerte explique sa cause chiffrée.
"""
from typing import List
from .domain import ResultatSimulation, Alerte


def generer_alertes(res: ResultatSimulation) -> List[Alerte]:
    alertes: List[Alerte] = []

    # 1. Déficit face à la demande
    if res.pieces_conformes < res.parametres.demande_client_jour:
        deficit_abs = res.parametres.demande_client_jour - res.pieces_conformes
        # Calcul de la cible théorique
        t_goulot_cible = res.t_eff / res.parametres.demande_client_jour
        alertes.append(Alerte(
            code="DEFICIT_DEMANDE",
            niveau="CRITIQUE",
            message=f"Production insuffisante : {res.pieces_conformes:.0f} pcs/j conformes "
                    f"face à une demande de {res.parametres.demande_client_jour:.0f} pcs/j "
                    f"(déficit de {deficit_abs:.1f} pcs/j).",
            cause_chiffree=(
                f"Goulot {res.poste_goulot.machine} = {res.t_goulot:.1f} min/pièce. "
                f"T_eff = {res.t_eff:.0f} min/j → capacité brute {res.capacite_prod:.1f} pcs/j. "
                f"Avec rebut {res.parametres.taux_rebut*100:.0f}% → {res.pieces_conformes:.1f} conformes."
            ),
            recommandation=(
                f"Pour atteindre {res.parametres.demande_client_jour:.0f} pcs/j, "
                f"il faut t_goulot ≤ {t_goulot_cible:.2f} min ou réduire taux d'arrêt/rebut."
            ),
        ))

    # 2. Goulot saturé
    u_goulot = res.taux_utilisation.get(res.poste_goulot.numero, 0)
    if u_goulot >= 0.95:
        alertes.append(Alerte(
            code="GOULOT_SATURE",
            niveau="ATTENTION",
            message=f"Le poste {res.poste_goulot.machine} tourne à {u_goulot*100:.1f}% : aucune marge en cas d'aléa.",
            cause_chiffree=f"Temps utilisé = {res.t_goulot * res.capacite_prod:.0f} min sur T_eff = {res.t_eff:.0f} min.",
            recommandation="Tout incident sur ce poste impacte directement la production journalière.",
        ))

    # 3. TRS faible
    if res.trs < 0.85:
        alertes.append(Alerte(
            code="TRS_FAIBLE",
            niveau="ATTENTION",
            message=f"TRS de {res.trs*100:.1f}% en dessous du seuil industriel de référence (85%).",
            cause_chiffree=f"A={res.disponibilite*100:.0f}% × P={res.performance*100:.0f}% × Q={res.qualite*100:.0f}% = {res.trs*100:.1f}%.",
            recommandation="Identifier la composante la plus faible (A, P ou Q) pour cibler les actions.",
        ))

    # 4. Arrêts élevés
    if res.parametres.taux_arret_machine >= 0.10:
        temps_perdu = res.parametres.temps_travail_min_jour * res.parametres.taux_arret_machine
        alertes.append(Alerte(
            code="ARRETS_ELEVES",
            niveau="INFO",
            message=f"Taux d'arrêt machine de {res.parametres.taux_arret_machine*100:.0f}%.",
            cause_chiffree=f"{temps_perdu:.0f} min/j perdues sur les {res.parametres.temps_travail_min_jour:.0f} min disponibles.",
            recommandation="Mise en place d'un plan TPM (maintenance préventive) + SMED (réduction temps changement).",
        ))

    # 5. Rebut élevé
    if res.parametres.taux_rebut >= 0.05:
        pertes = res.capacite_prod * res.parametres.taux_rebut
        alertes.append(Alerte(
            code="REBUT_ELEVE",
            niveau="INFO",
            message=f"Taux de rebut de {res.parametres.taux_rebut*100:.0f}%.",
            cause_chiffree=f"≈ {pertes:.1f} pcs/j fabriquées mais non conformes.",
            recommandation="Autocontrôle opérateur, contrôle qualité digital (vision), compensation d'usure outil.",
        ))

    # 6. Postes sous-utilisés
    for poste in res.postes:
        u = res.taux_utilisation.get(poste.numero, 0)
        if u < 0.40:
            alertes.append(Alerte(
                code="POSTE_SOUS_UTILISE",
                niveau="INFO",
                message=f"Poste {poste.machine} utilisé à seulement {u*100:.1f}%.",
                cause_chiffree=f"Temps opératoire {poste.temps_min_par_piece:.1f} min × {res.capacite_prod:.0f} pcs = {poste.temps_min_par_piece * res.capacite_prod:.0f} min sur {res.t_eff:.0f} dispo.",
                recommandation=f"Capacité dormante : peut absorber des tâches du goulot ({res.poste_goulot.machine}) via rééquilibrage.",
            ))

    # 7. WIP élevé
    if res.wip > res.parametres.taille_lot * 1.2:
        alertes.append(Alerte(
            code="WIP_ELEVE",
            niveau="INFO",
            message=f"WIP estimé à {res.wip:.1f} pcs (taille de lot = {res.parametres.taille_lot}).",
            cause_chiffree=f"Loi de Little : λ = {res.capacite_prod/res.t_eff:.3f} pcs/min × LT = {res.lead_time:.0f} min.",
            recommandation="Réduire la taille de lot ou améliorer le flux pour limiter les en-cours.",
        ))

    return alertes
