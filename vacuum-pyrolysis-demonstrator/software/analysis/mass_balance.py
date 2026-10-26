"""Measured product split (gas by difference) vs the nominal 80/15/5 oil/gas/char assumption.
Usage: python -m software.analysis.mass_balance --feed 500 --oil 390 --char 28 [--residue 6]"""
from __future__ import annotations

import argparse

NOMINAL = {"oil": 0.80, "gas": 0.15, "char": 0.05}


def balance(feed_g: float, oil_g: float, char_g: float, residue_g: float = 0.0) -> dict:
    if feed_g <= 0:
        raise ValueError("feed must be positive")
    gas_g = feed_g - oil_g - char_g - residue_g
    return {"oil": oil_g / feed_g, "char": char_g / feed_g, "gas_by_difference": gas_g / feed_g,
            "warning": "negative gas by difference - re-weigh" if gas_g < 0 else ""}


def main(argv=None) -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--feed", type=float, required=True)
    ap.add_argument("--oil", type=float, required=True)
    ap.add_argument("--char", type=float, required=True)
    ap.add_argument("--residue", type=float, default=0.0, help="wax/tar left in lines (g)")
    a = ap.parse_args(argv)
    r = balance(a.feed, a.oil, a.char, a.residue)
    print(f"oil  {r['oil']:.1%}  (nominal {NOMINAL['oil']:.0%})")
    print(f"char {r['char']:.1%}  (nominal {NOMINAL['char']:.0%})")
    print(f"gas  {r['gas_by_difference']:.1%}  (nominal {NOMINAL['gas']:.0%}, by difference)")
    if r["warning"]:
        print("WARNING:", r["warning"])


if __name__ == "__main__":
    main()
