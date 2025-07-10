#!/usr/bin/env python3
"""
JTWC2HURDAT2.py – Convert JTWC B-deck files (even sparse ones) to HURDAT2.
"""

import csv
import sys
from collections import OrderedDict
from pathlib import Path


# ───────────── helpers ─────────────
def convert_system(code: str, vmax: int) -> str:
    """Map JTWC system code to HURDAT2 – derive from wind if missing."""
    code = (code or "").strip().upper()
    if not code:
        # derive from 1-min sustained wind (kt) if code blank
        if vmax < 34:
            code = "LO"
        elif vmax < 64:
            code = "TS"
        else:
            code = "HU"
    return {
        "DB": "DB",
        "TD": "TD",
        "TS": "TS",
        "TY": "HU",
        "HU": "HU",
        "EX": "EX",
        "LO": "LO",
    }.get(code, "XX")


def fix_coord(raw: str) -> str:
    """Turn '152S' → '15.2S' etc.; return blank if missing."""
    raw = raw.strip().upper()
    if not raw:
        return ""
    hemi = raw[-1]
    try:
        value = int(raw[:-1]) / 10.0
    except ValueError:
        return ""
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
        rdr = csv.reader(fh)
        for r in rdr:
            # minimum: basin, number, yyyymmddhh...
            if len(r) < 3 or len(r[2].strip()) < 10:
                continue
            r = [c.strip() for c in r]
            # pad to at least 30 columns so we can index safely
            r += [""] * (30 - len(r))
            rows.append(r)

    if not rows:
        print("No valid rows found in file.")
        return

    rows.sort(key=lambda r: r[2])  # chronological

    basin, storm_num, year = rows[0][0], rows[0][1].zfill(2), rows[0][2][:4]

    # try to get a name; otherwise UNNAMED
    banned = {"INVEST", "THREE", "TRANSITIONED", ""}
    storm_name = "UNNAMED"
    for rec in reversed(rows):
        name = (rec[27] if len(rec) > 27 else "").upper()
        if name and name not in banned:
            storm_name = name
            break

    # aggregate by timestamp (first 10 chars = yyyymmddhh)
    agg = OrderedDict()
    for rec in rows:
        dt = rec[2][:10]
        vmax = s_int(rec[8])
        entry = agg.setdefault(
            dt,
            {
                "lat": rec[6],
                "lon": rec[7],
                "vmax": vmax,
                "pmin": s_int(rec[9], 0) or 0,
                "sys": rec[10],
                "r34": [0, 0, 0, 0],
                "r50": [0, 0, 0, 0],
                "r64": [0, 0, 0, 0],
            },
        )

        thresh = (rec[11] or "0").strip()
        if thresh in {"34", "50", "64"}:
            # rec[13:17] may be blank – convert safely
            radii = [s_int(x) for x in rec[13:17]]
            entry[f"r{thresh}"][:] = radii

    outdir = Path(__file__).resolve().parent / "../single_TC"
    outdir.mkdir(parents=True, exist_ok=True)
    outname = outdir / f"{basin}{storm_num}{year}_{storm_name}_{len(agg)}.txt"

    with open(outname, "w") as out:
        # header – 19-wide name field; 7-wide record count
        out.write(f"{basin}{storm_num}{year},{storm_name:>19},{len(agg):7d},\n")

        def fmt(arr):
            return [f"{v:5d}" for v in arr]  # 5-wide radii

        for dt, info in agg.items():
            date, hhmm = dt[:8], dt[8:] + "00"
            lat = f"{fix_coord(info['lat']):>5}"  # fixed width
            lon = f"{fix_coord(info['lon']):>6}"
            line = [
                date,
                hhmm,
                " ",
                convert_system(info["sys"], info["vmax"]),
                lat,
                lon,
                f"{info['vmax']:3d}",
                f"{info['pmin']:4d}",
            ]
            radii = fmt(info["r34"]) + fmt(info["r50"]) + fmt(info["r64"])
            out.write(", ".join(line) + ", " + ", ".join(radii) + ", -999\n")

    print(f"Wrote {outname}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python JTWC2HURDAT2.py <B-deck file>")
        sys.exit(1)
    main(sys.argv[1])