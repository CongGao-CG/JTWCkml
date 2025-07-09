#!/usr/bin/env bash
# download JTWC best-track ZIPs (1945-2023) with wget

set -euo pipefail

for year in {1945..2023}; do
    file="bsh${year}.zip"
    url="https://www.metoc.navy.mil/jtwc/products/best-tracks/${year}/${year}s-bsh/${file}"
    echo "⇣ $file"
    wget -q --show-progress --continue --tries=3 --no-clobber "$url" || echo "⚠️  missing $file"
done
