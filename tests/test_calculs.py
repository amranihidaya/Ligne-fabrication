"""
Tests unitaires des calculs.
L'oracle, c'est le PDF du projet : capacite=72, TRS=85.5%, LT=136 min, etc.
Si ces tests passent, les formules sont correctes.

Lancer : pytest tests/test_calculs.py -v
"""
import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.domain import Poste, Parametres
from services import calculs, scenarios, alertes


@pytest.fixture
def postes_pdf():
    return [
        Poste(1, "Découpe brut",       "Scie",       2.0),
        Poste(2, "Tournage extérieur", "Tour",       6.0),
        Poste(3, "Perçage axial",      "Perceuse",   4.0),
        Poste(4, "Fraisage rainure",   "Fraiseuse",  5.0),
        Poste(5, "Finition",           "Rectifieuse", 3.0),
        Poste(6, "Contrôle qualité",   "Manuel",     2.0),
    ]


@pytest.fixture
def params_pdf():
    return Parametres(
        demande_client_jour=80,
        temps_travail_min_jour=480,
        taux_rebut=0.05,
        taux_arret_machine=0.10,
        taille_lot=20,
    )


# ============================================================
# Tests valeurs baseline (PDF section 2)
# ============================================================

def test_temps_cycle_global(postes_pdf):
    assert calculs.temps_cycle_global(postes_pdf) == 22.0


def test_goulot(postes_pdf):
    g = calculs.identifier_goulot(postes_pdf)
    assert g.machine == "Tour"
    assert g.temps_effectif == 6.0


def test_temps_disponible_effectif(params_pdf):
    assert calculs.temps_disponible_effectif(params_pdf) == 432.0


def test_capacite_baseline(postes_pdf, params_pdf):
    res = calculs.simuler(postes_pdf, params_pdf)
    assert res.capacite_prod == 72.0
    assert abs(res.pieces_conformes - 68.4) < 0.01
    assert res.deficit == pytest.approx(11.6, abs=0.01)


def test_taux_utilisation(postes_pdf, params_pdf):
    res = calculs.simuler(postes_pdf, params_pdf)
    # Tour doit être à 100%, Scie à 33.3%
    assert res.taux_utilisation[2] == pytest.approx(1.0, abs=0.01)
    assert res.taux_utilisation[1] == pytest.approx(0.333, abs=0.01)


def test_trs_baseline(postes_pdf, params_pdf):
    res = calculs.simuler(postes_pdf, params_pdf)
    assert res.disponibilite == pytest.approx(0.90, abs=0.01)
    assert res.performance == pytest.approx(1.00, abs=0.01)
    assert res.qualite == pytest.approx(0.95, abs=0.01)
    assert res.trs == pytest.approx(0.855, abs=0.01)


def test_lead_time_baseline(postes_pdf, params_pdf):
    res = calculs.simuler(postes_pdf, params_pdf)
    # LT = 22 + 6 × 19 = 136
    assert res.lead_time == 136.0


def test_wip_baseline(postes_pdf, params_pdf):
    res = calculs.simuler(postes_pdf, params_pdf)
    # WIP ≈ 22.7
    assert res.wip == pytest.approx(22.67, abs=0.1)


# ============================================================
# Tests scénarios (PDF section 5)
# ============================================================

def test_scenario_s1_lean(postes_pdf, params_pdf):
    p, par = scenarios.scenario_s1_lean(postes_pdf, params_pdf)
    res = calculs.simuler(p, par, "S1")
    assert res.capacite_prod == pytest.approx(76.0, abs=0.5)
    assert res.pieces_conformes == pytest.approx(74.5, abs=0.5)
    assert res.trs == pytest.approx(0.931, abs=0.01)


def test_scenario_s2_machine(postes_pdf, params_pdf):
    p, par = scenarios.scenario_s2_machine(postes_pdf, params_pdf)
    res = calculs.simuler(p, par, "S2")
    # Tour passe à 3 min effectif, nouveau goulot = Fraiseuse 5 min
    assert res.poste_goulot.machine == "Fraiseuse"
    assert res.capacite_prod == pytest.approx(86.4, abs=0.5)


def test_scenario_s3_reequilibrage(postes_pdf, params_pdf):
    p, par = scenarios.scenario_s3_reequilibrage(postes_pdf, params_pdf)
    res = calculs.simuler(p, par, "S3")
    # Tour passe à 4 min, goulot devient Fraiseuse 5 min
    assert res.poste_goulot.machine == "Fraiseuse"
    assert res.capacite_prod == pytest.approx(86.4, abs=0.5)


def test_scenario_s4_industrie40(postes_pdf, params_pdf):
    p, par = scenarios.scenario_s4_industrie40(postes_pdf, params_pdf)
    res = calculs.simuler(p, par, "S4")
    assert res.capacite_prod == pytest.approx(93.0, abs=0.5)
    assert res.pieces_conformes == pytest.approx(92.1, abs=0.5)
    assert res.trs == pytest.approx(0.961, abs=0.01)


# ============================================================
# Tests alertes
# ============================================================

def test_alertes_baseline_critiques(postes_pdf, params_pdf):
    res = calculs.simuler(postes_pdf, params_pdf)
    alerts = alertes.generer_alertes(res)
    codes = [a.code for a in alerts]
    assert "DEFICIT_DEMANDE" in codes
    assert "GOULOT_SATURE" in codes
    assert "ARRETS_ELEVES" in codes
    assert "REBUT_ELEVE" in codes


def test_alertes_s4_aucun_deficit(postes_pdf, params_pdf):
    p, par = scenarios.scenario_s4_industrie40(postes_pdf, params_pdf)
    res = calculs.simuler(p, par)
    alerts = alertes.generer_alertes(res)
    codes = [a.code for a in alerts]
    assert "DEFICIT_DEMANDE" not in codes


# ============================================================
# Tests économie
# ============================================================

def test_economie_s4(postes_pdf, params_pdf):
    res_base = calculs.simuler(*scenarios.scenario_baseline(postes_pdf, params_pdf))
    p, par = scenarios.scenario_s4_industrie40(postes_pdf, params_pdf)
    res_s4 = calculs.simuler(p, par)
    eco = scenarios.calculer_economie(
        res_base.pieces_conformes, res_s4.pieces_conformes,
        params_pdf, scenarios.INVESTISSEMENTS["S4 - Industrie 4.0"]
    )
    # PDF : gain ≈ 195 360 €/an, ROI ≈ 388%
    assert eco["gain_annuel"] == pytest.approx(195000, abs=5000)
    assert eco["roi_pct"] > 300
