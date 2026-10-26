"""Log the Arduino temperature stream to CSV and add manual gauge readings/notes.

Run:   python -m software.logger.serial_logger --port COM3         (Windows)
       python -m software.logger.serial_logger --port /dev/ttyUSB0  (Linux/macOS)
While running, type and press Enter:
   g -18.5 inHg      record a compound-gauge reading (value and unit)
   n lid torqued     record a free-text note
   q                 quit
Output CSV columns: wall_time,t_s,temp_c,state,event,value
"""
from __future__ import annotations

import argparse
import csv
import datetime
import pathlib
import sys
import threading

import serial  # pyserial


def parse_line(line: str):
    """'12.0,431.5,OK' -> (12.0, 431.5, 'OK'); None for comments/garbage."""
    line = line.strip()
    if not line or line.startswith("#") or line.startswith("t_s"):
        return None
    parts = line.split(",")
    if len(parts) != 3:
        return None
    try:
        t = float(parts[0])
        temp = float("nan") if parts[1].lower() == "nan" else float(parts[1])
    except ValueError:
        return None
    return t, temp, parts[2]


def main(argv=None) -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    ap.add_argument("--port", required=True)
    ap.add_argument("--baud", type=int, default=9600)
    ap.add_argument("--out", default="data/runs")
    ap.add_argument("--tag", default="run")
    a = ap.parse_args(argv)

    out = pathlib.Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    path = out / f"{a.tag}_{datetime.datetime.now():%Y%m%d_%H%M%S}.csv"
    stop = threading.Event()
    lock = threading.Lock()
    last = {"t": 0.0, "temp": float("nan"), "state": ""}

    with open(path, "w", newline="") as f, serial.Serial(a.port, a.baud, timeout=2) as ser:
        w = csv.writer(f)
        w.writerow(["wall_time", "t_s", "temp_c", "state", "event", "value"])

        def write(event, value=""):
            with lock:
                w.writerow([datetime.datetime.now().isoformat(timespec="seconds"),
                            last["t"], last["temp"], last["state"], event, value])
                f.flush()

        def keyboard():
            for raw in sys.stdin:
                cmd = raw.strip()
                if cmd == "q":
                    stop.set()
                    return
                if cmd.startswith("g "):
                    write("gauge", cmd[2:])
                elif cmd.startswith("n "):
                    write("note", cmd[2:])

        threading.Thread(target=keyboard, daemon=True).start()
        print(f"Logging to {path}  (g <value unit>, n <note>, q to quit)")
        while not stop.is_set():
            rec = parse_line(ser.readline().decode(errors="ignore"))
            if rec is None:
                continue
            last.update(t=rec[0], temp=rec[1], state=rec[2])
            write("temp")
            print(f"{rec[0]:8.1f} s  {rec[1]:7.1f} C  {rec[2]}")
            if rec[2] in ("FAULT", "OVER_TEMP"):
                print("*** ALERT: check thermocouple / reduce dimmer setting ***")


if __name__ == "__main__":
    main()
