# tie_10ms.py
#
# Repeated independent short-duration Correlation measurements (option B):
# same Time Tagger connection stays open, but each trial creates a fresh
# Correlation object and runs for a fixed short duration, giving genuinely
# independent trials rather than one long continuous accumulation.
#
# Testing hypothesis: is the zero-count behavior seen at 1ms/10ms in the
# continuous run a ONE-TIME warm-up cost (only trial 1 would be zero),
# or an inherent per-measurement-object latency (ALL trials would be zero)?

from Swabian import TimeTagger
import numpy as np
import time
from datetime import datetime

# ============ CONFIGURATION ============
ch_master = 3
ch_slave = 4

BINWIDTH = 1
N_BINS = 2000

TRIAL_DURATION_SEC = 10e-3   # 10ms per trial
NUM_TRIALS = 1000

# ========================================

tagger = TimeTagger.createTimeTagger()
print("Connected Device Serial:", tagger.getSerial())

all_data = []   # one histogram (array) per trial
index = None

for trial in range(NUM_TRIALS):
    corr = TimeTagger.Correlation(tagger, ch_master, ch_slave, binwidth=BINWIDTH, n_bins=N_BINS)
    corr.startFor(int(TRIAL_DURATION_SEC * 1e12))  # startFor takes picoseconds
    corr.waitUntilFinished()

    if index is None:
        index = corr.getIndex()   # returns an array of ps time-difference value that each bin represents

    data = corr.getData()
    total_counts = data.sum()
    all_data.append(data)

    print(f"Trial {trial+1}/{NUM_TRIALS} — total counts: {total_counts}")

    del corr  # discard; next loop iteration creates a fresh object

TimeTagger.freeTimeTagger(tagger)

# Save all trials together: one 2D array (trials x bins), plus shared bin index
all_data = np.array(all_data)
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
np.savez(f"../data/tie_repeated_trials_10ms_{timestamp}.npz", index=index, data=all_data)
print(f"Saved {NUM_TRIALS} trials to ../data/tie_repeated_trials_10ms_{timestamp}.npz")