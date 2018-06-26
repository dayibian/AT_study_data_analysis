# -*- coding: utf-8 -*-
"""
Created on Tue May 16 18:00:05 2017

@author: biand
"""

import matplotlib.pyplot as plt
import cPickle as pickle

with open('alldata_801.pkl','rb') as f:
    data = pickle.load(f)
    
physioData = data[1]['physioData']

bvp = physioData['bvpData']
gsr = physioData['gsrData']
#hr = physioData['hrData']

fig = plt.figure()
ax1 = fig.add_subplot(2,1,1)
ax2 = fig.add_subplot(2,1,2)
#ax3 = fig.add_subplot(3,1,3)

bvp.plot(use_index=False,ax=ax1,title='PPG data',legend=False)
gsr.plot(use_index=False,ax=ax2,title='GSR data',legend=False)
#hr.plot(use_index=False,ax=ax3,title='HR data',legend=False)

plt.tight_layout()

plt.savefig('physioplot1.png',dpi=400)