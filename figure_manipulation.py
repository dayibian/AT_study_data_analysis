import matplotlib.pyplot as plt
import matplotlib.patches as pathches
import matplotlib.image as mpimg
import et_data_analysis as etda
try:
    import cPickle as pickle
except:
    import pickle

def plot_roi(figure_name):
    img = mpimg.imread(figure_name)
    fig = plt.figure()
    ax = fig.add_subplot(111,aspect='equal')
    head = pathches.Rectangle(etda.head[0],etda.head[1][0]-etda.head[0][0],
                            etda.head[1][1]-etda.head[0][1],edgecolor='r',
                            facecolor='none')
    nose = pathches.Rectangle(etda.nose[0],etda.nose[1][0]-etda.nose[0][0],
                            etda.nose[1][1]-etda.nose[0][1],edgecolor='r',
                            facecolor='none')
    mouth = pathches.Rectangle(etda.mouth[0],etda.mouth[1][0]-etda.mouth[0][0],
                            etda.mouth[1][1]-etda.mouth[0][1],edgecolor='r',
                            facecolor='none')
    ax.imshow(img)
    ax.add_patch(head); ax.add_patch(nose); ax.add_patch(mouth)
    plt.show()
    fig.savefig('native_roi.png',dpi = 200,bbox_inches='tight')
    
def plot_gazePos(figure_name,gazePos):
    gaze_xy = zip(*gazePos)
    gaze_x = gaze_xy[0]
    gaze_y = gaze_xy[1]
    img = mpimg.imread(figure_name)
    fig = plt.figure()
    plt.imshow(img)
    plt.scatter(gaze_x,gaze_y)
    plt.show()
    fig.savefig('gazePos.png',dpi=200,bbox_inches='tight')
    
    
if __name__ == '__main__':
    #plot_roi('native_stimulus.png')
    datafile = open('alldata.pkl','rb')
    alldata = pickle.load(datafile)
    etdata = alldata[0]['eyeGazeData']
    attention_per, gazePos = etda.compute_attention_percentage(etdata)
    gazePos_pixel = []
    for gaze in gazePos:
        if gaze[0]>0 and gaze[1]>0:
            gazePos_pixel.append((gaze[0]*1920, gaze[1]*1080))
    plot_gazePos('native_stimulus.png',gazePos_pixel)
