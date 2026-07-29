# tie_repeat.py
#
# Repeated independent trials at specific (longer) checkpoint durations,
# generalized to redo multiple far points from the continuous run in one script.

from Swabian import TimeTagger
import numpy as np
import time
from datetime import datetime

# ============ CONFIGURATION ============
ch_master = 3
ch_slave = 4

BINWIDTH = 1
N_BINS = 2000

# Array of durations to redo
DURATIONS_TO_REDO = [0.0009091, 0.002154, 0.002503]
NUM_TRIALS = 50

# ========================================

tagger = TimeTagger.createTimeTagger()
print("Connected Device Serial:", tagger.getSerial())

for TRIAL_DURATION_SEC in DURATIONS_TO_REDO:
    print(f"\n=== Starting {NUM_TRIALS} trials at {TRIAL_DURATION_SEC}s each ===")

    all_data = []
    index = None

    for trial in range(NUM_TRIALS):
        corr = TimeTagger.Correlation(tagger, ch_master, ch_slave, binwidth=BINWIDTH, n_bins=N_BINS)
        corr.startFor(int(TRIAL_DURATION_SEC * 1e12))
        corr.waitUntilFinished()

        if index is None:
            index = corr.getIndex()

        data = corr.getData()
        total_counts = data.sum()
        all_data.append(data)

        print(f"  Trial {trial+1}/{NUM_TRIALS} — total counts: {total_counts}")
        del corr

    all_data = np.array(all_data)
    combined_data = all_data.sum(axis=0)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    fname = f"../../data/tie_histogram_{TRIAL_DURATION_SEC:.4g}s_{timestamp}.npz"
    np.savez(fname, index=index, data=combined_data)
    print(f"Saved combined histogram to {fname}")

TimeTagger.freeTimeTagger(tagger)
print("\nAll durations complete.")