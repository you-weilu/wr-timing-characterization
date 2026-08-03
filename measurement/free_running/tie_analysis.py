# tie_analysis.py
#
# Raw TIE (Correlation histogram) snapshots between two WR-LEN clock outputs,
# taken at multiple elapsed-time checkpoints from a single continuous run.

from Swabian import TimeTagger
import numpy as np
import time
from datetime import datetime

# Configuration
ch_master = 3   # WR-LEN #1 clock output
ch_slave = 4    # WR-LEN #2 clock output

BINWIDTH = 1         # ps resolution
N_BINS = 2000        # span = binwidth * n_bins = 2000 ps = +- 1000 ps window

TRIGGER_LEVEL_V = 0.1

# Checkpoints: elapsed seconds at which to snapshot the histogram
# Logarithmically spaced
# 10ms to 1hr
MIN_CHECKPOINT_SEC = 1e-2
MAX_CHECKPOINT_SEC = 3600
NUM_CHECKPOINTS = 25

CHECKPOINTS_SEC = np.unique(np.logspace(
    np.log10(MIN_CHECKPOINT_SEC),
    np.log10(MAX_CHECKPOINT_SEC),
    NUM_CHECKPOINTS
))

tagger = TimeTagger.createTimeTagger()
print("Connected Device Serial:", tagger.getSerial())

tagger.setTriggerLevel(ch_master, TRIGGER_LEVEL_V)
tagger.setTriggerLevel(ch_slave, TRIGGER_LEVEL_V)

corr = TimeTagger.Correlation(tagger, ch_master, ch_slave, binwidth=BINWIDTH, n_bins=N_BINS)
corr.start()

elapsed = 0
for checkpoint in CHECKPOINTS_SEC:
    segment_duration = checkpoint - elapsed
    if segment_duration <= 0:
        continue

    corr.startFor(int(segment_duration * 1e12), clear=False)  # ps, keep accumulating)
    corr.waitUntilFinished()

    elapsed = checkpoint

    index = corr.getIndex()   # ps bin values (x-axis)
    data = corr.getData()     # coincidence counts in bins (y-axis)

    print(f"Checkpoint {checkpoint:.4g}s reached, saving histogram...")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    np.savez(f"../../data/tie_histogram_tt_jitter_{checkpoint:.4g}s_{timestamp}.npz", index=index, data=data)

corr.stop()
TimeTagger.freeTimeTagger(tagger)
print("Done.")