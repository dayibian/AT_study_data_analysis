#from datetime import datetime,timedelta
#from dateutil import tz
import time
import pandas as pd
import json

def convert_time(time_in_second):
    #t = ref_time + timedelta(microseconds = time_in_second*(10**6))
    #t = t.astimezone(tz.tzlocal())
    #str_t = t.strftime("%Y-%m-%d %H:%M:%f")
    t = time.localtime(time_in_second)
    str_t = time.strftime("%Y-%m-%d %H:%M:%S",t)
    return pd.to_datetime(str_t)
    
def import_physio_data(path):
    df = pd.read_csv(path, sep = ' ',  
                    names = ['Signal','TimeStamp','Value'], 
                    error_bad_lines = False)
    df.TimeStamp = pd.to_numeric(df.TimeStamp, errors = 'coerce')
    df.Value = pd.to_numeric(df.Value, errors = 'coerce')
    df = df.dropna(how = 'any')
    df.TimeStamp = df.TimeStamp.map(convert_time)
    df = df.set_index('TimeStamp')
    df = df.set_index('Signal',append=True)
    return df
    
def get_date(msg_fp2):
    with open(msg_fp2) as f:
        lines = f.readlines()
    s = ''
    for line in lines:
        if line.startswith('Participate date:'):
            s = line
            break
    d_str = s.split()[2]
    m,d,y = d_str.split('/')
    return '%s-%02d-%02d' % (y,int(m),int(d))
    
def generate_dt(date,t):
    # date format: '2016-08-09'
    # time format: '12:16:5:123'
    h,m,s,ms = t.split(':')
    return '%s %02d:%02d:%02d' % (date,int(h),int(m),int(s))
    
def compute_dt_index(msgs,date):
    # msgs: dictionary
    # date: date get from get_date function
    dt_index = []
    for msg in msgs[1:-1]:
        dt_index.append(generate_dt(date,msg['timeStamp']))
    return dt_index
    
    
if __name__ == '__main__':
    #df = import_data('test_data.txt')
    #print df.head(10)
    #df.xs('E4_Bvp',level='Signal')['2016-08-29 17:14:49':'2016-08-29 17:14:50']
    
    msg_fp = ('C:\\Users\\biand\\Documents\\Affective_touch\\'+
            'Affective_touch_data\\803\\jsonData-12-16.json')
    msg_fp2 = ('C:\\Users\\biand\\Documents\\Affective_touch\\'+
            'Affective_touch_data\\803\\txtData-12-16.txt')
    data_fp = ('C:\\Users\\biand\\Documents\\Affective_touch\\'+
            'Affective_touch_data\\803\\physioData_803_12.15.15.txt')
    
    df=import_physio_data(data_fp)
    msgs = json.load(msg_fp)
    date = get_date(msg_fp2)
    dt_index = compute_dt_index(msgs,date)
    physioData_list = []
    for i in range(6):
        physioData = {}
        bvpData = (df.xs('E4_Bvp',level='Signal')
                        [dt_index[2*i]:dt_index[2*i+1]])
        gsrData = (df.xs('E4_Gsr',level='Signal')
                        [dt_index[2*i]:dt_index[2*i+1]])
        ibiData = (df.xs('E4_Ibi',level='Signal')
                        [dt_index[2*i]:dt_index[2*i+1]])
        physioData['bvpData'] = bvpData
        physioData['gsrData'] = gsrData
        physioData['ibiData'] = ibiData
        physioData_list.append(physioData)
    