# plot_histogram.py
#
# Plots a single saved TIE histogram snapshot and prints its count rates.
#
# Usage: python plot_histogram.py <filename or path>
#   <filename> can be a bare filename (e.g. tie_histogram_b2b_2112s_20260819_160147.npz),
#   in which case it's looked up under data/ (including subfolders), or a full/relative path.

import sys
import numpy as np
import matplotlib.pyplot as plt
import re
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
DATA_DIR = SCRIPT_DIR.parent / "data"


def resolve_file(name):
    p = Path(name)
    if p.is_file():
        return p

    candidate = DATA_DIR / name
    if candidate.is_file():
        return candidate

    matches = sorted(DATA_DIR.rglob(name))
    if len(matches) == 1:
        return matches[0]
    if len(matches) > 1:
        print(f"Multiple files named '{name}' found under {DATA_DIR}:")
        for m in matches:
            print(f"  {m.relative_to(DATA_DIR)}")
        sys.exit(1)

    print(f"Could not find '{name}' (looked in cwd, {DATA_DIR}, and its subfolders)")
    sys.exit(1)


def main():
    if len(sys.argv) != 2:
        print("Usage: python plot_histogram.py <filename.npz>")
        sys.exit(1)

    path = resolve_file(sys.argv[1])
    d = np.load(path)
    index = d["index"]   # ps bin centers
    data = d["data"]     # counts per bin

    corrupted = (data < 0) | np.isnan(data)
    n_corrupted = int(corrupted.sum())
    if n_corrupted:
        print(f"WARNING: {n_corrupted} corrupted bin(s) (negative/NaN counts, likely int32 "
              f"overflow) -- excluded from the totals below and zeroed in the plot.")

    clean_data = np.where(corrupted, 0, data)

    total_counts = int(clean_data.sum())
    peak_i = int(np.argmax(clean_data))
    peak_count = int(clean_data[peak_i])
    peak_pos = index[peak_i]
    n_nonzero = int(np.count_nonzero(clean_data))

    match = re.search(r"_([\d.eE+-]+)s_\d{8}_\d{6}", path.stem)
    elapsed = float(match.group(1)) if match else None

    print(f"File: {path}")
    print(f"Bins: {len(index)} total, {n_nonzero} nonzero, span {index.min():.4g} to {index.max():.4g} ps")
    print(f"Total counts: {total_counts:,}")
    if elapsed:
        print(f"Elapsed time: {elapsed:.4g} s")
        print(f"Overall count rate: {total_counts / elapsed:,.4g} counts/s")
        print(f"Peak bin: {peak_pos:.4g} ps, {peak_count:,} counts, {peak_count / elapsed:,.4g} counts/s")
    else:
        print("Elapsed time not found in filename -- skipping rate calculation")
        print(f"Peak bin: {peak_pos:.4g} ps, {peak_count:,} counts")

    plt.figure(figsize=(8, 5))
    plt.step(index, clean_data, where="mid")
    plt.xlabel("TIE (ps)")
    plt.ylabel("Counts")
    plt.title(path.stem)
    plt.grid(True, ls="--", alpha=0.5)
    plt.tight_layout()
    out_path = SCRIPT_DIR / f"histogram_{path.stem}.png"
    plt.savefig(out_path)
    print(f"Saved plot to {out_path}")
    plt.show()


if __name__ == "__main__":
    main()
