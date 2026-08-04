# overlay_tierms_vs_time.py
#
# Overlays TIE RMS vs. averaging time for free-running and reference-clock runs.
# Error bars are per-point Monte Carlo: model the underlying distribution as
# Normal(mean, sigma) from the histogram, draw total_counts raw samples per trial,
# recompute RMS, and use the std of those estimates as the error bar.
# Error bars naturally shrink at longer averaging times (more counts).

import numpy as np
import matplotlib.pyplot as plt
import glob
import re


def tie_rms(index, data):
    mean = np.average(index, weights=data)
    return np.sqrt(np.average((index - mean)**2, weights=data))


def empirical_sigma(prefix):
    files = glob.glob(f"../data/tie_errorbars_{prefix}_*.npz")
    if not files:
        print(f"Warning: no error bar files found for prefix '{prefix}'")
        return 0.0
    sigmas = []
    for f in files:
        d = np.load(f)
        rms_per_trial = [tie_rms(d["index"], row) for row in d["trials"] if row.sum() > 0]
        if rms_per_trial:
            sigmas.extend(rms_per_trial)
    return np.std(sigmas)


# def monte_carlo_error(index, data, sigma, n_simulations=1000):
#     mean = np.average(index, weights=data)
#     rms = np.sqrt(np.average((index - mean)**2, weights=data))

#     rms_estimates = np.empty(n_simulations)
#     for i in range(n_simulations):
#         simulated_counts = np.random.normal(loc=data, scale=sigma)
#         simulated_counts = np.clip(simulated_counts, 0, None)
#         sim_mean = np.average(index, weights=simulated_counts)
#         rms_estimates[i] = np.sqrt(np.average((index - sim_mean)**2, weights=simulated_counts))

#     return rms, np.std(rms_estimates)


def load_tierms(files, time_regex, sigma):
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

        rms, error = tie_rms(index, data), sigma  # flat empirical-sigma error bar (same for all points)
        # rms, error = monte_carlo_error(index, data, sigma)

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
free_files = [f for f in all_files if "refclk" not in f and "1.2km" not in f and "tt_jitter" not in f]
link_files = sorted(glob.glob("../data/tie_histogram_1.2km_*.npz"))
tt_jitter_files = sorted(glob.glob("../data/tie_histogram_tt_jitter_*.npz"))

free_sigma = empirical_sigma("free")
link_sigma = empirical_sigma("1.2km")
tt_sigma   = empirical_sigma("tt_jitter")

free_times, free_rms, free_err = load_tierms(free_files, r"tie_histogram_([\d.eE+-]+)s_", free_sigma)
link_times, link_rms, link_err = load_tierms(link_files, r"tie_histogram_1\.2km_([\d.eE+-]+)s_", link_sigma)
tt_times,   tt_rms,   tt_err   = load_tierms(tt_jitter_files, r"tie_histogram_tt_jitter_([\d.eE+-]+)s_", tt_sigma)

plt.figure()
if len(free_times):
    plt.errorbar(free_times, free_rms, yerr=free_err, marker='o', capsize=3, label="Back-to-back")
if len(link_times):
    plt.errorbar(link_times, link_rms, yerr=link_err, marker='s', capsize=3, label="1.2 km link")
if len(tt_times):
    plt.errorbar(tt_times, tt_rms, yerr=tt_err, marker='^', capsize=3, label="TT jitter")
plt.xscale("log")

plt.xlabel("Averaging time (s)")
plt.ylabel("TIE RMS (ps)")
plt.title("TIE RMS vs. averaging time: back-to-back vs. 1.2 km link vs. TT jitter")
plt.legend()
plt.grid(True, which="both", ls="--", alpha=0.5)
plt.tight_layout()
plt.savefig("overlay(tt_jitter)_tie_rms_vs_time.png", dpi=150)
plt.show()

print("Back-to-back — times (s):", free_times)
print("Back-to-back — RMS (ps): ", free_rms)
print("1.2 km link  — times (s):", link_times)
print("1.2 km link  — RMS (ps): ", link_rms)
print("TT jitter    — times (s):", tt_times)
print("TT jitter    — RMS (ps): ", tt_rms)
