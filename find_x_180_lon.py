#!/usr/bin/env python3
"""
find_x_180_lon.py – Find TCs crossing 180 (or -180) Longitude
across all *.txt files in ./single_TC or a specified folder.

Usage
-----
$ python find_x_180_lon.py            # uses ./single_TC
$ python find_x_180_lon.py /path/to/a/directory
"""
import sys
from pathlib import Path
from read_hurricane_data import read_hurricane_data


def main():
    single_TC_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).with_name('single_TC')
    if not single_TC_dir.is_dir():
        sys.exit(f"!!! Directory '{single_TC_dir}' not found")

    print(single_TC_dir)
    for txt in single_TC_dir.glob('*.txt'):
        df = read_hurricane_data(txt)
        if ((df["lon"].min() < 0) & (df["lon"].max() > 0) & (df["lon"].abs().max() > 170)):
            print(txt)


if __name__ == '__main__':
    main()
