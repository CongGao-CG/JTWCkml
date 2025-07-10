#!/usr/bin/env python3
"""
jtwc2hurdat2.py – Convert a JTWC best-track (B-deck) file to HURDAT2.

Example
-------
    python jtwc2hurdat2.py  bcp032015.dat
"""

import csv
import sys
from collections import OrderedDict


# ────────────────── utility helpers ──────────────────
def convert_system(code: str) -> str:
    """Translate JTWC system codes to the HURDAT2 equivalents."""
    return {
        "DB": "DB",
        "TD": "TD",
        "TS": "TS",
        "TY": "HU",  # JTWC TY & HU → HU
        "HU": "HU",
        "EX": "EX",
        "LO": "LO",
    }.get(code.strip().upper(), "XX")


def fix_coord(raw: str) -> str:
    """
    Turn '185N' → '18.5N'   (tenths of a degree, hemisphere letter at end).
    """
    raw = raw.strip().upper()
    if not raw:
        return ""
    hemi = raw[-1]
    value = int(raw[:-1]) / 10.0
    return f"{value:.1f}{hemi}"


def safe_int(val, default=0):
    try:
        return int(val)
    except (ValueError, TypeError):
        return default


# ────────────────────── main converter ──────────────────────
def main(infile: str) -> None:
    rows = []
    with open(infile, newline="") as fh:
        rdr = csv.reader(fh)
        for r in rdr:
            # Require at least 17 columns and a 10-digit yyyymmddhh timestamp
            if len(r) < 17 or len(r[2].strip()) < 10:
                continue
            rows.append([c.strip() for c in r])

    if not rows:
        print("No valid records found – is this a JTWC B-deck?")
        return

    # chronological order
    rows.sort(key=lambda rec: rec[2])

    # ── basic header info ─────────────────────────────
    basin = rows[0][0]
    storm_num = rows[0][1].zfill(2)
    year = rows[0][2][:4]

    # last non-generic storm name in column 28 (idx 27)
    banned = {"INVEST", "THREE", "TRANSITIONED", ""}
    storm_name = "UNNAMED"
    for rec in reversed(rows):
        if len(rec) > 27:
            name = rec[27].strip().upper()
            if name not in banned:
                storm_name = name
                break

    # ── aggregate by synoptic time (yyymmddhh) ────────
    agg: OrderedDict[str, dict] = OrderedDict()

    for rec in rows:
        dt = rec[2][:10]          # yyyymmddhh
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
            ne, se, sw, nw = map(safe_int, rec[13:17])
            entry[f"r{thresh}"][:] = [ne, se, sw, nw]

    # ── write HURDAT2 ─────────────────────────────────
    outname = f"{basin}{storm_num}{year}_{storm_name}_{len(agg)}.txt"
    with open(outname, "w") as out:
        # header
        out.write(f"{basin}{storm_num}{year},{storm_name:>20},{len(agg):5d},\n")

        for dt, info in agg.items():
            date = dt[:8]
            hhmm = dt[8:10] + "00"  # JTWC has only hh; add mm=00
            core = [
                date,
                hhmm,
                " ",                                   # blank record-ID field
                convert_system(info["sys"]),
                fix_coord(info["lat"]),
                fix_coord(info["lon"]),
                f"{info['vmax']:>3}",
                f"{info['pmin']:>4}",
            ]

            def fmt(arr):
                return [f"{v:5d}" for v in arr]

            radii = fmt(info["r34"]) + fmt(info["r50"]) + fmt(info["r64"])
            out.write(", ".join(core) + ", " +
                      ", ".join(radii) + ", -999\n")

    print(f"Wrote {outname}")


# ───────────────────────── entry point ─────────────────────────
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python jtwc2hurdat2.py  <JTWC_deck.dat|txt>")
        sys.exit(1)
    main(sys.argv[1])