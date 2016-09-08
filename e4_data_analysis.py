from datetime import datetime,timedelta
from dateutil import tz
import pandas as pd

ref_time = datetime(1970,1,1,tzinfo=tz.tzutc())

def convert_time(time_in_second):
    t = ref_time + timedelta(seconds = time_in_second)
    t = t.astimezone(tz.tzlocal())
    str_t = t.strftime("%Y-%m-%d %H:%M:%S")
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
    df = import_data('physioData_Test_time_05.14.46.txt')
    print df.head(10)
    df.xs('E4_Bvp',level='Signal')['2016-08-29 17:14:49':'2016-08-29 17:14:50']
