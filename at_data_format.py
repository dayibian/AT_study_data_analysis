try:
    import cPickle as pickle
except:
    import pickle
    
import e4_data_format as e4df
import eye_tracker_data_format as etdf
import json
import os

base_fp = 'C:\\Users\\biand\\Documents\\Affective_touch\\Affective_touch_data\\'
participantID_list = ['801','803','804','805','806','807']

for participantID in participantID_list:
    print '='*40
    data_fp = base_fp + participantID
    files = [f for f in os.listdir(data_fp) 
                    if os.path.isfile(os.path.join(data_fp,f))]
                    
    for f in files:
        if f.startswith('RawData'):
            etData_fp = data_fp+'\\'+f
        elif f.startswith('jsonData'):
            jsonMsg_fp = data_fp+'\\'+f
        elif f.startswith('txtData'):
            txtMsg_fp = data_fp+'\\'+f
        elif f.startswith('physioData'):
            physioData_fp = data_fp+'\\'+f
        else:
            print 'Contains unrecognized file: ' + f
    print 'Got all the file names!\n'
            
    #etData_fp = ('C:\\Users\\biand\\Documents\\Affective_touch\\'+
    #            'Affective_touch_data\\803\\RawData_09-08-2016_12-11-20-2408.dat')
    #jsonMsg_fp = ('C:\\Users\\biand\\Documents\\Affective_touch\\'+
    #            'Affective_touch_data\\803\\jsonData-12-16.json')
    #txtMsg_fp = ('C:\\Users\\biand\\Documents\\Affective_touch\\'+
    #            'Affective_touch_data\\803\\txtData-12-16.txt')
    #physioData_fp = ('C:\\Users\\biand\\Documents\\Affective_touch\\'+
    #            'Affective_touch_data\\803\\physioData_803_12.15.15.txt')
    
    print 'Processing eye tracking data...\n'            
    rec_time, et_df = etdf.import_eye_tracker_data(etData_fp)
    msgs = json.load(open(jsonMsg_fp))
    gaze_data_index = etdf.compute_index(rec_time, msgs)
    
    etdf_list = []
    for i in range(6):
        etdf_list.append(et_df.iloc[gaze_data_index[i*2+1]:gaze_data_index[i*2+2]])
    
    print 'Processing physiological data...\n'
    e4_df=e4df.import_physio_data(physioData_fp)
    date = e4df.get_date(txtMsg_fp)
    dt_index = e4df.compute_dt_index(msgs,date)
    physioData_list = []
    for i in range(6):
        physioData = {}
        try:
            bvpData = (e4_df.xs('E4_Bvp',level='Signal')
                            [dt_index[2*i]:dt_index[2*i+1]])
        except:
            bvpData = []
        gsrData = (e4_df.xs('E4_Gsr',level='Signal')
                        [dt_index[2*i]:dt_index[2*i+1]])
        ibiData = (e4_df.xs('E4_Ibi',level='Signal')
                        [dt_index[2*i]:dt_index[2*i+1]])
        hrData = (e4_df.xs('E4_Hr',level='Signal')
                        [dt_index[2*i]:dt_index[2*i+1]]) 
        physioData['bvpData'] = bvpData
        physioData['gsrData'] = gsrData
        physioData['ibiData'] = ibiData
        physioData['hrData'] = hrData
        physioData_list.append(physioData)
    
    print 'Combining all the data into one file...\n'
    data_list = []
    for i in range(6):
        structured_data = {}
        structured_data['stimulusName'] = msgs[2*i+1]['stimulusName']
        structured_data['brushEnabled'] = msgs[2*i+1]['brushEnabled']
        structured_data['eyeGazeData'] = etdf_list[i]
        structured_data['physioData'] = physioData_list[i]
        data_list.append(structured_data)
    
    print 'Writing to a pickle file...\n'
    datafile_name = 'alldata_'+participantID+'.pkl'
    F = open(datafile_name,'wb')
    pickle.dump(data_list, F)
    F.close()
    print 'Data of participant ' + participantID + ' formating done!\n'