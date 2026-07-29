# ref_tierms_vs_time.py
#
# Reads saved TIE histogram snapshots from the reference clock run,
# computes an RMS estimate (around the histogram's own mean to account for fixed delay)
# from each histogram, and plots TIE RMS (ref clock) vs. elapsed checkpoint time.

import numpy as np
import matplotlib.pyplot as plt
import glob
import re

def gaussian_monte_carlo_error(index, data, n_simulations=1000, max_sim_size=20000):
    mean = np.average(index, weights=data)
    sigma = np.sqrt(np.average((index - mean)**2, weights=data))
    total_counts = int(data.sum())
    sim_size = min(total_counts, max_sim_size)

    rms_estimates = []
    for _ in range(n_simulations):
        simulated = np.random.normal(loc=mean, scale=sigma, size=sim_size)
        sim_mean = np.mean(simulated)
        sim_rms = np.sqrt(np.mean((simulated - sim_mean)**2))
        rms_estimates.append(sim_rms)

    rms_estimates = np.array(rms_estimates)
    return sigma, np.std(rms_estimates)

files = sorted(glob.glob("../data/tie_histogram_refclk_*.npz"))

checkpoint_times = []
tie_rms_values = []
error_bars = []

for f in files:
    d = np.load(f)
    index = d["index"]   # ps bin centers
    data = d["data"]      # counts per bin

    if data.sum() == 0:
        print(f"Skipping {f} — zero counts")
        continue

    rms, error = gaussian_monte_carlo_error(index, data)

    match = re.search(r"tie_histogram_refclk_([\d.eE+-]+)s_", f)
    checkpoint_time = float(match.group(1))

    checkpoint_times.append(checkpoint_time)
    tie_rms_values.append(rms)
    error_bars.append(error)

order = np.argsort(checkpoint_times)
checkpoint_times = np.array(checkpoint_times)[order]
tie_rms_values = np.array(tie_rms_values)[order]
error_bars = np.array(error_bars)[order]

plt.errorbar(checkpoint_times, tie_rms_values, yerr=error_bars, marker='o', capsize=3)
plt.xscale("log")
plt.yscale("log")
plt.xlabel("Elapsed time (s)")
plt.ylabel("TIE RMS (ps)")
plt.title("TIE RMS (ref clock) vs. averaging time")
plt.grid(True, which="both", ls="--", alpha=0.5)
plt.tight_layout()
plt.savefig("ref_tie_rms_vs_time.png")
plt.show()

print("Checkpoint times (s):", checkpoint_times)
print("TIE RMS (ps):", tie_rms_values)