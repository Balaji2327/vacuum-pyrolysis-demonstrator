# Vacuum-Assisted Batch Pyrolysis Demonstrator (500 g, benchtop)

Kanthal resistive-coil heated pyrolysis of HDPE/PP waste with vacuum O2 exclusion, two-stage
condensation for fuel oil, a gas clean-up train, and a thermoelectric (TEG) demonstration
that turns burnt pyrolysis gas into measurable DC output. Budget target: INR 10,000.

Sri Sairam Engineering College, Chennai - Dept. of Mechanical and Automation Engineering.

> **Safety first.** This is a hot, potentially pressurised, flammable-gas system. Do not heat
> without an independent pressure relief device, a documented pressure rating for the
> modified vessel, outdoor/fume-extracted setup and faculty supervision. The firmware is
> **monitoring only** and is not an over-temperature protection system.

## Process flow
```
Hand vacuum pump -> [isolation valve] -> SS vessel (Kanthal coil, dimmer) + PRD + compound gauge
   vessel -> Cu coil (water bath) -> Cu coil (ice bath) -> oil jar -> NaOH scrubber
          -> silica gel -> activated carbon -> gas bag -> burner -> heat plate -> TEG -> LED/motor
Thermocouple (K) -> MAX6675 -> Arduino -> USB -> serial_logger.py -> CSV -> plot_run.py
```

## Repository layout
| Path | Purpose |
|---|---|
| `firmware/temp_logger/` | Arduino sketch: reads MAX6675, prints `t_s,temp_c,state` CSV |
| `software/calc/sizing.py` | Energy, Kanthal coil, gas yield, O2 exclusion, blocked-outlet pressure, BOM total |
| `software/gates/gate_checklist.py` | Interactive gated test sequence (stops at first failed gate, logs JSON) |
| `software/logger/serial_logger.py` | Serial -> CSV logger with manual gauge/notes entry |
| `software/analysis/` | `plot_run.py`, `mass_balance.py`, `teg_output.py` |
| `data/bom.csv` | Bill of materials (mandatory total INR 7,950) |
| `docs/RUNBOOK.md` | Build order and test-day procedure |
| `tests/` | pytest suite (CI via GitHub Actions) |

## Quick start
```bash
python -m venv .venv && source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pytest -q                                             # 16 tests
python -m software.calc.sizing                        # design numbers
```
Flash `firmware/temp_logger/temp_logger.ino` (Arduino IDE, install *MAX6675 library* by Adafruit).

Test day:
```bash
python -m software.gates.gate_checklist               # must pass before heating
python -m software.logger.serial_logger --port COM3 --tag batch1
python -m software.analysis.plot_run data/runs/batch1_*.csv --save batch1.png
python -m software.analysis.mass_balance --feed 500 --oil 390 --char 28
python -m software.analysis.teg_output --v 0.9 --r 10
```

## Honest limitations
- 80/15/5 oil/gas/char split, ~58 L gas and 677 kJ heating energy are **sizing estimates**; measure them.
- Raw gas is a light-hydrocarbon mix; it is **not** H2-rich syngas without GC analysis and reforming.
- Activated-carbon stage is single-pass polishing, not PSA. TEG replaces a PEM fuel cell.
- Vacuum gives demonstration-level inertion (~140 mL residual O2 per 2 L headspace; ~46 mL with N2 backfill).

## License
MIT
