try:
    import cPickle as pickle
except:
    import pickle
    
import e4_data_format as e4df
import eye_tracker_data_format as etdf
import json

etData_fp = ('C:\\Users\\biand\\Documents\\Affective_touch\\'+
            'Affective_touch_data\\803\\RawData_09-08-2016_12-11-20-2408.dat')
jsonMsg_fp = ('C:\\Users\\biand\\Documents\\Affective_touch\\'+
            'Affective_touch_data\\803\\jsonData-12-16.json')
txtMsg_fp = ('C:\\Users\\biand\\Documents\\Affective_touch\\'+
            'Affective_touch_data\\803\\txtData-12-16.txt')
physioData_fp = ('C:\\Users\\biand\\Documents\\Affective_touch\\'+
            'Affective_touch_data\\803\\physioData_803_12.15.15.txt')
            
rec_time, et_df = etdf.import_eye_tracker_data(etData_fp)
msgs = json.load(open(jsonMsg_fp))
gaze_data_index = etdf.compute_index(rec_time, msgs)

etdf_list = []
for i in range(6):
    etdf_list.append(et_df.iloc[gaze_data_index[i*2+1]:gaze_data_index[i*2+2]])

e4_df=e4df.import_physio_data(physioData_fp)
date = e4df.get_date(txtMsg_fp)
dt_index = e4df.compute_dt_index(msgs,date)
physioData_list = []
for i in range(6):
    physioData = {}
    bvpData = (e4_df.xs('E4_Bvp',level='Signal')
                    [dt_index[2*i]:dt_index[2*i+1]])
    gsrData = (e4_df.xs('E4_Gsr',level='Signal')
                    [dt_index[2*i]:dt_index[2*i+1]])
    ibiData = (e4_df.xs('E4_Ibi',level='Signal')
                    [dt_index[2*i]:dt_index[2*i+1]])
    physioData['bvpData'] = bvpData
    physioData['gsrData'] = gsrData
    physioData['ibiData'] = ibiData
    physioData_list.append(physioData)

data_list = []
for i in range(6):
    structured_data = {}
    structured_data['stimulusName'] = msgs[2*i+1]['stimulusName']
    structured_data['brushEnabled'] = msgs[2*i+1]['brushEnabled']
    structured_data['eyeGazeData'] = etdf_list[i]
    structured_data['physioData'] = physioData_list[i]
    data_list.append(structured_data)
    
F = open('alldata.pkl','wb')
pickle.dump(data_list, F)
F.close()