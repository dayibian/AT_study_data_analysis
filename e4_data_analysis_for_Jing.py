import time
import numpy as np
import pandas as pd

# This package need to be installed to peak detection, use pip install peakutils
import peakutils as pu
from scipy import signal
import zipfile
import glob
from pathlib import Path
import pickle
import warnings

class Physio_data:
    def __init__(self, startsecs, PID):
        '''
        input: startsecs: This is the time your task starts,
                          It is seconds since epoch
                          https://docs.python.org/3/library/time.html
               PID: Path to your participant folder, assuming you put the data in a folder named by participant ID
        '''
        self.startsecs = startsecs
        with open(PID/'EDA.csv', 'r') as f:
            EDA_lines = f.readlines()
        with open(PID/'BVP.csv', 'r') as f:
            BVP_lines = f.readlines()
        with open(PID/'HR.csv', 'r') as f:
            HR_lines = f.readlines()
        with open(PID/'IBI.csv', 'r') as f:
            self.IBI_lines = f.readlines()

        # Get all the data you have recorded
        self.EDA_ = np.array([float(d.strip()) for d in EDA_lines])
        self.BVP_ = np.array([float(d.strip()) for d in BVP_lines])
        self.HR_ = np.array([float(d.strip()) for d in HR_lines])
        self.IBI_ = pd.read_csv(PID/'IBI.csv',skiprows=[0],names=['time','ibi'])
    def get_EDA(self):
        '''
        This method and the following three medthods segment your data into a list of numpy arrays
        You might need to rewrite this part according to your task data
        '''
        start_time = self.EDA_[0]
        freq = int(self.EDA_[1])
        offset = int(self.startsecs-start_time)
        EDA_ = self.EDA_[offset+2:]
        self.EDA = [EDA_[(50+15)*freq*i:(50+15)*freq*i+50*freq] for i in range(6)]
    def get_BVP(self):
        start_time = self.BVP_[0]
        freq = int(self.BVP_[1])
        offset = int(self.startsecs-start_time)
        BVP_ = self.BVP_[offset+2:]
        self.BVP = [BVP_[(50+15)*freq*i:(50+15)*freq*i+50*freq] for i in range(6)]
    def get_HR(self):
        start_time = self.HR_[0]
        freq = int(self.HR_[1])
        offset = int(self.startsecs-start_time)
        HR_ = self.HR_[offset+2:]
        self.HR = [HR_[(50+15)*freq*i:(50+15)*freq*i+50*freq] for i in range(6)]
    def get_IBI(self):
        start_time = float(self.IBI_lines[0].split(',')[0])
        offset = int(self.startsecs-start_time)
        time_intervals = [(offset+(50+15)*i, offset+(50+15)*i+50) for i in range(6)]
        self.IBI = [[] for _ in range(6)]
        for i in range(6):
            interval = time_intervals[i]
            trial = self.IBI_[self.IBI_.time<interval[1]][self.IBI_.time>interval[0]]
            self.IBI[i] = trial.ibi.values
    def process(self):
        self.get_EDA()
        self.get_BVP()
        self.get_HR()
        self.get_IBI()

class Physio_features:
    def __init__(self):
        '''
        self.features is a list of eight features, length of list depends on your segments
        I hard coded 6 here, you need to change it
        '''
        self.feature_names = ['hr', 'ibi', 'scl_mean', 'scl_std',
                              'scr_rate', 'scr_mean', 'scr_std', 'scr_max']
        self.features = [[] for _ in range(6)]
    def extract_bvp_fv(self, hrs, ibis):
        '''
        This method use hr data and ibi data to directly get hr and ibi feature
        '''
        for i in range(len(hrs)):
            self.features[i].append(np.mean(hrs[i]))
            self.features[i].append(np.mean(ibis[i]))
    def extract_eda_fv(self, edas):
        '''
        This method extract EDA features
        '''
        for i in range(len(edas)):
            eda = edas[i]
            scr,scl = self.decompose_eda(eda)
            self.features[i].append(np.mean(scl))
            self.features[i].append(np.std(scl))
            for fv in self.compute_scr_fv(scr):
                self.features[i].append(fv)
    def decompose_eda(self, eda):
        """Decompose EDA signal into SCR and SCL respectively."""
        if len(eda)<20:
            return 'NA','NA'
        b,a = signal.butter(4,0.5/2)
        gsr_filt = signal.filtfilt(b,a,eda)
        b,a = signal.butter(4,0.05/2,'highpass')
        scr = signal.filtfilt(b,a,gsr_filt)
        scl = [x-y for x,y in zip(gsr_filt,scr)]
        return scr,scl
    def compute_scr_fv(self, scr):
        #peaks = signal.find_peaks_cwt(scr_lp,np.arange(1,20))
        if scr == 'NA':
            return 'NA','NA','NA','NA'

        peaks = pu.indexes(scr,0.6,15)
        t = len(scr)/float(4*60)
        scr_rate = len(peaks)/t

        responses = [scr[i] for i in peaks]
        scr_mean = np.mean(responses)
        scr_sd = np.std(responses)
        scr_max = np.max(responses)
        return scr_rate, scr_mean, scr_sd, scr_max

if __name__ == '__main__':
    '''
    An example
    '''
    PIDs = ['851']
    data_path = Path('../MADCAP_DATA')
    results = []
    for PID in PIDs:
        print('Processing '+PID+' now.')
        allFeatures = []
        datafolder = data_path/PID
        physio_zipfile = list(datafolder.glob('*.zip'))[0]
        with zipfile.ZipFile(physio_zipfile) as f:
            f.extractall(datafolder)

        # Get startsecs from your task data
        # avInfo = AV_info(av_file)
        # avInfo.process()
        # startsecs = avInfo.startsecs

        physioData = Physio_data(startsecs, datafolder)
        physioData.process()
        eda = physioData.EDA
        bvp = physioData.BVP
        hr = physioData.HR
        ibi = physioData.IBI
        physioFeatures = Physio_features()
        physioFeatures.extract_bvp_fv(hr, ibi)
        physioFeatures.extract_eda_fv(eda)