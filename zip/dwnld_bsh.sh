#!/usr/bin/env bash
# download JTWC best-track ZIPs (1945-2024) with wget

set -euo pipefail

for year in {1945..2024}; do
    file="bsh${year}.zip"
    temp_file="${file}.download"
    url="https://www.metoc.navy.mil/jtwc/products/best-tracks/${year}/${year}s-bsh/${file}"
    echo "⇣ $file"
    if wget -q --show-progress --tries=3 -O "$temp_file" "$url"; then
        mv -f "$temp_file" "$file"
    else
        rm -f "$temp_file"
        echo "⚠️  missing $file"
    fi
done
