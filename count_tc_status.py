#!/usr/bin/env python3
"""
count_tc_status.py – Count occurrences of each tropical-cyclone status code
(HU, TS, EX, etc.) across all *.txt files in ./single_TC or a specified folder.

Usage
-----
$ python count_tc_status.py            # uses ./single_TC
$ python count_tc_status.py /path/to/a/directory
"""
import sys
from pathlib import Path
import re
from collections import Counter


def accumulate_counts(path: Path, counts: Counter):
    with path.open() as f:
        for line in f:
            if not re.match(r"^\d{8},", line):
                continue  # skip header/meta
            parts = [p.strip() for p in line.split(',')]
            if len(parts) >= 4 and parts[3]:
                counts[parts[3]] += 1


def main():
    single_TC_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).with_name('single_TC')
    if not single_TC_dir.is_dir():
        sys.exit(f"!!! Directory '{single_TC_dir}' not found")

    print(single_TC_dir)
    counts = Counter()
    for txt in single_TC_dir.glob('*.txt'):
        accumulate_counts(txt, counts)

    total = sum(counts.values())
    if not total:
        print('No status codes found.')
        return

    print('Tropical cyclone status counts:')
    for status, n in counts.most_common():
        print(f'{status:>3} : {n}')
    print('-' * 20)
    print(f'Total : {total}')


if __name__ == '__main__':
    main()
