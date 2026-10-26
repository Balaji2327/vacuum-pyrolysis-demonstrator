"""TEG demo electrical output from multimeter readings.
Usage: python -m software.analysis.teg_output --v 0.9 --r 10
       python -m software.analysis.teg_output --v 0.9 --i 0.085"""
from __future__ import annotations

import argparse


def power_w(v: float, r_ohm: float | None = None, i_a: float | None = None) -> float:
    if i_a is not None:
        return v * i_a
    if r_ohm:
        return v * v / r_ohm
    raise ValueError("give a load resistance or a current")


def main(argv=None) -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--v", type=float, required=True)
    ap.add_argument("--r", type=float)
    ap.add_argument("--i", type=float)
    a = ap.parse_args(argv)
    print(f"Output power: {power_w(a.v, a.r, a.i)*1000:.1f} mW "
          "(log hot-side temperature too; it must stay within the module rating)")


if __name__ == "__main__":
    main()
