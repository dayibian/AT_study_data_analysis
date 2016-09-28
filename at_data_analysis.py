try:
    import cPickle as pickle
except:
    import pickle
import e4_data_analysis as e4da
import et_data_analysis as etda

participantID_list = ['801','803','804','805','806','807']
for participantID in participantID_list:
    print '='*40
    datafile_name = 'alldata_' + participantID + '.pkl'   
    datafile = open(datafile_name,'rb')
    alldata = pickle.load(datafile)
    feature_list = []
    
    print 'Extracting features for participant: ' + participantID + '...\n'
    for data in alldata:
        feature = {}
        hrData = data['physioData']['hrData']
        ibiData = data['physioData']['ibiData']
        etData = data['eyeGazeData']
        gsrData = data['physioData']['gsrData']
        gsr_l = e4da.convert2list(gsrData)
        scr,scl = e4da.decompose_signal(gsr_l)
        scl_mean, scl_sd = e4da.compute_scl_fv(scl)
        scr_rate, scr_mean, scr_sd, scr_max = e4da.compute_scr_fv(scr)
        hr = e4da.compute_heart_rate(hrData)
        ibi = e4da.compute_ibi(ibiData)
        attention_percentage, gazePositions = etda.compute_attention_percentage(
                                                                        etData)
        roiPercentage = etda.compute_roi_percentage(gazePositions)
        feature['heartRate'] = hr
        feature['ibi'] = ibi
        feature['scl_mean'] = scl_mean
        feature['scl_sd'] = scl_sd
        feature['scr_rate'] = scr_rate
        feature['scr_mean'] = scr_mean
        feature['scr_sd'] = scr_sd
        feature['scr_max'] = scr_max
        feature['attentionPercentage'] = attention_percentage
        feature['roiPercentage'] = roiPercentage
        feature['stimulusName'] = data['stimulusName']
        feature['brushEnabled'] = data['brushEnabled']
        feature_list.append(feature)
    
    print 'Saving the features in pickle file...\n'
    featurefile_name = 'features_' + participantID + '.pkl'
    datafile = open(featurefile_name,'wb')
    pickle.dump(feature_list, datafile)
    datafile.close()
    print 'Done!\n'