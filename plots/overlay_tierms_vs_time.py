# overlay_tierms_vs_time.py
#
# Overlays TIE RMS vs. averaging time for free-running and reference-clock runs,
# with Monte Carlo uncertainty via Poisson resampling of bin counts.

import numpy as np
import matplotlib.pyplot as plt
import glob
import re


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


def load_tierms(files, time_regex):
    n = len(files)
    checkpoint_times = np.empty(n)
    tie_rms_values = np.empty(n)
    error_bars = np.empty(n)

    i = 0
    for f in files:
        d = np.load(f)
        index = d["index"]
        data = d["data"]

        if data.sum() == 0:
            print(f"Skipping {f} — zero counts")
            continue

        rms, error = gaussian_monte_carlo_error(index, data)

        match = re.search(time_regex, f)
        checkpoint_times[i] = float(match.group(1))
        tie_rms_values[i] = rms
        error_bars[i] = error
        i += 1

    checkpoint_times = checkpoint_times[:i]
    tie_rms_values = tie_rms_values[:i]
    error_bars = error_bars[:i]

    order = np.argsort(checkpoint_times)
    return checkpoint_times[order], tie_rms_values[order], error_bars[order]


all_files = sorted(glob.glob("../data/tie_histogram_*.npz"))
free_files = [f for f in all_files if "refclk" not in f and "1.2km" not in f]
link_files = sorted(glob.glob("../data/tie_histogram_1.2km_*.npz"))

free_times, free_rms, free_err = load_tierms(free_files, r"tie_histogram_([\d.eE+-]+)s_")
link_times, link_rms, link_err = load_tierms(link_files, r"tie_histogram_1\.2km_([\d.eE+-]+)s_")

plt.figure()
if len(free_times):
    plt.errorbar(free_times, free_rms, yerr=free_err, marker='o', capsize=3, label="Free running")
if len(link_times):
    plt.errorbar(link_times, link_rms, yerr=link_err, marker='s', capsize=3, label="1.2 km link")
plt.xscale("log")

plt.xlabel("Averaging time (s)")
plt.ylabel("TIE RMS (ps)")
plt.title("TIE RMS vs. averaging time: free running vs. 1.2 km link")
plt.legend()
plt.grid(True, which="both", ls="--", alpha=0.5)
plt.tight_layout()
plt.savefig("overlay(1.2km)_tie_rms_vs_time.png", dpi=150)
plt.show()

print("Free-running — times (s):", free_times)
print("Free-running — RMS (ps): ", free_rms)
print("1.2 km link  — times (s):", link_times)
print("1.2 km link  — RMS (ps): ", link_rms)
