import json
import pathlib

import numpy as np

from software.analysis import mass_balance, plot_run, teg_output
from software.gates import gate_checklist
from software.logger.serial_logger import parse_line


def test_parse_line():
    assert parse_line("12.0,431.5,OK") == (12.0, 431.5, "OK")
    assert parse_line("# comment") is None
    assert parse_line("t_s,temp_c,state") is None
    t, temp, st = parse_line("3.0,nan,FAULT")
    assert np.isnan(temp) and st == "FAULT"
    assert parse_line("garbage") is None


def test_mass_balance():
    r = mass_balance.balance(500, 390, 28, 6)
    assert round(r["oil"], 2) == 0.78 and round(r["gas_by_difference"], 3) == 0.152
    assert mass_balance.balance(500, 400, 100, 50)["warning"]


def test_teg_power():
    assert abs(teg_output.power_w(1.0, r_ohm=10) - 0.1) < 1e-9
    assert abs(teg_output.power_w(1.0, i_a=0.05) - 0.05) < 1e-9


def test_analyse_run():
    t = np.arange(0, 3600, 5.0)
    T = np.minimum(30 + t * 0.15, 480)
    res = plot_run.analyse(t, T)
    assert res["peak_c"] == 480 and res["minutes_in_band"] > 5
    assert 8 < res["ramp_rate_c_per_min"] < 10


def _answers(seq):
    it = iter(seq)
    return lambda prompt: next(it)


def test_gates_all_pass(tmp_path):
    answers = ["y"] * 6 + ["y", "20", "18", "10"] + ["y"] * 6
    # order: 6 pre-gates, stage1 y, 2a (3 numbers), then 2b..6 = 5 y
    answers = ["y"] * 6 + ["y"] + ["20", "18", "10"] + ["y"] * 5
    log = gate_checklist.run(_answers(answers), str(tmp_path))
    assert log["result"] == "ALL GATES PASSED"
    assert list(pathlib.Path(tmp_path).glob("*.json"))


def test_gates_stop_on_vacuum_failure(tmp_path):
    answers = ["y"] * 6 + ["y"] + ["20", "10", "10"]
    log = gate_checklist.run(_answers(answers), str(tmp_path))
    assert log["result"].startswith("STOP")
    data = json.loads(next(pathlib.Path(tmp_path).glob("*.json")).read_text())
    assert data["stages"][-1]["pass"] is False


def test_gates_stop_on_prefail(tmp_path):
    log = gate_checklist.run(_answers(["y", "n"]), str(tmp_path))
    assert "pre-gate" in log["result"]
