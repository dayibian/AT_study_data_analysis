import time
import numpy as np
import pandas as pd
import peakutils as pu
from scipy import signal
import zipfile
import glob
from pathlib import Path
import pickle
import warnings

warnings.filterwarnings('ignore')

class AV_info:
    def __init__(self, filename):
        self.stimuli_duration = 50
        self.rest_interval = 15
        self.startsecs = 0
        self.PID = ''
        self.stimulus_order = []
        self.stimulus_info = ['native_w_touch', 'native_w/o_touch',
                              'nonnative_w_touch', 'nonnative_w/o_touch',
                              'native_async_w_touch', 'native_async_w/o_touch']
        with open(filename, 'r') as f:
            self.lines = f.readlines()
    def get_start_secs(self):
        t = self.lines[1].split()
        t = ':'.join(t[0].split(':')[:3])
        d = self.lines[16].split()[2]
        dt = d + ' ' + t
        self.startsecs = time.mktime(time.strptime(dt, '%m/%d/%Y %H:%M:%S'))
    def get_PID(self):
        self.PID = self.lines[15].split()[2]
    def get_order(self):
        order = self.lines[18].split()[3:]
        self.stimulus_order = [int(o) for o in order]
    def process(self):
        self.get_start_secs()
        self.get_PID()
        self.get_order()

class Physio_data:
    def __init__(self, startsecs, PID):
        self.startsecs = startsecs
        with open(PID/'EDA.csv', 'r') as f:
            EDA_lines = f.readlines()
        with open(PID/'BVP.csv', 'r') as f:
            BVP_lines = f.readlines()
        with open(PID/'HR.csv', 'r') as f:
            HR_lines = f.readlines()
        with open(PID/'IBI.csv', 'r') as f:
            self.IBI_lines = f.readlines()
        self.EDA_ = np.array([float(d.strip()) for d in EDA_lines])
        self.BVP_ = np.array([float(d.strip()) for d in BVP_lines])
        self.HR_ = np.array([float(d.strip()) for d in HR_lines])
        self.IBI_ = pd.read_csv(PID/'IBI.csv',skiprows=[0],names=['time','ibi'])
    def get_EDA(self):
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
        self.feature_names = ['hr', 'ibi', 'scl_mean', 'scl_std',
                              'scr_rate', 'scr_mean', 'scr_std', 'scr_max']
        self.features = [[] for _ in range(6)]
    def extract_bvp_fv(self, hrs, ibis):
        for i in range(6):
            self.features[i].append(np.mean(hrs[i]))
            self.features[i].append(np.mean(ibis[i]))
    def extract_eda_fv(self, edas):
        for i in range(6):
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

class ET_data:
    def __init__(self, startsecs, filename):
        with open(filename) as f:
            lines = f.readlines()
        rec_time = lines[13].split('  ')[1]
        rec_time = '-'.join(rec_time.split('-')[:3])
        rec_date = lines[8].split('  ')[1].strip()
        dt = rec_date + ' ' + rec_time
        rec_secs = time.mktime(time.strptime(dt, '%m-%d-%Y %H-%M-%S'))
        offset = int(startsecs - rec_secs)
        self.df = pd.DataFrame(data=[l.split() for l in lines[18+offset*120:]],
                        columns=lines[17].split())
        self.df = self.df.apply(lambda x:pd.to_numeric(x,errors='ignore'))
    def get_data(self):
        freq = 120
        self.ETdata = [self.df.iloc[(50+15)*freq*i:(50+15)*freq*i+50*freq, :]
                       for i in range(6)]
    def process(self):
        self.get_data()

class ET_features:
    def __init__(self):
        self.head = ((750,400),(1250,560))
        self.mouth = ((850,720),(1130,880))
        self.feature_names = ['attention_pct', 'roi_pct', 'eye_pct', 'mouth_pct']
        self.features = [[] for _ in range(6)]
    def extract_feature(self, ETdata):
        for i in range(6):
            self.features[i].append(self.compute_attention_percentage(ETdata[i]))
            self.features[i].append(self.compute_roi_percentage(self.gazePositions))
            self.features[i].append(self.compute_eye_pct(self.gazePositions))
            self.features[i].append(self.compute_mouth_pct(self.gazePositions))
        return self.features
    def compute_attention_percentage(self, etdata):
        sample_num = len(etdata)
        x = []
        y = []
        for i in range(sample_num):
            sample = etdata.iloc[i]
            if sample.GazeX!=None and 0<sample.GazeX<1 and 0<sample.GazeY<1:
                x.append(sample.GazeX)
                y.append(sample.GazeY)
        self.gazePositions = list(zip(x,y))
        try:
            attention_percentage = len(self.gazePositions)/float(sample_num)
        except ZeroDivisionError:
            attention_percentage = 'NA'
        return attention_percentage
    def check_hit(self, gazePosition, roi='all'):
        gazePosition_pixel = (gazePosition[0]*1920, gazePosition[1]*1080)
        hit = False
        if roi=='all':
            for roi in [self.head, self.mouth]:
                if (roi[0][0]<gazePosition_pixel[0]<roi[1][0] and 
                        roi[0][1]<gazePosition_pixel[1]<roi[1][1]):
                    hit = True
                    break
        elif roi=='mouth':
            for roi in [self.mouth]:
                if (roi[0][0]<gazePosition_pixel[0]<roi[1][0] and 
                        roi[0][1]<gazePosition_pixel[1]<roi[1][1]):
                    hit = True
                    break
        elif roi=='head':
            for roi in [self.head]:
                if (roi[0][0]<gazePosition_pixel[0]<roi[1][0] and 
                        roi[0][1]<gazePosition_pixel[1]<roi[1][1]):
                    hit = True
                    break
        return hit
    def compute_roi_percentage(self, gazePositions):
        sample_num = len(gazePositions)
        hit_num = 0
        for gazePosition in gazePositions:
            if self.check_hit(gazePosition, 'all'):
                hit_num += 1
        try:
            hit_percentage = hit_num/float(sample_num)
        except ZeroDivisionError:
            hit_percentage = 'NA'
        return hit_percentage
    def compute_eye_pct(self, gazePositions):
        sample_num = len(gazePositions)
        hit_num = 0
        for gazePosition in gazePositions:
            if self.check_hit(gazePosition, 'head'):
                hit_num += 1
        try:
            hit_percentage = hit_num/float(sample_num)
        except ZeroDivisionError:
            hit_percentage = 'NA'
        return hit_percentage
    def compute_mouth_pct(self, gazePositions):
        sample_num = len(gazePositions)
        hit_num = 0
        for gazePosition in gazePositions:
            if self.check_hit(gazePosition, 'mouth'):
                hit_num += 1
        try:
            hit_percentage = hit_num/float(sample_num)
        except ZeroDivisionError:
            hit_percentage = 'NA'
        return hit_percentage

if __name__ == '__main__':
    # PIDs = ['810v3', '817v4', '818v4', '822v3', '824v3', '826v3', '827v3',
    #     '830v3', '833v3', '835v3', '838v3', '843v2', '845',
    #     '847', '848', '849', '823v3', '829v2', '844v2']
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
        av_file = list(datafolder.glob('txtData*.txt'))[0]
        et_file = list(datafolder.glob('*.dat'))[0]

        avInfo = AV_info(av_file)
        avInfo.process()
        startsecs = avInfo.startsecs

        physioData = Physio_data(startsecs, datafolder)
        physioData.process()
        eda = physioData.EDA
        bvp = physioData.BVP
        hr = physioData.HR
        ibi = physioData.IBI
        physioFeatures = Physio_features()
        physioFeatures.extract_bvp_fv(hr, ibi)
        physioFeatures.extract_eda_fv(eda)
        
        etData = ET_data(startsecs, et_file)
        etData.process()
        etDf = etData.ETdata
        etFeature = ET_features()
        etFeature.extract_feature(etDf)
        allFeatures = np.concatenate((physioFeatures.features, etFeature.features), axis=1)

        feature_names = physioFeatures.feature_names + etFeature.feature_names

        order = avInfo.stimulus_order
        orderedFeatures = [[] for _ in range(6)]
        for i in range(6):
            o = order[i]
            orderedFeatures[i] = allFeatures[o]
        result = pd.DataFrame(data=orderedFeatures, columns=feature_names)
        result['PID'] = PID
        result['Session'] = range(1,7)
        results.append(result)
    results_df = pd.concat(results, ignore_index=True)
    with open('results.pkl', 'wb') as f:
        pickle.dump(results, f)
    results_df.to_csv('features_851.csv')
