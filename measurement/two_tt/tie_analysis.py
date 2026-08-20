# tie_analysis.py
#
# Raw TIE (Correlation histogram) snapshots between two WR-LEN clock outputs,
# taken at multiple elapsed-time checkpoints from a single continuous run.
#
# Setup: two Time Taggers (USB, same PC), each disciplined by a shared
# external frequency generator on ch_ref. Each tagger tags the clock output
# of one WR-LEN module on ch_signal, and the WR-LEN's 1PPS output on ch_pps
# for absolute epoch alignment. The two taggers are combined into a
# single TimeTaggerNetwork so their channels can be cross-correlated;
# channels from the second (slave) server are offset by 1000.

from Swabian import TimeTagger
import numpy as np
import time
from datetime import datetime

# Configuration
SERIAL_MASTER = '23010013TP'
SERIAL_SLAVE = '232800150J'

PORT_MASTER = 41101
PORT_SLAVE = 41102

ch_ref = 15     # shared external frequency generator input (time base)
ch_pps = 2      # WR-LEN 1PPS output (absolute epoch alignment)
ch_signal = 1   # WR-LEN clock output being tagged

ch_master = ch_signal            # master tagger, WR-LEN #1 clock output
ch_slave = ch_signal + 1000      # slave tagger, WR-LEN #2 clock output (network channel offset)

BINWIDTH = 1         # ps resolution
N_BINS = 2000        # span = binwidth * n_bins = 2000 ps = +- 1000 ps window
SW_DELAY = 2000      # in ps

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

tagger_master = TimeTagger.createTimeTagger(SERIAL_MASTER)
tagger_slave = TimeTagger.createTimeTagger(SERIAL_SLAVE)
print("Master Tagger Serial:", tagger_master.getSerial())
print("Slave Tagger Serial:", tagger_slave.getSerial())

# Lock each tagger's internal timebase to the shared external frequency generator,
# and align both taggers' absolute epoch using each WR-LEN's 1PPS output.
for tagger in (tagger_master, tagger_slave):
    tagger.setReferenceClock(
        clock_channel=ch_ref,
        clock_frequency=10e6,
        time_constant=1e-3, # how long the sw PLL averages over when estimating the clock signal's frequency
        synchronization_channel=ch_pps,
        synchronization_offset=0,
        wait_until_locked=True
    )
print("Reference clocks locked.")

tagger_master.startServer(TimeTagger.AccessMode.Control, port=PORT_MASTER)
tagger_slave.startServer(TimeTagger.AccessMode.Control, port=PORT_SLAVE)

network = TimeTagger.createTimeTaggerNetwork([f"localhost:{PORT_MASTER}", f"localhost:{PORT_SLAVE}"])

corr = TimeTagger.Correlation(network, ch_master, ch_slave, binwidth=BINWIDTH, n_bins=N_BINS)
corr.start()

# delay to account for offset
network.setDelaySoftware(ch_slave, SW_DELAY)

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
    np.savez(f"../../data/tie_histogram_refclk_{checkpoint:.4g}s_{timestamp}.npz", index=index, data=data)

corr.stop()
TimeTagger.freeTimeTagger(network)
tagger_master.stopServer()
tagger_slave.stopServer()
TimeTagger.freeTimeTagger(tagger_master)
TimeTagger.freeTimeTagger(tagger_slave)
print("Done.")
