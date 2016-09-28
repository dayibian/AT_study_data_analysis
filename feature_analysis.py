try:
    import cPickle as pickle
except:
    import pickle
import numpy as np

def compute_mean(l):
    s = 0
    count = 0
    for item in l:
        if item != 'NA' and item != 0:
            s += item
            count += 1
    if count != 0:
        return s/float(count)
    else:
        return 0
            
participantID_list = ['803','807']

feature_list = []
for participantID in participantID_list:
    participantID = participantID_list[0]
    featurefile_name = 'features_' + participantID +'.pkl'
    f = open(featurefile_name, 'rb')
    features = pickle.load(f)
    for feature in features:
        feature_list.append(feature)
        
print 'Length of feature list is:',len(feature_list)

attentionPercentage = []
attentionPercentage_wt = []
attentionPercentage_wot = []
roiPercentage = []
roiPercentage_wt = []
roiPercentage_wot = []

heartRate_wt = []
heartRate_wot = []
ibi_wt = []
ibi_wot = []
scrRate_wt = []
scrRate_wot = []
scrMean_wt = []
scrMean_wot = []
sclMean_wt = []
sclMean_wot = []

attentionPercentage_nat = []
attentionPercentage_nonnat = []
roiPercentage_nat = []
roiPercentage_nonnat = []

attentionPercentage_sync = []
attentionPercentage_async = []
roiPercentage_sync = []
roiPercentage_async = []

# Compute the overall attention rate
# Compute overall roi attention rate
# Compute screen attention rate for each condition
# Compute roi attention rate for each condition
# Compute average heart rate for each condition
# Compute average ibi for each condition

for feature in features:
    attentionPercentage.append(feature['attentionPercentage'])
    roiPercentage.append(feature['roiPercentage'])
    if feature['brushEnabled']:
        attentionPercentage_wt.append(feature['attentionPercentage'])
        roiPercentage_wt.append(feature['roiPercentage'])
        heartRate_wt.append(feature['heartRate'])
        ibi_wt.append(feature['ibi'])
        scrRate_wt.append(feature['scr_rate'])
        scrMean_wt.append(feature['scr_mean'])
        sclMean_wt.append(feature['scl_mean'])
    elif not feature['brushEnabled']:
        attentionPercentage_wot.append(feature['attentionPercentage'])
        roiPercentage_wot.append(feature['roiPercentage'])
        heartRate_wot.append(feature['heartRate'])
        ibi_wot.append(feature['ibi'])
        scrRate_wot.append(feature['scr_rate'])
        scrMean_wot.append(feature['scr_mean'])
        sclMean_wot.append(feature['scl_mean'])
        
    if (feature['stimulusName']=='native_low_1' or 
            feature['stimulusName']=='native_low_2'):
        attentionPercentage_nat.append(feature['attentionPercentage'])
        roiPercentage_nat.append(feature['roiPercentage'])
    elif (feature['stimulusName']=='nonnative_low_1' or 
            feature['stimulusName']=='nonnative_low_2'):
        attentionPercentage_nonnat.append(feature['attentionPercentage'])
        roiPercentage_nonnat.append(feature['roiPercentage'])
        
    if feature['stimulusName'].find('async') != -1:
        attentionPercentage_async.append(feature['attentionPercentage'])
        roiPercentage_async.append(feature['roiPercentage'])
    elif feature['stimulusName'].find('async') == -1:
        attentionPercentage_sync.append(feature['attentionPercentage'])
        roiPercentage_sync.append(feature['roiPercentage'])

print 'Overall attention rate is:',compute_mean(attentionPercentage)
print 'Attention rate for touch group is:',compute_mean(attentionPercentage_wt)
print 'Attention rate for non-touch group is:',compute_mean(attentionPercentage_wot)
print 'Overall roi attention rate is:',compute_mean(roiPercentage)
print 'Roi attention rate for touch group is:',compute_mean(roiPercentage_wt)
print 'Roi attention rate for non-touch group is:',compute_mean(roiPercentage_wot)
print 'Heart rate for touch group is:',np.mean(heartRate_wt)
print 'Heart rate for non-touch group is:',np.mean(heartRate_wot)
print 'Ibi for touch group is:',np.mean(ibi_wt)
print 'Ibi for non-touch group is:',np.mean(ibi_wot)
print 'scr rate for touch group is:',compute_mean(scrRate_wt)
print 'scr rate for non-touch group is:',compute_mean(scrRate_wot)
print 'scr mean for touch group is:',compute_mean(scrMean_wt)
print 'scr mean for non-touch group is:',compute_mean(scrMean_wot)
print 'scl mean for touch group is:',compute_mean(sclMean_wt)
print 'scl mean for non-touch group is:',compute_mean(sclMean_wot)

print 'Attention rate for sync group is:',compute_mean(attentionPercentage_sync)
print 'Attention rate for async group is:',compute_mean(attentionPercentage_async)
print 'Roi attention rate for sync group is:',compute_mean(roiPercentage_sync)
print 'Roi attention rate for async group is:',compute_mean(roiPercentage_async)

print 'Attention rate for native group is:',compute_mean(attentionPercentage_nat)
print 'Attention rate for nonnative group is:',compute_mean(attentionPercentage_nonnat)
print 'Roi attention rate for native group is:',compute_mean(roiPercentage_nat)
print 'Roi attention rate for nonnative group is:',compute_mean(roiPercentage_nonnat)

        