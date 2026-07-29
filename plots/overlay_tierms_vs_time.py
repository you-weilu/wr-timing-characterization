# overlay_tierms_vs_time.py
#
# Overlays TIE RMS vs. averaging time for free-running and reference-clock runs.

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

    return sigma, np.std(np.array(rms_estimates))


def load_tierms(files, time_regex):
    checkpoint_times = []
    tie_rms_values = []
    error_bars = []

    for f in files:
        d = np.load(f)
        index = d["index"]
        data = d["data"]

        if data.sum() == 0:
            print(f"Skipping {f} — zero counts")
            continue

        rms, error = gaussian_monte_carlo_error(index, data)

        match = re.search(time_regex, f)
        checkpoint_times.append(float(match.group(1)))
        tie_rms_values.append(rms)
        error_bars.append(error)

    order = np.argsort(checkpoint_times)
    return np.array(checkpoint_times)[order], np.array(tie_rms_values)[order], np.array(error_bars)[order]


all_files = sorted(glob.glob("../data/tie_histogram_*.npz"))
free_files = [f for f in all_files if "refclk" not in f]
ref_files  = sorted(glob.glob("../data/tie_histogram_refclk_*.npz"))

free_times, free_rms, free_err = load_tierms(free_files, r"tie_histogram_([\d.eE+-]+)s_")
ref_times,  ref_rms,  ref_err  = load_tierms(ref_files,  r"tie_histogram_refclk_([\d.eE+-]+)s_")

plt.figure()
if len(free_times):
    plt.errorbar(free_times, free_rms, yerr=free_err, marker='o', capsize=3, label="Free running")
if len(ref_times):
    plt.errorbar(ref_times, ref_rms, yerr=ref_err, marker='s', capsize=3, label="Ref clock")
plt.xscale("log")
plt.yscale("log")

plt.xlabel("Averaging time (s)")
plt.ylabel("TIE RMS (ps)")
plt.title("TIE RMS vs. averaging time: free running vs. ref clock")
plt.legend()
plt.grid(True, which="both", ls="--", alpha=0.5)
plt.tight_layout()
plt.savefig("overlay_tie_rms_vs_time.png", dpi=150)
plt.show()

print("Free-running — times (s):", free_times)
print("Free-running — RMS (ps): ", free_rms)
print("Ref clock    — times (s):", ref_times)
print("Ref clock    — RMS (ps): ", ref_rms)
