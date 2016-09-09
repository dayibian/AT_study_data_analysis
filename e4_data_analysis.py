#from datetime import datetime,timedelta
#from dateutil import tz
import time
import pandas as pd

#ref_time = datetime(1970,1,1,tzinfo=tz.tzutc())

def convert_time(time_in_second):
    #t = ref_time + timedelta(microseconds = time_in_second*(10**6))
    #t = t.astimezone(tz.tzlocal())
    #str_t = t.strftime("%Y-%m-%d %H:%M:%f")
    t = time.localtime(time_in_second)
    str_t = time.strftime("%Y-%m-%d %H:%M:%S",t)
    return pd.to_datetime(str_t)
    
def import_data(path):
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
    
if __name__ == '__main__':
    df = import_data('test_data.txt')
    print df.head(10)
    #df.xs('E4_Bvp',level='Signal')['2016-08-29 17:14:49':'2016-08-29 17:14:50']
