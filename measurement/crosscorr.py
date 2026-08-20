#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  crosscorr.py
#  
#  Copyright 2021 Jordan <Jordan@DESKTOP-LJEHFUG>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  

"""
This example shows how to use FileWriter and FileReader for writing and reading
the time tag stream onto a disk.

"""

import os

#from TimeTagger import createTimeTagger, FileWriter, FileReader,TimeTaggerVirtual, Countrate,StartStop,Correlation,createTimeTaggerVirtual
import numpy as np
import sys
sys.modules[__name__].__dict__.clear()
import numpy as np
from TimeTaggerRPC import client
from time import sleep
import scipy.io as sio #import one method of scipy such as input output. Refer to it by the alias "sio"
import matplotlib.pyplot as plt
import tempfile


#from TimeTagger import createTimeTagger, FileWriter, FileReader,TimeTaggerVirtual, Countrate,StartStop,Correlation,createTimeTaggerVirtual


with client.createProxy(host='129.105.6.161',port=23000)as TT:

	channels = [2, 3]
	
	tagger = TT.createTimeTagger(serial = '1740000JEA') #1 of your classes. Creates the hardware access.  can leave argument blank if only 1 time tagger
	tagger.setTestSignal(2, False)
	tagger.setTestSignal(3, False)
	tagger.setTestSignal(1, False)
	tagger.setTestSignal(4, False)
	print("")
	print("Wait until the changes are applied (sync).")
	tagger.sync()

	VTH=0.150#(V) 
#set trigger levels that work with superconducting detectors 11/16/18, do NOT change
	tagger.setTriggerLevel(4,VTH)
	tagger.setTriggerLevel(1,VTH)
	tagger.setTriggerLevel(2,VTH)
	tagger.setTriggerLevel(3,VTH)
	print('set dead time')
	tagger.setDeadtime(1,int(15*1e3))
	tagger.sync()#ensure changes have been made
	print('dead time of CH 1: ',tagger.getDeadtime(1))
	print('set dead time')
	tagger.setDeadtime(4,int(15*1e3))
	tagger.sync()#ensure changes have been made
	print('dead time of CH 0: ',tagger.getDeadtime(4))
	tagger.sync()

	print("""
********************************************************
*  STEP 1: Write events from two channels into a file.
********************************************************
""")

	scanTIME = int(input('How long do you want to record? (in seconds ): '))

	delay = 30700
	channel_to_delay = 3
	tagger.setDelaySoftware(2,delay)
	tagger.setDelaySoftware(1,delay)
	tagger.setDelaySoftware(3,delay)
	tagger.setDelaySoftware(4,delay)




	CHAN_A = 3
	CHAN_B = 1
	bs=1000#bin size
	nb=200
	ccw=10000
	#ttv = createTimeTaggerVirtual()
	crate = TT.Countrate(tagger, [2, 3])
	#crate = TT.Countrate(tagger, [CHAN_A, CHAN_B])
	CORR=TT.Correlation(tagger,channel_1=CHAN_A,channel_2=CHAN_B,binwidth=1000,n_bins=900000)
	sleep(scanTIME)
	rate0 = TT.Countrate(tagger, channels=[2])
	rate1 = TT.Countrate(tagger, channels=[3])
# Wait until the file reading is finished
	#ttv.waitForCompletion()
	print("File streaming completed.")
	crate.stop()
	ch0_CR=crate.getData()[0]
	ch1_CR=crate.getData()[1]
	CCR_TIMES=CORR.getIndex()
	CCR_CNTS=CORR.getData()
	sleep(1)
	crate.clear()
	CORR.stop()
		
	#ttv.sync() #added 01-06-2020
	sleep(1)
	print('avg count rate on ch2: ',ch0_CR)
	print('avg count rate on ch3: ',ch1_CR)
	print('total aquisition time: ',scanTIME)
	
	#print('avg count rate on ch0: ',rate0)
	#print('avg count rate on ch1: ',rate1)
	#print('total aquisition time: ',scanTIME)
	#plt.plot(CCR_TIMES[1:200,0],CCR_CNTS[1:200,0])
	plt.plot(CCR_TIMES,CCR_CNTS)
	plt.show()
	#xlabel('Time [ps]')
	#ylabel('Clicks')
	
	propagation_delay = int(abs(CORR.getIndex()[CORR.getData().argmax()]))
	#propagation_delay = int(CORR.getData().argmax())
	print('time delay: ',propagation_delay)
	print('max CC: ',CORR.getData().argmax())
	print('max CC: ',CORR.getData()[CORR.getData().argmax()])
	CORR.clear()
	# Free Virtual Time Tagger resources
	TT.freeTimeTagger(tagger)
	#ch0_and_ch1 = Coincidence(tagger, channels=[1,3], coincidenceWindow=propagation_delay)
	
	


