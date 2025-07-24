#!/usr/bin/env python3
"""
JTWC2HURDAT2.py – Convert JTWC B-deck files (even sparse ones) to HURDAT2.

Changes
-------
* The storm identifier **{basin}{storm_num}{year}** is now taken from the
  **file-name** (case-insensitive), stripping the leading “b” and upper-casing
  the basin letters.  
  Example:  `bwp191998.txt`  →  **WP191998**
"""

import csv
import re
import sys
from collections import OrderedDict
from pathlib import Path

# ───────────── helpers ─────────────
_ID_RE = re.compile(r"""^b              # leading “b”
                        ([a-z]{2})      # basin code
                        (\d{2})         # storm number
                        (\d{4})         # year
                     """, re.I | re.X)


def id_from_filename(path: Path) -> tuple[str, str, str]:
    """Return (basin, num, year) parsed from the B-deck file name."""
    m = _ID_RE.match(path.stem)
    if not m:
        raise ValueError(f"Cannot parse basin/number/year from {path.name}")
    basin, num, year = m.groups()
    return basin.upper(), num, year


def convert_system(code: str, vmax: int) -> str:
    """Map JTWC system code to HURDAT2 – derive from wind if missing."""
    code = (code or "").strip().upper()
    if not code:
        code = "LO" if vmax < 34 else ("TS" if vmax < 64 else "HU")
    return {
        "DB": "DB",
        "TD": "TD",
        "TS": "TS",
        "TY": "HU",
        "ST": "HU",
        "HU": "HU",
        "EX": "EX",
        "LO": "LO",
    }.get(code, "XX")


def fix_coord(raw: str) -> str:
    """Turn '152S' → '15.2S'; blank if missing."""
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
def main(infile: str) -> None:
    path = Path(infile)
    try:
        basin, storm_num, year = id_from_filename(path)
    except ValueError as e:
        print(e)
        return

    rows: list[list[str]] = []
    with path.open(newline="") as fh:
        for r in csv.reader(fh):
            if len(r) < 3 or len(r[2].strip()) < 10:
                continue
            # pad so we can index safely
            r = [c.strip() for c in r] + [""] * (30 - len(r))
            rows.append(r)

    if not rows:
        print("No valid rows found in file.")
        return

    rows.sort(key=lambda r: r[2])  # chronological

    # ---- storm name ---------------------------------------------------------
    banned = {"INVEST", "NONAME", "TRANSITIONED", ""}
    storm_name = "UNNAMED"
    for rec in reversed(rows):
        name = (rec[27] if len(rec) > 27 else "").upper()
        if name and name not in banned:
            storm_name = name
            break

    # ---- aggregate by timestamp --------------------------------------------
    agg: OrderedDict[str, dict] = OrderedDict()
    for rec in rows:
        dt = rec[2][:10]                       # yyyymmddhh
        vmax = s_int(rec[8])
        entry = agg.setdefault(
            dt,
            {
                "lat": rec[6],
                "lon": rec[7],
                "vmax": vmax,
                "pmin": s_int(rec[9]),
                "sys": rec[10],
                "r34": [0, 0, 0, 0],
                "r50": [0, 0, 0, 0],
                "r64": [0, 0, 0, 0],
            },
        )
        thresh = (rec[11] or "0").strip()
        if thresh in {"34", "50", "64"}:
            entry[f"r{thresh}"][:] = [s_int(x) for x in rec[13:17]]

    # ---- output -------------------------------------------------------------
    outdir = Path(__file__).resolve().parent / "../single_TC"
    outdir.mkdir(parents=True, exist_ok=True)
    outname = outdir / f"{basin}{storm_num}{year}_{storm_name}_{len(agg)}.txt"

    with outname.open("w") as out:

        # header – 19-wide name, 7-wide count
        out.write(f"{basin}{storm_num}{year},{storm_name:>19},{len(agg):7d},\n")

        def fmt(arr):          # 4-wide radii
            return [f"{v:4d}" for v in arr]

        for dt, info in agg.items():
            date, hhmm = dt[:8], dt[8:] + "00"
            lat = f"{fix_coord(info['lat']):>5}"
            lon = f"{fix_coord(info['lon']):>6}"
            core = [
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
            out.write(", ".join(core) + ", " + ", ".join(radii) + ", -999\n")

    print(f"Wrote {outname}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python JTWC2HURDAT2.py <B-deck file>")
        sys.exit(1)
    main(sys.argv[1])
