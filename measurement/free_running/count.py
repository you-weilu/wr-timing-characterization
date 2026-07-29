import numpy as np
import glob
import re

files = sorted(f for f in glob.glob("../../data/tie_histogram_*.npz") if "refclk" not in f)

checkpoint_times = []
counts_list = []

for f in files:
    d = np.load(f)
    data = d["data"]
    total_counts = data.sum()

    match = re.search(r"tie_histogram_([\d.eE+-]+)s_", f)
    checkpoint_time = float(match.group(1))

    checkpoint_times.append(checkpoint_time)
    counts_list.append(total_counts)

# Sort by checkpoint time for a clean, ordered printout
order = np.argsort(checkpoint_times)
checkpoint_times = np.array(checkpoint_times)[order]
counts_list = np.array(counts_list)[order]

for t, c in zip(checkpoint_times, counts_list):
    print(f"{t:.4g}s — {c} counts")