#!/usr/bin/env python3
"""
run_all.py – drive JTWC2HURDAT2.py over every b*.txt / b*.dat in the current
directory, while

  • de-duplicating storms that appear as both .txt and .dat
  • skipping storms whose product already exists in ../single_TC/
  • keeping correct statistics
"""

from pathlib import Path
from collections import Counter
import subprocess, sys, textwrap, glob

# ------------------------------------------------------------
BDECKS = sorted(Path(".").glob("b*.txt")) + sorted(Path(".").glob("b*.dat"))
if not BDECKS:
    sys.exit("No b*.txt / b*.dat files found")

# 1) collapse duplicates  (.txt + .dat with the same stem)
unique_inputs = {}
for f in BDECKS:
    stem = f.stem        # bcp032015
    # prefer .dat over .txt if both exist
    if stem not in unique_inputs or f.suffix == ".dat":
        unique_inputs[stem] = f

stats = Counter()
errors, nodata = [], []

print(f"Found {len(unique_inputs)} unique storms\n")

for stem, path in unique_inputs.items():
    # Expected product prefix  (bwp082019 → WP082019  etc.)
    prod_prefix = stem[1:].upper()                 # drop leading 'b'

    already = glob.glob(f"../single_TC/{prod_prefix}*.txt")
    if already:
        stats["skipped"] += 1
        continue

    # --- run the converter --------------------------------------------------
    proc = subprocess.run(
        ["python", "JTWC2HURDAT2.py", str(path)],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    out = proc.stdout
    if "No valid rows found" in out:
        stats["no_data"] += 1
        nodata.append(path.name)
    elif proc.returncode == 0:
        stats["success"] += 1
    else:
        stats["errors"] += 1
        errors.append(path.name)
        # keep going
# ---------------------------------------------------------------------------

total = sum(stats.values())

print("\n========== SUMMARY ==========")
print(f"✓  Success : {stats['success']}")
print(f"↷  Skipped : {stats['skipped']}")
print(f"Ø  No data : {stats['no_data']}")
print(f"✗  Errors  : {stats['errors']}")
print(f"Total storms processed: {total}")

if nodata:
    print("\n— No valid rows —")
    for f in nodata:
        print(f"   {f}")

if errors:
    print("\n— Conversion errors —")
    for f in errors:
        print(f"   {f}")