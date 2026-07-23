import numpy as np
import time

# Define synchronization channels
ch_master = 3
ch_slave = 4

# Enable the ReferenceClock using the first external reference
tt.setReferenceClock(clock_channel=ch_master, clock_frequency=10e6)

# Define measurement steps (logarithmically spaced averaging times)
steps = np.unique(np.logspace(0, 7, 100, dtype=np.int64))

# Initialize Frequency Stability measurement on the second reference
fs = TT.FrequencyStability(tt, ch_slave, steps, average=1)

# Allow the measurement to collect data
time.sleep(100)

# Retrieve frequency stability results
obj = fs.getDataObject()
tau = obj.getTau()
ADEV = obj.getADEV()
TDEV = obj.getTDEV()
MDEV = obj.getMDEV()