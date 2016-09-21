try:
    import cPickle as pickle
except:
    import pickle
import numpy as np
    
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
    
if __name__ == '__main__':
    datafile = open('alldata.pkl','rb')
    alldata = pickle.load(datafile)
    for data in alldata:
        ibidata = data['physioData']['hrData']
        hr = compute_heart_rate(ibidata)
        print hr
    