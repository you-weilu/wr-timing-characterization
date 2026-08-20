"""
    examples for TimeTagger, an OpalKelly based single photon counting library
    Copyright (C) 2013-2015  Helmut Fedder helmut@swabianinstruments.com

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License along
    with this program; if not, write to the Free Software Foundation, Inc.,
    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
"""
"""
    My notes:
    The main API is written in c++
    There are wrappers classes provided for python that are used to access API written in C++
    -Need only 2 classes to write code: (1) timetagger, (2) some base measurement method
    -running program may have folder dependicies.  Safest to run program from python example folder
    in case access to nearby folders is required.
    
    ******************************************special note**************************************************
    Python GUI examples requre installation of the following packages: traits, traitsui, chaco, pyface enable
    ********************************************************************************************************
    other requirements: windows 10 x64 down to windows 7x32, a seperate installer for 32, 64 bit systems
    other python packages: numpy, matplotlib(pylab), time, cPickle 
    -no installer for linux yet, you would have to contact the company to get it as of 07/2018
    UNITS: all time units measured and entered in (ps)
    
    *****************************************************************************************
    WARNINGS: 
    I'm assuming something could possibly be damaged if you do not ensure the 
    internal signal generator is DISABLED and apply an external signal.  There is an onchip signal generator
      Just make sure in any program you write that you EXPLICITLY "disable" the 
    internal function generator
    ***************************************************************************************
"""
import os
import sys  # module for system specific parameters and functions
from time import sleep
from TimeTaggerRPC import client
import numpy as np
import TimeTagger as TTX

from pylab import *
#import  the core parts of numpy, scipy, and matplotlib. notice lack of import numpy, import scipy, import matplotlib
tagger = TTX.createTimeTagger(serial = '23010013TP')


		#every measurement requires an instance of the time tagger class
#tagger.reset(); #reset the time tagger to the startup state
CHAN1 = 1
CHAN2 = 2

	#set trigger levels
	#tagger.setTriggerLevel(4,0.13)
	#tagger.setTriggerLevel(1,0.12)
	#tagger.setTriggerLevel(2,0.14)
tagger.setTriggerLevel(CHAN1,0.4)
tagger.setTriggerLevel(CHAN2,0.4)

	#tagger.setConditionalFilter(trigger=[2], filtered=[9])
	
	#if you have a long delay, then the jit ter will change enough to change the counts for electrical signals used to test the code
	#minimize delay after figuring out the propagation delay.  No plots, no displaying of text??? 
	#need binwidth*n_bins=clock period in (ps)
	#you should choose a binwdith > "total" system jitter
	#1000ps=1ns bin width, #bins=1000, then 1us cycles for 1MHz count rate
	

	# wait until the 1000 values should be filled
	# 
dataCNT=np.array([0*np.arange(0,600,1)]) #initialize array of zeros of size N-1=5-1=4
	
rate00 = TTX.Countrate(tagger, channels=[CHAN1]) # 15.93
rate11 = TTX.Countrate(tagger, channels=[CHAN2]) # channel 6 15.35
	
	#rate0 = TT.Countrate(tagger, channels=[2]) # channel 7  18.28
	#rate1 = TT.Countrate(tagger, channels=[3])  # channel 8 18.04
	#rateC = TT.Countrate(tagger, channels=[8]) #clock
	#print('event divider factor for channel 0 ',tagger.getEventDivider(0))
	#print('event divider factor for channel 1 ',tagger.getEventDivider(1))
	#print('event divider factor for channel 3 ',tagger.getEventDivider(3))
tagger.sync()
for jj in range(0,5000,1):
	#	rate0.clear()
	#	rate1.clear()
	rate00.clear()
	rate11.clear()
	#	rateC.clear()
	tagger.sync()
	sleep(1)
		
		
		#sleep(5)
	print ('Ch1: ',rate00.getData(),'Ch2: ', rate11.getData())
		#scanTIME = str(input('continue?'))

		#print ( 'Clock: ', rateC.getData(), 'Ch0(1290 good): ',rate00.getData(),'Ch1(1290_bad): ', rate11.getData(),'Ch2(1310 atherm): ', rate0.getData(),'Ch3(1310 PA): ', rate1.getData())
		
	
	#rate.stop()



