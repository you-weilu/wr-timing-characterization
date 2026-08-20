# tierms_vs_time.py
#
# Reads saved TIE histogram snapshots,
# computes an RMS estimate (around the histogram's own mean to account for fixed delay)
# from each histogram with Monte Carlo uncertainty via Poisson resampling of bin counts,
# and plots TIE RMS vs. elapsed checkpoint time.

import numpy as np
import matplotlib.pyplot as plt
import re
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
DATA_DIR = SCRIPT_DIR.parent / "data"

# ============ CONFIGURATION ============
PREFIX = "b2b"   # filename prefix after "tie_histogram_", e.g. "b2b", "jacob", "1.2km", "free"
# ========================================

def gaussian_monte_carlo_error(index, data, n_simulations=1000):
    mean = np.average(index, weights=data)
    sigma = np.sqrt(np.average((index - mean)**2, weights=data))

    rms_estimates = np.empty(n_simulations)

    for i in range(n_simulations):
        simulated_counts = np.random.poisson(lam=data)
        sim_mean = np.average(index, weights=simulated_counts)
        sim_rms = np.sqrt(np.average((index - sim_mean)**2, weights=simulated_counts))
        rms_estimates[i] = sim_rms

    return sigma, np.std(rms_estimates)

files = sorted(str(p) for p in DATA_DIR.glob(f"tie_histogram_{PREFIX}_*.npz"))
free_running_files = [f for f in files if "refclk" not in f]

# preallocate arrays with number of data points
n = len(free_running_files)
checkpoint_times = np.empty(n)
tie_rms_values = np.empty(n)
error_bars = np.empty(n)

i = 0
for f in free_running_files:
    d = np.load(f)
    index = d["index"]   # ps bin centers
    data = d["data"]      # counts per bin

    if data.sum() == 0:
        print(f"Skipping {f} — zero counts")
        continue

    if (data < 0).any() or np.isnan(data).any():
        print(f"Skipping {f} — corrupted histogram (negative or NaN counts, int32 overflow)")
        continue

    rms, error = gaussian_monte_carlo_error(index, data)

    match = re.search(rf"tie_histogram_{re.escape(PREFIX)}_([\d.eE+-]+)s_", f)
    checkpoint_time = float(match.group(1))

    checkpoint_times[i] = checkpoint_time
    tie_rms_values[i] = rms
    error_bars[i] = error
    i += 1

checkpoint_times = checkpoint_times[:i]
tie_rms_values = tie_rms_values[:i]
error_bars = error_bars[:i]

# Sort by checkpoint time, in case glob's alphabetical order doesn't match numeric order
order = np.argsort(checkpoint_times)
checkpoint_times = np.array(checkpoint_times)[order]
tie_rms_values = np.array(tie_rms_values)[order]
error_bars = np.array(error_bars)[order]

plt.plot(checkpoint_times, tie_rms_values, marker='o')
plt.xscale("log")
plt.xlabel("Elapsed time (s)")
plt.ylabel("TIE RMS (ps)")
plt.title(f"TIE RMS vs. averaging time ({PREFIX})")
plt.grid(True, which="both", ls="--", alpha=0.5)
plt.tight_layout()
plt.savefig(SCRIPT_DIR / f"tie_rms_vs_time_{PREFIX}.png")
plt.show()

print("Checkpoint times (s):", checkpoint_times)
print("TIE RMS (ps):", tie_rms_values)
