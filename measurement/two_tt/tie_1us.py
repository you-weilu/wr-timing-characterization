# tie_1us.py
#
# Repeated independent short-duration Correlation measurements:
# same Time Tagger connection stays open, but each trial creates a fresh
# Correlation object and runs for a fixed short duration, giving genuinely
# independent trials rather than one long continuous accumulation.

from Swabian import TimeTagger
import numpy as np
import time
from datetime import datetime

# ============ CONFIGURATION ============
ch_master = 3
ch_slave = 4

BINWIDTH = 1
N_BINS = 2000

TRIAL_DURATION_SEC = 1e-6   # 1us per trial
NUM_TRIALS = 1000

# ========================================

tagger = TimeTagger.createTimeTagger()
print("Connected Device Serial:", tagger.getSerial())

# Set reference Clock (to master)
tagger.setReferenceClock(
    clock_channel=ch_master,
    clock_frequency=10e6,
    time_constant=1e-3,
    synchronization_offset=0,
    wait_until_locked=True
)
print("Reference Clock locked.")

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
combined_data = all_data.sum(axis=0) # collapse into one histogram
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
np.savez(f"../../data/tie_histogram_refclk_{TRIAL_DURATION_SEC:.4g}s_{timestamp}.npz", index=index, data=combined_data)
print(f"Saved combined histogram from {NUM_TRIALS} trials to ../data/tie_histogram_refclk_1us_{timestamp}.npz")
