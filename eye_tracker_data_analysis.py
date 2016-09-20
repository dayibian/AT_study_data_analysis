import pandas as pd
import json

def import_eye_tracker_data(fp):
    with open(fp) as f:
        lines = f.readlines()
    rec_time = lines[13].split('  ')[1]
    df = pd.DataFrame(data=[l.split() for l in lines[18:]],
                        columns=lines[17].split())
    df_num = df.apply(lambda x: pd.to_numeric(x,errors='ignore'))
    return rec_time, df_num

def import_msgs(fp):
    msgs = json.load(open(fp))
    return msgs
    
def compute_index(rec_time, msgs):
    gaze_data_index = [0]
    for msg in msgs[1:-1]:
        gaze_data_index.append(compute_secs_offset(rec_time,msg['timeStamp']))
    gaze_data_index = [int(i*120) for i in gaze_data_index]
    return gaze_data_index
    
def compute_secs_offset(rec_time, msg_time):
    # rec_time format: 12-13-40-2258
    # msg_time format: 12:23:1:930
    rec_time_l = [int(i) for i in rec_time.split('-')]
    msg_time_l = [int(i) for i in msg_time.split(':')]
    secs_offset = ((msg_time_l[0]-rec_time_l[0])*60*60+
                   (msg_time_l[1]-rec_time_l[1])*60+
                   (msg_time_l[2]-rec_time_l[2])+
                   (msg_time_l[3]/1000.0-rec_time_l[3]/10000.0))
    return secs_offset
    
if __name__ == '__main__':
    data_fp = ('C:\\Users\\biand\\Documents\\Affective_touch\\'+
            'Affective_touch_data\\803\\RawData_09-08-2016_12-11-20-2408.dat')
    msg_fp = ('C:\\Users\\biand\\Documents\\Affective_touch\\'+
            'Affective_touch_data\\803\\jsonData-12-16.json')
    rec_time, df = import_eye_tracker_data(data_fp)
    msgs = import_msgs(msg_fp)
    gaze_data_index = compute_index(rec_time, msgs)
    print(gaze_data_index)
    df_list = []
    for i in range(6):
        df_list.append(df.iloc[gaze_data_index[i*2+1]:gaze_data_index[i*2+2]])
    print(df_list)
    
    data_list = []
    for i in range(6):
        structured_data = {}
        structured_data['stimulusName'] = msgs[2*i+1]['stimulusName']
        structured_data['brushEnabled'] = msgs[2*i+1]['brushEnabled']
        structured_data['eyeGazeData'] = df_list[i]
        data_list.append(structured_data)