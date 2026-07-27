# tierms_vs_time.py
#
# Reads saved TIE histogram snapshots (from tie_histogram_snapshots.py),
# computes an RMS estimate from each histogram, and plots TIE RMS vs.
# elapsed checkpoint time.

import numpy as np
import matplotlib.pyplot as plt
import glob
import re

files = sorted(glob.glob("../data/tie_histogram_*.npz"))

checkpoint_times = []
tie_rms_values = []

for f in files:
    d = np.load(f)
    index = d["index"]   # ps bin centers
    data = d["data"]      # counts per bin

    if data.sum() == 0:
        print(f"Skipping {f} — zero counts")
        continue

    # RMS of the histogram: sqrt(weighted average of index^2, weighted by counts)
    rms = np.sqrt(np.average(index**2, weights=data))

    # Extract the checkpoint time from the filename itself
    # (filenames look like: tie_histogram_0.1s_20260724_....npz)
    match = re.search(r"tie_histogram_([\d.eE+-]+)s_", f)
    checkpoint_time = float(match.group(1))

    checkpoint_times.append(checkpoint_time)
    tie_rms_values.append(rms)

# Sort by checkpoint time, in case glob's alphabetical order doesn't match numeric order
order = np.argsort(checkpoint_times)
checkpoint_times = np.array(checkpoint_times)[order]
tie_rms_values = np.array(tie_rms_values)[order]

plt.loglog(checkpoint_times, tie_rms_values, marker='o')
plt.xlabel("Elapsed time (s)")
plt.ylabel("TIE RMS (ps)")
plt.title("TIE RMS vs. averaging time")
plt.grid(True, which="both", ls="--", alpha=0.5)
plt.savefig("tie_rms_vs_time.png")
plt.show()

print("Checkpoint times (s):", checkpoint_times)
print("TIE RMS (ps):", tie_rms_values)