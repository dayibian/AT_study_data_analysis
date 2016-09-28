"""This is the code for e4 physiological data feature extraction."""

try:
    import cPickle as pickle
except:
    import pickle
import numpy as np
import matplotlib.pylab as plt
from scipy import signal
import peakutils as pu
    
def compute_heart_rate(hrData):
    try:
        return np.mean(hrData.Value)
    except:
        return 'NA'
        
def compute_ibi(ibiData):
    try:
        return np.mean(ibiData.Value)
    except:
        return 'NA'
        
def convert2list(data):
    """Covert data from pandas series to list."""
    data_l = []
    for i in range(len(data)):
        data_l.append(data.iloc[i].Value)
    return data_l
        
def plot_signal(data_l):
    plt.plot(data_l)
    plt.show()
    
def decompose_signal(gsr_l):
    """Decompose GSR signal into SCR and SCL respectively."""
    if len(gsr_l)<20:
        return 'NA','NA'
    b,a = signal.butter(4,0.5/2)
    gsr_filt = signal.filtfilt(b,a,gsr_l)
    b,a = signal.butter(4,0.05/2,'highpass')
    scr = signal.filtfilt(b,a,gsr_filt)
    scl = [x-y for x,y in zip(gsr_filt,scr)]
    return scr,scl
    
def compute_scl_fv(scl):
    if scl == 'NA':
        return 'NA','NA'
        
    scl_mean = np.mean(scl)
    scl_sd = np.std(scl)
    return scl_mean,scl_sd
    
def compute_scr_fv(scr,plot_peak=False):
    #peaks = signal.find_peaks_cwt(scr_lp,np.arange(1,20))
    if scr == 'NA':
        return 'NA','NA','NA','NA'
        
    peaks = pu.indexes(scr,0.6,15)
    t = len(scr)/float(4*60)
    scr_rate = len(peaks)/t
    
    if plot_peak == True:
        plt.figure()
        plt.plot(scr)
        for index in peaks:
            plt.plot(index,scr[index],'ro')
        plt.show()
    
    responses = [scr[i] for i in peaks]
    scr_mean = np.mean(responses)
    scr_sd = np.std(responses)
    scr_max = np.max(responses)
    return scr_rate, scr_mean, scr_sd, scr_max
    
if __name__ == '__main__':
    datafile = open('alldata_801.pkl','rb')
    alldata = pickle.load(datafile)
    for data in alldata:
        gsr = data['physioData']['gsrData']
        gsr_l = convert2list(gsr)
        scr,scl = decompose_signal(gsr_l)
        scr_rate, scr_mean, scr_sd, scr_max = compute_scr_fv(scr,True)
