import TimeTagger

# Initialize device (uses default Standard resolution mode)
tagger = TimeTagger.createTimeTagger()

print("Connected Device Serial:", tagger.getSerial())

# Routes onboard test signal generator to channels 1 and 2
tagger.setTestSignal([1, 2], True)

# Measure average count rate on channels 1 and 2
cr = TimeTagger.Countrate(tagger, [1, 2])
cr.startFor(int(1e12), clear=True)  # Run for 1 second (1e12 ps)
cr.waitUntilFinished()

print("Measured Count Rates (cps):", cr.getData())

# Clean up
TimeTagger.freeTimeTagger(tagger)