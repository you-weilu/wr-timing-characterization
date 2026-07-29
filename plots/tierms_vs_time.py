# tierms_vs_time.py
#
# Reads saved TIE histogram snapshots,
# computes an RMS estimate (around the histogram's own mean to account for fixed delay)
# from each histogram, and plots TIE RMS vs. elapsed checkpoint time.

import numpy as np
import matplotlib.pyplot as plt
import glob
import re

def gaussian_monte_carlo_error(index, data, n_simulations=1000):
    mean = np.average(index, weights=data)
    sigma = np.sqrt(np.average((index - mean)**2, weights=data))
    total_counts = int(data.sum())

    rms_estimates = []
    for _ in range(n_simulations):
        simulated = np.random.normal(loc=mean, scale=sigma, size=total_counts)
        sim_mean = np.mean(simulated)
        sim_rms = np.sqrt(np.mean((simulated - sim_mean)**2))
        rms_estimates.append(sim_rms)

    rms_estimates = np.array(rms_estimates)
    return sigma, np.std(rms_estimates)   # (actual RMS from real data, error bar)

files = sorted(glob.glob("../data/tie_histogram_*.npz"))
free_running_files = [f for f in files if "refclk" not in f]

checkpoint_times = []
tie_rms_values = []
error_bars = []

for f in free_running_files:
    d = np.load(f)
    index = d["index"]   # ps bin centers
    data = d["data"]      # counts per bin

    if data.sum() == 0:
        print(f"Skipping {f} — zero counts")
        continue
    
    # rms around histogram's mean + monte carlo error
    rms, error = gaussian_monte_carlo_error(index, data)

    # Extract the checkpoint time from the filename itself
    # (filenames look like: tie_histogram_0.1s_20260724_....npz)
    match = re.search(r"tie_histogram_([\d.eE+-]+)s_", f)
    checkpoint_time = float(match.group(1))

    checkpoint_times.append(checkpoint_time)
    tie_rms_values.append(rms)
    error_bars.append(error)

# Sort by checkpoint time, in case glob's alphabetical order doesn't match numeric order
order = np.argsort(checkpoint_times)
checkpoint_times = np.array(checkpoint_times)[order]
tie_rms_values = np.array(tie_rms_values)[order]
error_bars = np.array(error_bars)[order]

plt.errorbar(checkpoint_times, tie_rms_values, yerr=error_bars, marker='o', capsize=3)
plt.xscale("log")
plt.yscale("log")
plt.xlabel("Elapsed time (s)")
plt.ylabel("TIE RMS (ps)")
plt.title("TIE RMS vs. averaging time")
plt.grid(True, which="both", ls="--", alpha=0.5)
plt.tight_layout()
plt.savefig("tie_rms_vs_time.png")
plt.show()

print("Checkpoint times (s):", checkpoint_times)
print("TIE RMS (ps):", tie_rms_values)