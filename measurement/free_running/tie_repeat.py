# tie_repeat.py
#
# Repeated independent trials at specific (longer) checkpoint durations,
# same pattern as tie_100ns.py / tie_1ms.py, generalized to redo multiple
# far points from the continuous run in one script.

from Swabian import TimeTagger
import numpy as np
import time
from datetime import datetime

# ============ CONFIGURATION ============
ch_master = 3
ch_slave = 4

BINWIDTH = 1
N_BINS = 2000

MIN_DURATION_SEC = 1e-6
MAX_DURATION_SEC = 1e-2
NUM_CHECKPOINTS = 20
NUM_TRIALS = 50

TRIGGER_LEVEL_V = 0.1

PREFIX = "jacob"

# ========================================

DURATIONS_TO_REDO = np.unique(np.logspace(
    np.log10(MIN_DURATION_SEC),
    np.log10(MAX_DURATION_SEC),
    NUM_CHECKPOINTS
))

tagger = TimeTagger.createTimeTagger()
print("Connected Device Serial:", tagger.getSerial())

tagger.setTriggerLevel(ch_master, TRIGGER_LEVEL_V)
tagger.setTriggerLevel(ch_slave, TRIGGER_LEVEL_V)

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
    fname = f"../../data/tie_histogram_{PREFIX}_{TRIAL_DURATION_SEC:.4g}s_{timestamp}.npz"
    np.savez(fname, index=index, data=combined_data)
    print(f"Saved combined histogram to {fname}")

TimeTagger.freeTimeTagger(tagger)
print("\nAll durations complete.")