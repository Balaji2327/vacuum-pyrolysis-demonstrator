"""First-principles sizing for the 500 g vacuum-assisted batch pyrolysis demonstrator.

All numbers are PRELIMINARY SIZING ESTIMATES, not measured results. Product split, gas
molecular weight and heater efficiency must be confirmed experimentally.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

STP_MOLAR_VOLUME_L = 22.414      # L/mol at 0 C, 1 atm
R_L_ATM = 0.082057               # L*atm/(mol*K)
KANTHAL_A1_RESISTIVITY = 1.45e-6  # ohm*m at 20 C
ATM_INHG = 29.92
O2_FRACTION_AIR = 0.2095


@dataclass
class EnergyInputs:
    mass_kg: float = 0.5
    cp_j_per_kgk: float = 2300.0
    t_start_c: float = 30.0
    t_end_c: float = 450.0
    cracking_j: float = 100_000.0
    vessel_thermal_j: float = 94_000.0


def energy_budget(i: EnergyInputs | None = None) -> dict:
    i = i or EnergyInputs()
    sensible = i.mass_kg * i.cp_j_per_kgk * (i.t_end_c - i.t_start_c)
    total = sensible + i.cracking_j + i.vessel_thermal_j
    return {"sensible_j": sensible, "cracking_j": i.cracking_j,
            "vessel_j": i.vessel_thermal_j, "total_j": total, "total_kj": total / 1000}


def heat_up_time_min(energy_j: float, power_w: float, efficiency: float = 1.0) -> float:
    """Minutes to deliver energy_j at power_w with heater-to-feed efficiency in (0, 1]."""
    if not 0 < efficiency <= 1:
        raise ValueError("efficiency must be in (0, 1]")
    return energy_j / (power_w * efficiency) / 60.0


def kanthal_design(wire_dia_mm: float = 0.56, length_m: float = 30.0, mains_v: float = 230.0,
                   vessel_dia_mm: float = 140.0, mica_thk_mm: float = 1.0,
                   pitch_mm: float = 2.0) -> dict:
    area_m2 = math.pi * (wire_dia_mm / 2000) ** 2
    resistance = KANTHAL_A1_RESISTIVITY / area_m2 * length_m
    power = mains_v ** 2 / resistance
    surface_cm2 = math.pi * (wire_dia_mm / 10) * (length_m * 100)
    mean_dia_mm = vessel_dia_mm + 2 * mica_thk_mm + wire_dia_mm
    turns = length_m / (math.pi * mean_dia_mm / 1000)
    return {"resistance_ohm": resistance, "power_w": power, "current_a": mains_v / resistance,
            "surface_loading_w_cm2": power / surface_cm2, "turns": turns,
            "coil_height_mm": turns * pitch_mm}


def gas_yield(feed_g: float = 500.0, gas_fraction: float = 0.15, mw_g_mol: float = 29.0) -> dict:
    gas_g = feed_g * gas_fraction
    mol = gas_g / mw_g_mol
    return {"gas_g": gas_g, "mol": mol, "litres_stp": mol * STP_MOLAR_VOLUME_L}


def blocked_outlet_pressure_atm(gas_g: float, mw_g_mol: float, temp_c: float,
                                headspace_l: float) -> float:
    """Worst case: all generated gas trapped in the headspace (outlet blocked). Ideal-gas
    upper bound - shows why the PRD and an unobstructed vapour line are mandatory."""
    return (gas_g / mw_g_mol) * R_L_ATM * (temp_c + 273.15) / headspace_l


def o2_after_evacuation(headspace_l: float = 2.0, vacuum_inhg: float = 20.0,
                        cycles: int = 1, atm_inhg: float = ATM_INHG) -> dict:
    """Residual O2 after `cycles` evacuations; cycles > 1 assume N2 backfill between them."""
    if not 0 <= vacuum_inhg < atm_inhg:
        raise ValueError("vacuum_inhg must be between 0 and atmospheric")
    frac = (atm_inhg - vacuum_inhg) / atm_inhg
    o2_start_ml = headspace_l * 1000 * O2_FRACTION_AIR
    return {"fraction_per_cycle": frac, "o2_start_ml": o2_start_ml,
            "o2_residual_ml": o2_start_ml * frac ** cycles}


def vacuum_hold_ok(start_inhg: float, end_inhg: float, minutes: float,
                   max_decay_inhg: float = 5.0, window_min: float = 10.0) -> bool:
    """Gate 2a: vacuum decay (scaled to a 10-minute window) must stay below the limit."""
    if minutes <= 0:
        raise ValueError("minutes must be > 0")
    decay = max(0.0, start_inhg - end_inhg) * (window_min / minutes)
    return decay < max_decay_inhg


def bom_total(csv_path: str, mandatory_only: bool = True) -> int:
    import csv
    total = 0
    with open(csv_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if mandatory_only and row["optional"].strip().lower() == "yes":
                continue
            total += int(row["cost_inr"])
    return total


def report() -> str:
    e = energy_budget()
    k = kanthal_design()
    g = gas_yield()
    o1, o2 = o2_after_evacuation(cycles=1), o2_after_evacuation(cycles=2)
    p_blk = blocked_outlet_pressure_atm(g["gas_g"], 29.0, 480.0, 2.0)
    return "\n".join([
        "=== Heating energy (500 g, 30->450 C) ===",
        f"Total ~ {e['total_kj']:.0f} kJ (sensible {e['sensible_j']/1000:.0f} + cracking "
        f"{e['cracking_j']/1000:.0f} + vessel {e['vessel_j']/1000:.0f})",
        f"Ideal time at {k['power_w']:.0f} W: {heat_up_time_min(e['total_j'], k['power_w']):.0f} min; "
        f"at 60% efficiency: {heat_up_time_min(e['total_j'], k['power_w'], 0.6):.0f} min (MEASURE!)",
        "=== Kanthal A1 24 SWG, 30 m, 230 V ===",
        f"R = {k['resistance_ohm']:.0f} ohm, P = {k['power_w']:.0f} W, I = {k['current_a']:.2f} A, "
        f"loading = {k['surface_loading_w_cm2']:.2f} W/cm2",
        f"Turns ~ {k['turns']:.0f}, coil height ~ {k['coil_height_mm']:.0f} mm at 2 mm pitch",
        "=== Gas (nominal 15 %, MW 29 - ASSUMED) ===",
        f"{g['gas_g']:.0f} g -> {g['litres_stp']:.0f} L at STP",
        f"Worst-case blocked-outlet pressure ~ {p_blk:.0f} atm -> PRD + clear vapour line mandatory",
        "=== O2 exclusion (2 L headspace, -20 inHg) ===",
        f"Start {o1['o2_start_ml']:.0f} mL O2 -> 1 evacuation {o1['o2_residual_ml']:.0f} mL; "
        f"N2 backfill + 2nd evacuation {o2['o2_residual_ml']:.0f} mL (demonstration-level inertion)",
    ])


if __name__ == "__main__":
    print(report())
