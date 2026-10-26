"""Plot a logged run; report ramp rate and time inside the 450-500 C band.
Usage: python -m software.analysis.plot_run data/runs/run_XXXX.csv [--save out.png]"""
from __future__ import annotations

import argparse
import csv

import numpy as np


def load(path: str):
    t, T, gauge = [], [], []
    with open(path, newline="") as f:
        for r in csv.DictReader(f):
            ts = float(r["t_s"])
            if r["event"] == "temp":
                temp = float(r["temp_c"])
                if not np.isnan(temp):
                    t.append(ts)
                    T.append(temp)
            elif r["event"] == "gauge":
                gauge.append((ts, r["value"]))
    return np.array(t), np.array(T), gauge


def analyse(t: np.ndarray, T: np.ndarray, lo: float = 450.0, hi: float = 500.0) -> dict:
    if len(t) < 3:
        raise ValueError("not enough data")
    ramp = (T >= 100) & (T <= 400)
    rate = float(np.polyfit(t[ramp] / 60, T[ramp], 1)[0]) if ramp.sum() > 5 else float("nan")
    dt = np.diff(t, prepend=t[0])
    in_band = float(dt[(T >= lo) & (T <= hi)].sum() / 60)
    return {"peak_c": float(T.max()), "ramp_rate_c_per_min": rate,
            "minutes_in_band": in_band, "duration_min": float((t[-1] - t[0]) / 60)}


def main(argv=None) -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("csv")
    ap.add_argument("--save")
    a = ap.parse_args(argv)
    t, T, gauge = load(a.csv)
    for k, v in analyse(t, T).items():
        print(f"{k:22s} {v:8.1f}")
    import matplotlib
    if a.save:
        matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.plot(t / 60, T, label="Reactor temp")
    ax.axhspan(450, 500, alpha=0.15, label="450-500 C band")
    for ts, val in gauge:
        ax.axvline(ts / 60, ls=":", lw=0.8)
        ax.annotate(val, (ts / 60, T.max() * 0.05), rotation=90, fontsize=7)
    ax.set_xlabel("Time (min)")
    ax.set_ylabel("Temperature (C)")
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    if a.save:
        fig.savefig(a.save, dpi=150)
    else:
        plt.show()


if __name__ == "__main__":
    main()
