# overlay_tierms_vs_time.py
#
# Overlays TIE RMS vs. averaging time for free-running and reference-clock runs.
# Error bars are empirical: sigma = std of TIE RMS values across 1000 independent
# trials collected at short averaging times, assumed constant across all time points.

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
            sigmas.append(np.std(rms_per_trial))
    return np.mean(sigmas)


def load_tierms(files, time_regex):
    n = len(files)
    checkpoint_times = np.empty(n)
    tie_rms_values = np.empty(n)

    i = 0
    for f in files:
        d = np.load(f)
        index = d["index"]
        data = d["data"]

        if data.sum() == 0:
            print(f"Skipping {f} — zero counts")
            continue

        match = re.search(time_regex, f)
        checkpoint_times[i] = float(match.group(1))
        tie_rms_values[i] = tie_rms(index, data)
        i += 1

    checkpoint_times = checkpoint_times[:i]
    tie_rms_values = tie_rms_values[:i]

    order = np.argsort(checkpoint_times)
    return checkpoint_times[order], tie_rms_values[order]


all_files = sorted(glob.glob("../data/tie_histogram_*.npz"))
free_files = [f for f in all_files if "refclk" not in f and "1.2km" not in f and "tt_jitter" not in f]
link_files = sorted(glob.glob("../data/tie_histogram_1.2km_*.npz"))
tt_jitter_files = sorted(glob.glob("../data/tie_histogram_tt_jitter_*.npz"))

free_sigma = empirical_sigma("free")
link_sigma = empirical_sigma("refclk")
tt_sigma   = empirical_sigma("tt_jitter")

free_times, free_rms = load_tierms(free_files, r"tie_histogram_([\d.eE+-]+)s_")
link_times, link_rms = load_tierms(link_files, r"tie_histogram_1\.2km_([\d.eE+-]+)s_")
tt_times,   tt_rms   = load_tierms(tt_jitter_files, r"tie_histogram_tt_jitter_([\d.eE+-]+)s_")

plt.figure()
if len(free_times):
    plt.errorbar(free_times, free_rms, yerr=free_sigma, marker='o', capsize=3, label="Back-to-back")
if len(link_times):
    plt.errorbar(link_times, link_rms, yerr=link_sigma, marker='s', capsize=3, label="1.2 km link")
if len(tt_times):
    plt.errorbar(tt_times, tt_rms, yerr=tt_sigma, marker='^', capsize=3, label="TT jitter")
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
