# Runbook: build order and test day

## Build order (each step has a pass criterion)
1. Vessel: drill vapour outlet, PRD/gauge port, vacuum port (+ needle valve), thermocouple gland.
2. Coil: mica wrap, wind ~67 turns Kanthal 24 SWG at 2 mm pitch, ceramic beads on leads, wool + foil.
   Pass: resistance 170-185 ohm cold.
3. Heater only through dimmer + fuse + switch. Pass: no short, temperature tracks dimmer.
4. Electronics: MAX6675 -> Arduino, flash sketch, compare with a reference thermometer in boiling water (~100 C).
5. Gas train and condensers; soap-water leak test every joint.
6. Vacuum-hold test (empty vessel): pump to ~-20 inHg, close valve, disconnect pump.
   Pass: decay < 5 inHg in 10 min. If not, re-seat gasket, re-torque evenly, retest.
7. TEG station: collector plate isolating the TEC1-12706 from direct flame; hot side within module rating.
8. Run `python -m software.gates.gate_checklist` - all pre-gates must be answered yes.

## Test day
1. Outdoors/fume extraction, supervisor present, fire extinguisher at hand, no ignition source near bag.
2. Weigh feed (500 g HDPE/PP, no PVC). Load, seal, torque evenly.
3. Evacuate, close valve, **disconnect pump** before the heater is switched on. Optional: N2 backfill + 2nd evacuation.
4. Start `serial_logger`; ramp with dimmer, aiming for a steady rise; log gauge readings with `g <value unit>` every ~5 min.
5. Hold 450-500 C; stop heating when oil drip slows. Let cool fully before opening.
6. Capture only the final 10-15 min of gas in the bag; burn only outdoors at low flow; record TEG V/I.
7. Weigh oil, char, line residue -> `mass_balance`. Plot run. Commit the CSV summary (not raw secrets).

## Abort triggers
Gauge climbing fast, leak smell, flame at joints, FAULT/OVER_TEMP in logger: switch heater off at the isolator, step back, let it cool.
