#!/usr/bin/env bash
# download JTWC best-track ZIPs (1945-2024) with wget

set -euo pipefail

failed_files=()
failure_count=0

for year in {1945..2024}; do
    file="bio${year}.zip"
    temp_file="${file}.download"
    url="https://www.metoc.navy.mil/jtwc/products/best-tracks/${year}/${year}s-bio/${file}"
    echo "⇣ $file"

    if ! wget -q --show-progress --tries=3 -O "$temp_file" "$url"; then
        rm -f "$temp_file"
        echo "⚠️  download failed: $file"
        failed_files+=("$file (download failed)")
        ((failure_count += 1))
        continue
    fi

    if ! unzip -tq "$temp_file" >/dev/null 2>&1; then
        rm -f "$temp_file"
        echo "⚠️  invalid ZIP: $file"
        failed_files+=("$file (invalid ZIP)")
        ((failure_count += 1))
        continue
    fi

    mv -f "$temp_file" "$file"
done

if ((failure_count > 0)); then
    printf '\n⚠️  %d file(s) were not downloaded correctly:\n' "$failure_count"
    printf '  - %s\n' "${failed_files[@]}"
    exit 1
fi

echo "✓ All files downloaded and validated successfully."
