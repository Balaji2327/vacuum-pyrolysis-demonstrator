"""Interactive gated test checklist. Enforces the test order: a failed gate stops the run.
Usage:  python -m software.gates.gate_checklist
Writes a timestamped JSON record to data/gate_logs/ (ignored by git)."""
from __future__ import annotations

import datetime
import json
import pathlib
from typing import Callable

from software.calc.sizing import vacuum_hold_ok

PRE_GATES = [
    "Feedstock is HDPE/PP only; PVC screened out",
    "Pressure relief device fitted and verified independently of the gauge",
    "Vessel/fitting/PRD rating for the MODIFIED assembly documented and signed off by faculty safety authority",
    "TEG heat collector plate thermally isolates TEC1-12706 (hot side stays within rated limit)",
    "Firmware flashed and temperature readout verified against a reference",
    "Test site is outdoors or under approved fume extraction; supervisor present; emergency shutoff known",
]

STAGES = [
    ("1  Cold test", "Soap-water test: zero visible leaks at every joint?"),
    ("2a Vacuum-hold test", "__VACUUM__"),
    ("2b Heater-only test", "Empty vessel to 300 C: thermocouple tracks dimmer, no gasket weep, no shorts?"),
    ("3  Inertion", "Feed loaded, target vacuum reached AND held with valve closed, pump physically disconnected?"),
    ("4  Live batch", "Gauge within the documented safe range for the assembly, supervisor present?"),
    ("5  Gas capture", "Bag filled without strain on fittings?"),
    ("6  TEG demo", "Stable flame on collector plate, TEG hot side within limit, no leak at jet?"),
]


def _yes(ask: Callable[[str], str], q: str) -> bool:
    return ask(f"{q} [y/N]: ").strip().lower() in ("y", "yes")


def run(ask: Callable[[str], str] = input, out_dir: str = "data/gate_logs") -> dict:
    log = {"started": datetime.datetime.now().isoformat(timespec="seconds"),
           "pre_gates": [], "stages": [], "result": "INCOMPLETE"}

    def finish(result: str) -> dict:
        log["result"] = result
        path = pathlib.Path(out_dir)
        path.mkdir(parents=True, exist_ok=True)
        fn = path / f"gates_{datetime.datetime.now():%Y%m%d_%H%M%S}.json"
        fn.write_text(json.dumps(log, indent=2))
        print(f"\n{result}. Log: {fn}")
        return log

    for g in PRE_GATES:
        ok = _yes(ask, f"PRE-GATE: {g}")
        log["pre_gates"].append({"gate": g, "pass": ok})
        if not ok:
            return finish(f"STOP - pre-gate failed: {g}")

    for name, q in STAGES:
        if q == "__VACUUM__":
            s = float(ask("Stage 2a start vacuum (inHg, e.g. 20): "))
            e = float(ask("Stage 2a end vacuum (inHg): "))
            m = float(ask("Hold time (minutes): "))
            ok = vacuum_hold_ok(s, e, m)
            detail = {"start_inhg": s, "end_inhg": e, "minutes": m}
        else:
            ok, detail = _yes(ask, f"STAGE {name}: {q}"), {}
        log["stages"].append({"stage": name, "pass": ok, **detail})
        if not ok:
            return finish(f"STOP - stage failed: {name}")
    return finish("ALL GATES PASSED")


if __name__ == "__main__":
    run()
