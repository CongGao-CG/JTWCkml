#!/usr/bin/env python3
"""
run_all.py – drive JTWC2HURDAT2.py over every b*.txt / b*.dat in the current
directory, while

  • de-duplicating storms that appear as both .txt and .dat
  • replacing storms whose product already exists in ../single_TC/
  • keeping correct statistics
"""

from pathlib import Path
from collections import Counter
import subprocess
import sys

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

    existing_products = list(Path("../single_TC").glob(f"{prod_prefix}*.txt"))

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
        written = [
            line[len("Wrote ") :].strip()
            for line in out.splitlines()
            if line.startswith("Wrote ")
        ]
        if not written:
            stats["errors"] += 1
            errors.append(path.name)
            continue

        written_product = Path(written[-1]).resolve()
        for old_product in existing_products:
            if old_product.resolve() != written_product:
                old_product.unlink()

        stats["success"] += 1
    else:
        stats["errors"] += 1
        errors.append(path.name)
        # keep going
# ---------------------------------------------------------------------------

total = sum(stats.values())

print("\n========== SUMMARY ==========")
print(f"✓  Success : {stats['success']}")
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
