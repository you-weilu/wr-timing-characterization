# ref_tierms_vs_time.py
#
# Reads saved TIE histogram snapshots from the reference clock run,
# computes an RMS estimate (around the histogram's own mean to account for fixed delay)
# from each histogram with Monte Carlo uncertainty via Poisson resampling of bin counts,
# and plots TIE RMS (ref clock) vs. elapsed checkpoint time.

import numpy as np
import matplotlib.pyplot as plt
import glob
import re

# rmb to compare with fitted gaussian instead of actual histogram

def gaussian_monte_carlo_error(index, data, n_simulations=1000):
    mean = np.average(index, weights=data)
    sigma = np.sqrt(np.average((index - mean)**2, weights=data))

    rms_estimates = np.empty(n_simulations)

    for i in range(n_simulations):
        # For each bin, simulate a new count via ???Poisson noise??? around the real count
        simulated_counts = np.random.poisson(lam=data) # simulated_counts: each element in data array simulated with poissonian error
        
        # Recompute mean/RMS using these simulated counts as the new weights
        sim_mean = np.average(index, weights=simulated_counts)
        sim_rms = np.sqrt(np.average((index - sim_mean)**2, weights=simulated_counts))
        rms_estimates[i] = sim_rms

    return sigma, np.std(rms_estimates)

files = sorted(glob.glob("../data/tie_histogram_refclk_*.npz"))

# preallocate arrays with number of data points
n = len(files)
checkpoint_times = np.empty(n)
tie_rms_values = np.empty(n)
error_bars = np.empty(n)

i = 0
for f in files:
    d = np.load(f)
    index = d["index"]   # ps bin centers
    data = d["data"]      # counts per bin

    if data.sum() == 0:
        print(f"Skipping {f} — zero counts")
        continue

    rms, error = gaussian_monte_carlo_error(index, data)

    match = re.search(r"tie_histogram_refclk_([\d.eE+-]+)s_", f)
    checkpoint_time = float(match.group(1)) # extract first set of parantheses from regex pattern search (checkpoint time)

    checkpoint_times[i] = checkpoint_time
    tie_rms_values[i] = rms
    error_bars[i] = error
    i += 1

checkpoint_times = checkpoint_times[:i]
tie_rms_values = tie_rms_values[:i]
error_bars = error_bars[:i]

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