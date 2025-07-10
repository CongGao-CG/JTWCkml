#!/usr/bin/env bash
# run_all.sh – batch-convert every b*.txt / b*.dat file with JTWC2HURDAT2.py
#   • skips files whose HURDAT2 output already exists in ../Single_TC/
#   • continues after any Python error
#   • prints a summary (success / skipped / no-valid / failed)

set -euo pipefail

CONVERTER="JTWC2HURDAT2.py"
OUTDIR="../Single_TC"

[[ -f $CONVERTER ]] || { echo "Error: cannot find $CONVERTER" >&2; exit 1; }
[[ -d $OUTDIR ]] || mkdir -p "$OUTDIR"

shopt -s nocaseglob nullglob

success=0 failed=0 novalid=0 skipped=0
failed_files=() novalid_files=() skipped_files=()

for bdeck in b*.txt b*.dat; do
    [[ -e $bdeck ]] || break          # quit loop if no matching files at all

    fname=${bdeck##*/}                # basename
    id=${fname#?}                     # drop leading 'b'
    id=${id%%.*}                      # strip extension
    # upper-case in a Bash-3-friendly way
    id=$(printf '%s' "$id" | tr '[:lower:]' '[:upper:]')

    # ── skip if any output file already exists ──────────────────────────────
    matches=( "$OUTDIR"/"$id"* )
    if (( ${#matches[@]} )); then
        echo "⏩  $bdeck – output for $id exists, skipping"
        skipped_files+=("$bdeck"); ((skipped++))
        continue
    fi

    echo "▶  Converting $bdeck …"
    if output=$(python "$CONVERTER" "$bdeck" 2>&1); then
        echo "$output"
        if grep -qi "No valid rows found in file" <<<"$output"; then
            novalid_files+=("$bdeck"); ((novalid++))
        else
            ((success++))
        fi
    else
        echo "$output"
        failed_files+=("$bdeck"); ((failed++))
        echo "  ↳ conversion FAILED, continuing with next file"
    fi
done

# ────── summary ──────
echo
echo "══════════ Summary ══════════"
printf "✓ Successful conversions : %d\n" "$success"
printf "⏩ Skipped (already done) : %d\n" "$skipped"
printf "✗ Python errors          : %d\n" "$failed"
printf "∅ No valid rows          : %d\n" "$novalid"

(( skipped )) && { echo -e "\nSkipped files:"; printf "  • %s\n" "${skipped_files[@]}"; }
(( failed  )) && { echo -e "\nFiles with Python errors:"; printf "  • %s\n" "${failed_files[@]}"; }
(( novalid )) && { echo -e "\nFiles with no valid rows:"; printf "  • %s\n" "${novalid_files[@]}"; }