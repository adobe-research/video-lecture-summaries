import numpy
from PIL import Image
import scipy as sp
import cv2
import re
import numpy as np
import os

def grayimage(img):
    if len(img.shape) <= 2:
        return img
    depth = img.shape[2]
    if (depth ==3):
        return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    elif (depth == 4):
        return cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY)
    else:
        print "Image format not recognized"
        return img


def stringlist_from_txt(filepath):
    txtfile = open(filepath, "r")
    list_of_strings = []
    for val in txtfile.readlines():
        list_of_strings.append(val)
    return list_of_strings

def list_of_vecs_from_txt(filepath, n=2):
    txtfile = open(filepath, "r")
    list_of_vecs = []
    for line in txtfile:
        values = line.split()
        vec = []
        for i in range(0, n):
            vec.append(values[i])
        list_of_vecs.append(vec)
    return list_of_vecs    

def strings2ints(stringlist):
    int_list = []
    for s in stringlist:
        int_list.append(int(s))
    return int_list

def array_to_pil(data, mode="RGB"):
    if (mode == "RGB"):
        image = Image.fromarray(data, "RGB")
        b, g, r = image.split()
        image = Image.merge("RGB", (r, g, b))
    elif (mode == "RGBA"):
        image = Image.fromarray(data, "RGBA")
        b, g, r, a = image.split()
        image = Image.merge("RGBA", (r, g, b,a))
    return image

def filename_comp(name1, name2):
    num1 = re.findall("\d+.\d+", name1)
    num1 = float(num1[0])
    num2 = re.findall("\d+.\d+", name2)
    num2 = float(num2[0])
    return int(num1 - num2)

def bbox_overlap(box1, box2):
    tlx = max(box1[0], box2[0])
    tly = max(box1[1], box2[1])
    brx = min(box1[2], box2[2])
    bry = min(box1[3], box2[3])
    
    return (tlx, tly, brx, bry)
     
def boxarea(box):
    if (box[0] > box[2] or box[1] > box[3]):
        return 0
    else:
        return (box[2] - box[0]) * (box[3] - box[1])

def showimages(list_of_images):
    htotal = 0
    wtotal = 0
    hmax = 0
    wmax = 0
    for img in list_of_images:
        h, w = img.shape[:2]
        htotal += h
        wtotal += w
        hmax = max(hmax, h)
        wmax = max(wmax, w)
        
    view = sp.zeros((hmax, wtotal, 3), sp.uint8)
    curw = 0
    for img in list_of_images:
        h,w = img.shape[:2]
        if (len(img.shape) == 2):
            view[:h,curw:curw+w, 0] = img
            view[:h,curw:curw+w,1] = img
            view[:h,curw:curw+w,2] = img
        else:
            view[:h,curw:curw+w, 0] = img[:,:,0]
            view[:h,curw:curw+w, 1] = img[:,:,1]
            view[:h,curw:curw+w, 2] = img[:,:,2]
        curw = curw+w
    cv2.namedWindow("show images", cv2.WINDOW_NORMAL)
    cv2.imshow("show images", view)
    cv2.waitKey()
    
def saveimage(img, outdir, filename):
    if not os.path.exists(os.path.abspath(outdir)):
        os.makedirs(os.path.abspath(outdir))
    cv2.imwrite(outdir + "/" + filename, img)


def smooth(x,window_len=11,window='hanning'):
    """smooth the data using a window with requested size.  
    This method is based on the convolution of a scaled window with the signal.
    The signal is prepared by introducing reflected copies of the signal (with the window size) in both ends so that transient parts are minimized in the begining and end part of the output signal.
    
    input:
        x: the input signal 
        window_len: the dimension of the smoothing window; should be an odd integer
        window: the type of window from 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'
            flat window will produce a moving average smoothing.

    output:
        the smoothed signal
        
    example:

    t=linspace(-2,2,0.1)
    x=sin(t)+randn(len(t))*0.1
    y=smooth(x)
    
    see also: 
    
    numpy.hanning, numpy.hamming, numpy.bartlett, numpy.blackman, numpy.convolve
    scipy.signal.lfilter
 
    TODO: the window parameter could be the window itself if an array instead of a string
    NOTE: length(output) != length(input), to correct this: return y[(window_len/2-1):-(window_len/2)] instead of just y.
    """

    if x.ndim != 1:
        raise ValueError, "smooth only accepts 1 dimension arrays."

    if x.size < window_len:
        raise ValueError, "Input vector needs to be bigger than window size."


    if window_len<3:
        return x


    if not window in ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']:
        raise ValueError, "Window is not one of 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'"


    s=numpy.r_[x[window_len-1:0:-1],x,x[-1:-window_len:-1]]
    #print(len(s))
    if window == 'flat': #moving average
        w=numpy.ones(window_len,'d')
    else:
        w=eval('numpy.'+window+'(window_len)')

    y=numpy.convolve(w/w.sum(),s,mode='valid')
    return y[(window_len/2-1):-(window_len/2)]


def get_keyframe_ts_framediff(framediff_txt, fps, thresh_scale=0.10):
    framediff = stringlist_from_txt(framediff_txt)
    framediff = strings2ints(framediff)
    
    keyframe_ms = []
    blur = smooth(np.array(framediff))
    sub_blur = blur[0:len(blur):int(fps)]
    avg = np.mean(sub_blur)
    thres = thresh_scale * avg
    capturing = False
    ms = 0
    for diff in sub_blur:
            if diff < thres and not capturing:                
                    keyframe_ms.append(int(ms))
                    capturing = True
            elif diff > thres:
                capturing = False
            ms += 1000
    return keyframe_ms    
