# ref_tierms_vs_time.py
#
# Reads saved TIE histogram snapshots from the reference clock run,
# computes an RMS estimate (around the histogram's own mean to account for fixed delay)
# from each histogram, and plots TIE RMS (ref clock) vs. elapsed checkpoint time.

import numpy as np
import matplotlib.pyplot as plt
import glob
import re

files = sorted(glob.glob("../data/tie_histogram_refclk_*.npz"))

checkpoint_times = []
tie_rms_values = []

for f in files:
    d = np.load(f)
    index = d["index"]   # ps bin centers
    data = d["data"]      # counts per bin

    if data.sum() == 0:
        print(f"Skipping {f} — zero counts")
        continue

    # RMS around histogram's mean
    mean = np.average(index, weights=data)
    rms = np.sqrt(np.average((index - mean)**2, weights=data))

    # Extract the checkpoint time from the filename itself
    # (filenames look like: tie_histogram_0.1s_20260724_....npz)
    match = re.search(r"tie_histogram_refclk_([\d.eE+-]+)s_", f)
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
plt.title("TIE RMS (ref clock) vs. averaging time")
plt.grid(True, which="both", ls="--", alpha=0.5)
plt.tight_layout()
plt.savefig("ref_tie_rms_vs_time.png")
plt.show()

print("Checkpoint times (s):", checkpoint_times)
print("TIE RMS (ps):", tie_rms_values)