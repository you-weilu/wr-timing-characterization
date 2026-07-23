# ADEV data collection script
# Measuring ADEV/TDEV/MDEV across a configurable range of averaging times.

from Swabian import TimeTagger
import numpy as np
import time
from datetime import datetime

# Configuration

CLOCK_FREQUENCY = 10e6         # Hz — WR-LEN reference clock frequency (10 MHz)
TIME_CONSTANT = 1e-3           # seconds — PLL response tuning (1 ms)

MIN_TAU = 100e-9               # seconds — shortest averaging time (100 ns = 1 period @ 10MHz)
MAX_TAU = 3600                 # seconds — longest averaging time (1 hour)
NUM_POINTS = 100                # number of logarithmically spaced tau points

AVERAGE = 1000                  # number of raw time-tags averaged before ADEV math

RUN_DURATION_SEC = 4 * 3600     # how long to actually collect data

ch_master = 3   # WR-LEN 10MHz output
ch_slave = 4    # second WR-LEN's clock output being compared


tagger = TimeTagger.createTimeTagger()
print("Connected Device Serial:", tagger.getSerial())

# Set Reference Clock
tagger.setReferenceClock(
    clock_channel=ch_master,
    clock_frequency=CLOCK_FREQUENCY,
    time_constant=TIME_CONSTANT,
    synchronization_offset=0,
    wait_until_locked=True
)

# Convert MIN_TAU / MAX_TAU into step-count exponents:
# steps = tau / period, where period = 1 / CLOCK_FREQUENCY
# np.log10 converts each into "what power of 10" for np.logspace's start/stop args
period = 1 / CLOCK_FREQUENCY
start_exp = np.log10(MIN_TAU / period)
stop_exp = np.log10(MAX_TAU / period)

steps = np.unique(np.logspace(start_exp, stop_exp, NUM_POINTS, dtype=np.int64))

# Initialize Frequency Stability measurement on the slave channel,
# comparing it against the Reference-Clock-disciplined internal timebase
fs = TimeTagger.FrequencyStability(tagger, ch_slave, steps, average=AVERAGE)

# Allow the measurement to collect data
print(f"Collecting data for {RUN_DURATION_SEC} seconds...")
time.sleep(RUN_DURATION_SEC)

# Retrieve frequency stability results
obj = fs.getDataObject()
tau = obj.getTau()
ADEV = obj.getADEV()
TDEV = obj.getTDEV()
MDEV = obj.getMDEV()

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
np.savez(f"data/adev_results_{timestamp}.npz", tau=tau, ADEV=ADEV, TDEV=TDEV, MDEV=MDEV)
print(f"Saved data/adev_results_{timestamp}.npz")

TimeTagger.freeTimeTagger(tagger)