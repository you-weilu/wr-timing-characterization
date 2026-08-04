# tie_errorbars.py
#
# Collects 1000 independent trials at each of several short averaging times.
# Saves individual trial histograms as a 2D array (trials x bins) so the
# plotting script can compute TIE RMS per trial and take the std as the error bar.
#
# Change DATA_PREFIX to "tt_jitter" when measuring TT internal jitter.

from Swabian import TimeTagger
import numpy as np
from datetime import datetime

# ============ CONFIGURATION ============
ch_master = 3
ch_slave = 4

BINWIDTH = 1
N_BINS = 2000

DATA_PREFIX = "free"  # change to "tt_jitter" for TT internal jitter measurements

DURATIONS_SEC = [1e-5, 1e-4, 1e-3, 1e-2, 1e-1]  # 10us to 100ms
NUM_TRIALS = 1000

TRIGGER_LEVEL_V = 0.1
# ========================================

tagger = TimeTagger.createTimeTagger()
print("Connected Device Serial:", tagger.getSerial())

tagger.setTriggerLevel(ch_master, TRIGGER_LEVEL_V)
tagger.setTriggerLevel(ch_slave, TRIGGER_LEVEL_V)

for duration in DURATIONS_SEC:
    print(f"\n=== {NUM_TRIALS} trials at {duration:.4g}s each ===")
    all_data = []
    index = None

    for trial in range(NUM_TRIALS):
        corr = TimeTagger.Correlation(tagger, ch_master, ch_slave, binwidth=BINWIDTH, n_bins=N_BINS)
        corr.startFor(int(duration * 1e12))
        corr.waitUntilFinished()

        if index is None:
            index = corr.getIndex()

        data = corr.getData()
        all_data.append(data)
        print(f"  Trial {trial+1}/{NUM_TRIALS} — counts: {data.sum()}")
        del corr

    all_data = np.array(all_data)  # shape: (NUM_TRIALS, N_BINS)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    fname = f"../../data/tie_errorbars_{DATA_PREFIX}_{duration:.4g}s_{timestamp}.npz"
    np.savez(fname, index=index, trials=all_data)
    print(f"Saved {NUM_TRIALS} trials to {fname}")

TimeTagger.freeTimeTagger(tagger)
print("\nDone.")
