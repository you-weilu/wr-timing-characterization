# ADEV data collection script

from Swabian import TimeTagger
import numpy as np
import time

tagger = TimeTagger.createTimeTagger()
print("Connected Device Serial:", tagger.getSerial())

# physical channels
CLOCK_CHANNEL = 3 # WR-LEN 10MHz Output
SYNC_CHANNEL = 4 # WR-LEN 1PPS output

### Set Reference Clock ###

tagger.setReferenceClock(
    clock_channel=CLOCK_CHANNEL,
    clock_frequency=10e6,
    time_constant=1e-3,
    synchronization_channel=SYNC_CHANNEL,
    synchronization_offset=0,
    wait_until_locked=True
)

print("Reference Clock locked.")

# Check the state of the lock
state = tagger.getReferenceClockState()
print("Reference Clock state:", state)

TimeTagger.freeTimeTagger(tagger)




