# overlay_tierms_vs_time.py
#
# Overlays TIE RMS vs. averaging time for free-running and reference-clock runs.

import numpy as np
import matplotlib.pyplot as plt
import glob
import re


def load_tierms(files, time_regex):
    checkpoint_times = []
    tie_rms_values = []

    for f in files:
        d = np.load(f)
        index = d["index"]
        data = d["data"]

        if data.sum() == 0:
            print(f"Skipping {f} — zero counts")
            continue

        mean = np.average(index, weights=data)
        rms = np.sqrt(np.average((index - mean)**2, weights=data))

        match = re.search(time_regex, f)
        checkpoint_times.append(float(match.group(1)))
        tie_rms_values.append(rms)

    order = np.argsort(checkpoint_times)
    return np.array(checkpoint_times)[order], np.array(tie_rms_values)[order]


all_files = sorted(glob.glob("../data/tie_histogram_*.npz"))
free_files = [f for f in all_files if "refclk" not in f]
ref_files  = sorted(glob.glob("../data/tie_histogram_refclk_*.npz"))

free_times, free_rms = load_tierms(free_files, r"tie_histogram_([\d.eE+-]+)s_")
ref_times,  ref_rms  = load_tierms(ref_files,  r"tie_histogram_refclk_([\d.eE+-]+)s_")

plt.figure()
if len(free_times):
    plt.loglog(free_times, free_rms, marker='o', label="Free running")
if len(ref_times):
    plt.loglog(ref_times, ref_rms, marker='s', label="Ref clock")

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
