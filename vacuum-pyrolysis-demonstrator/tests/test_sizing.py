import math
import pathlib

import pytest

from software.calc import sizing as s

BOM = pathlib.Path(__file__).parent.parent / "data" / "bom.csv"


def test_energy_budget_matches_677kj():
    assert s.energy_budget()["total_kj"] == pytest.approx(677, abs=1)


def test_kanthal_design():
    k = s.kanthal_design()
    assert k["resistance_ohm"] == pytest.approx(176, abs=2)
    assert k["power_w"] == pytest.approx(300, abs=5)
    assert k["surface_loading_w_cm2"] == pytest.approx(0.57, abs=0.02)
    assert 64 <= k["turns"] <= 70


def test_gas_yield_range():
    assert 55 <= s.gas_yield()["litres_stp"] <= 62


def test_o2_reduction():
    one = s.o2_after_evacuation(cycles=1)["o2_residual_ml"]
    two = s.o2_after_evacuation(cycles=2)["o2_residual_ml"]
    assert 120 <= one <= 150 and 35 <= two <= 55


def test_invalid_vacuum():
    with pytest.raises(ValueError):
        s.o2_after_evacuation(vacuum_inhg=40)


def test_vacuum_hold_gate():
    assert s.vacuum_hold_ok(20, 17, 10)
    assert not s.vacuum_hold_ok(20, 14, 10)
    assert not s.vacuum_hold_ok(20, 17, 5)  # 3 inHg in 5 min -> 6 per 10 min


def test_blocked_pressure_is_large():
    assert s.blocked_outlet_pressure_atm(75, 29, 480, 2.0) > 10


def test_bom_totals():
    assert s.bom_total(str(BOM)) == 7950
    assert s.bom_total(str(BOM), mandatory_only=False) == 8050


def test_heat_up_time():
    assert s.heat_up_time_min(677_000, 300) == pytest.approx(37.6, abs=0.5)
    with pytest.raises(ValueError):
        s.heat_up_time_min(1, 300, 0)
