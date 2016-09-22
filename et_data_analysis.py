try:
    import cPickle as pickle
except:
    import pickle
    
head = ((750,400),(1250,560))
nose = ((920,560),(1070,700))
mouth = ((850,720),(1130,880))

def compute_attention_percentage(etdata):
    sample_num = len(etdata)
    x = []
    y = []
    for i in range(sample_num):
        sample = etdata.iloc[i]
        if sample.GazeX*sample.GazeY != 0:
            x.append(sample.GazeX)
            y.append(sample.GazeY)
    gazePositions = zip(x,y)
    try:
        attention_percentage = len(gazePositions)/float(sample_num)
    except ZeroDivisionError:
        attention_percentage = 'NA'
    return attention_percentage, gazePositions
    
def check_hit(gazePosition):
    gazePosition_pixel = (gazePosition[0]*1920, gazePosition[1]*1080)
    hit = False
    for roi in [head, nose, mouth]:
        if (roi[0][0]<gazePosition_pixel[0]<roi[1][0] and 
                roi[0][1]<gazePosition_pixel[1]<roi[1][1]):
            hit = True
            break
    return hit

def compute_roi_percentage(gazePositions):
    sample_num = len(gazePositions)
    hit_num = 0
    for gazePosition in gazePositions:
        if check_hit(gazePosition):
            hit_num += 1
    try:
        hit_percentage = hit_num/float(sample_num)
    except ZeroDivisionError:
        hit_percentage = 'NA'
    return hit_percentage

if __name__ == '__main__':
    etfile = open('alldata.pkl','rb')
    alldata = pickle.load(etfile)
    for data in alldata:
        etdata = data['eyeGazeData']
        attention_per, gazePos = compute_attention_percentage(etdata)
        print attention_per
        #print gazePos