# check_errorbars.py
#
# Prints the TIE RMS sigma per averaging time for each dataset,
# so we can verify sigma is approximately constant across intervals.

import numpy as np
import glob
import re


def tie_rms(index, data):
    mean = np.average(index, weights=data)
    return np.sqrt(np.average((index - mean)**2, weights=data))


def check_prefix(prefix):
    files = sorted(glob.glob(f"../data/tie_errorbars_{prefix}_*.npz"))
    if not files:
        print(f"  No files found for prefix '{prefix}'\n")
        return

    print(f"  {'Duration (s)':<15} {'Mean RMS (ps)':<18} {'Sigma (ps)':<12} {'N trials'}")
    print(f"  {'-'*58}")
    for f in files:
        d = np.load(f)
        valid_trials = [row for row in d["trials"] if row.sum() > 0]
        rms_vals = [tie_rms(d["index"], row) for row in valid_trials]

        match = re.search(rf"tie_errorbars_{re.escape(prefix)}_([\d.eE+-]+)s_", f)
        duration = float(match.group(1))

        print(f"  {duration:<15.4g} {np.mean(rms_vals):<18.4f} {np.std(rms_vals):<12.4f} {len(rms_vals)}")
    print()


for prefix in ["free", "1.2km", "tt_jitter", "jacob"]:
    print(f"=== {prefix} ===")
    check_prefix(prefix)
