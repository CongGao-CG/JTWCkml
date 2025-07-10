#!/usr/bin/env python3
"""
jtwc2hurdat2.py – Convert a JTWC best-track (B-deck) file to HURDAT2.
"""

import csv
import sys
from collections import OrderedDict


# ───────────── helpers ─────────────
def convert_system(code: str) -> str:
    return {
        "DB": "DB",
        "TD": "TD",
        "TS": "TS",
        "TY": "HU",
        "HU": "HU",
        "EX": "EX",
        "LO": "LO",
    }.get(code.strip().upper(), "XX")


def fix_coord(raw: str) -> str:
    raw = raw.strip().upper()
    if not raw:
        return ""
    hemi = raw[-1]
    value = int(raw[:-1]) / 10.0
    return f"{value:.1f}{hemi}"


def s_int(val, default=0):
    try:
        return int(val)
    except (ValueError, TypeError):
        return default


# ───────────── main ─────────────
def main(path: str) -> None:
    rows = []
    with open(path, newline="") as fh:
        for r in csv.reader(fh):
            if len(r) < 17 or len(r[2].strip()) < 10:
                continue
            rows.append([c.strip() for c in r])

    if not rows:
        print("No valid rows found in file.")
        return

    rows.sort(key=lambda r: r[2])

    basin, storm_num, year = rows[0][0], rows[0][1].zfill(2), rows[0][2][:4]

    banned = {"INVEST", "THREE", "TRANSITIONED", ""}
    storm_name = "UNNAMED"
    for rec in reversed(rows):
        if len(rec) > 27:
            name = rec[27].upper()
            if name not in banned:
                storm_name = name
                break

    agg = OrderedDict()
    for rec in rows:
        dt = rec[2][:10]        # yyyymmddhh
        thresh = rec[11] or "0"

        entry = agg.setdefault(
            dt,
            {
                "lat": rec[6],
                "lon": rec[7],
                "vmax": rec[8],
                "pmin": rec[9],
                "sys": rec[10],
                "r34": [0, 0, 0, 0],
                "r50": [0, 0, 0, 0],
                "r64": [0, 0, 0, 0],
            },
        )

        if thresh in {"34", "50", "64"}:
            entry[f"r{thresh}"][:] = list(map(s_int, rec[13:17]))

    outname = f"{basin}{storm_num}{year}_{storm_name}_{len(agg)}.txt"
    with open(outname, "w") as out:
        # 19-wide name field; 7-wide record count per HURDAT2 spec
        out.write(f"{basin}{storm_num}{year},{storm_name:>19},{len(agg):7d},\n")

        def fmt(arr):               # 4-wide radii values
            return [f"{v:4d}" for v in arr]

        for dt, info in agg.items():
            date, hhmm = dt[:8], dt[8:] + "00"
            core = [
                date,
                hhmm,
                " ",
                convert_system(info["sys"]),
                fix_coord(info["lat"]),
                fix_coord(info["lon"]),
                f"{int(info['vmax']):3d}",
                f"{int(info['pmin']):4d}",
            ]
            radii = fmt(info["r34"]) + fmt(info["r50"]) + fmt(info["r64"])
            out.write(", ".join(core) + ", " + ", ".join(radii) + ", -999\n")

    print(f"Wrote {outname}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python jtwc2hurdat2.py <B-deck file>")
        sys.exit(1)
    main(sys.argv[1])