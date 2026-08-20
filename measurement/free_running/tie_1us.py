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
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"

# ============ CONFIGURATION ============
ch_master = 1
ch_slave = 2

BINWIDTH = 1
N_BINS = 2000

TRIAL_DURATION_SEC = 1e-6 # 1us
NUM_TRIALS = 1000
SW_DELAY = 2000 # in ps

# wr clk_out ≈ 950mV
TRIGGER_LEVEL_V = 0 # Trigger_level = 50% peak voltage

PREFIX = "b2b"

# ========================================

tagger = TimeTagger.createTimeTagger('23010013TP')
print("Connected Device Serial:", tagger.getSerial())

tagger.setTriggerLevel(ch_master, TRIGGER_LEVEL_V)
tagger.setTriggerLevel(ch_slave, TRIGGER_LEVEL_V)

all_data = []   # one histogram (array) per trial
index = None
corr = TimeTagger.Correlation(tagger, ch_master, ch_slave, binwidth=BINWIDTH, n_bins=N_BINS)

# delay to account for offset
tagger.setDelaySoftware(2,SW_DELAY)

for trial in range(NUM_TRIALS):
    corr.startFor(int(TRIAL_DURATION_SEC * 1e12))  # startFor takes picoseconds
    corr.waitUntilFinished()

    if index is None:
        index = corr.getIndex()   # returns an array of ps time-difference value that each bin represents

    data = corr.getData()
    total_counts = data.sum()
    all_data.append(data)

    print(f"Trial {trial+1}/{NUM_TRIALS} — total counts: {total_counts}")

    corr.clear()  # discard; next loop iteration reuses the same object

TimeTagger.freeTimeTagger(tagger)

# Save all trials together: one 2D array (trials x bins), plus shared bin index
all_data = np.array(all_data)
combined_data = all_data.sum(axis=0) # collapse into one histogram
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
out_path = DATA_DIR / f"tie_histogram_{PREFIX}_{TRIAL_DURATION_SEC:.4g}s_{timestamp}.npz"
np.savez(out_path, index=index, data=combined_data)
print(f"Saved combined histogram from {NUM_TRIALS} trials to {out_path}")