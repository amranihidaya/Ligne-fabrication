"""
Modèles de domaine. Pures dataclasses, aucune dépendance framework.
"""
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Poste:
    numero: int
    nom_operation: str
    machine: str
    temps_min_par_piece: float
    nb_machines: int = 1

    @property
    def temps_effectif(self) -> float:
        """Temps par pièce en tenant compte des machines en parallèle."""
        return self.temps_min_par_piece / self.nb_machines


@dataclass
class Parametres:
    demande_client_jour: float
    temps_travail_min_jour: float
    taux_rebut: float            # 0.05 = 5%
    taux_arret_machine: float    # 0.10 = 10%
    taille_lot: int
    prix_vente_unitaire: float = 85.0
    cout_variable_unitaire: float = 48.0
    jours_ouvres_an: int = 220


@dataclass
class Alerte:
    code: str
    niveau: str  # "CRITIQUE", "ATTENTION", "INFO"
    message: str
    cause_chiffree: str
    recommandation: str


@dataclass
class ResultatSimulation:
    postes: List[Poste]
    parametres: Parametres
    # Indicateurs calculés
    tc_global: float
    t_goulot: float
    poste_goulot: Poste
    t_eff: float
    capacite_prod: float
    pieces_conformes: float
    deficit: float
    taux_utilisation: dict  # {numero_poste: taux}
    # TRS
    disponibilite: float
    performance: float
    qualite: float
    trs: float
    # Flux
    lead_time: float
    wip: float
    # Métadonnées
    nom_scenario: str = "Baseline"
    alertes: List[Alerte] = field(default_factory=list)
