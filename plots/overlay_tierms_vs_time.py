# overlay_tierms_vs_time.py
#
# Overlays TIE RMS vs. averaging time for selected data series.
# To change what gets plotted, edit SERIES below — each entry needs:
#   prefix : filename prefix after "tie_histogram_" (used for glob + error bar lookup)
#   label  : legend label
#   marker : matplotlib marker symbol
#
# Files are expected at ../data/tie_histogram_<prefix>_<time>s_*.npz
# Error bars come from ../data/tie_errorbars_<prefix>_*.npz (empirical sigma).

import numpy as np
import matplotlib.pyplot as plt
import glob
import re

# ── configure series here ────────────────────────────────────────────────────
SERIES = [
    {"prefix": "1.2km",     "label": "1.2 km link",  "marker": "x"},
    {"prefix": "jacob",     "label": "Jacob",         "marker": "x"},
    # {"prefix": "tt_jitter", "label": "TT jitter",    "marker": "^"},
    # {"prefix": "free",      "label": "Back-to-back", "marker": "D"},
]

OUTPUT_FILE = "overlay_jacob_vs_1.2km_tie_rms.png"
# ─────────────────────────────────────────────────────────────────────────────


def tie_rms(index, data):
    mean = np.average(index, weights=data)
    return np.sqrt(np.average((index - mean)**2, weights=data))


def empirical_sigma(prefix):
    files = glob.glob(f"../data/tie_errorbars_{prefix}_*.npz")
    if not files:
        print(f"Warning: no error bar files found for prefix '{prefix}'")
        return 0.0
    d = np.load(files[0])
    rms_per_trial = [tie_rms(d["index"], row) for row in d["trials"] if row.sum() > 0]
    return np.std(rms_per_trial) if rms_per_trial else 0.0


def load_tierms(prefix, sigma):
    files = sorted(glob.glob(f"../data/tie_histogram_{prefix}_*.npz"))
    escaped = re.escape(prefix)
    time_regex = rf"tie_histogram_{escaped}_([\d.eE+-]+)s_"

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

        match = re.search(time_regex, f)
        if match is None:
            print(f"Warning: could not parse time from filename, skipping: {f}")
            continue

        checkpoint_times[i] = float(match.group(1))
        tie_rms_values[i] = tie_rms(index, data)
        error_bars[i] = sigma
        i += 1

    checkpoint_times = checkpoint_times[:i]
    tie_rms_values = tie_rms_values[:i]
    error_bars = error_bars[:i]

    order = np.argsort(checkpoint_times)
    return checkpoint_times[order], tie_rms_values[order], error_bars[order]


plt.figure()
for s in SERIES:
    prefix = s["prefix"]
    sigma = empirical_sigma(prefix)
    times, rms, err = load_tierms(prefix, sigma)
    if len(times):
        plt.errorbar(times, rms, yerr=err, marker=s["marker"], capsize=3, label=s["label"])
    print(f"{s['label']} — times (s): {times}")
    print(f"{s['label']} — RMS (ps):  {rms}")

plt.xscale("log")
plt.xlabel("Averaging time (s)")
plt.ylabel("TIE RMS (ps)")
plt.title("TIE RMS vs. averaging time")
plt.legend()
plt.grid(True, which="both", ls="--", alpha=0.5)
plt.tight_layout()
plt.savefig(OUTPUT_FILE, dpi=150)
plt.show()
