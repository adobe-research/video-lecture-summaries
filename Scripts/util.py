import numpy
from PIL import Image
import scipy as sp
import cv2
import re
import numpy as np
import os
import processframe as pf
import sys
import math

def write_ints(list_of_ints, filename="temp.txt"):
    textfile = open(filename, "w")
    for val in list_of_ints:
        textfile.write("%i\n" % int(val))
    textfile.close()

def get_images(framedir, fids):
    images = []
    filenames = []
    for fid in fids:
        filename = framedir + "/capture_"        
        filename = filename + ("%06i" % fid) + "_fid.png"
        img = cv2.imread(filename)
        if (img is None):
            print 'Warning %s not found' %filename
        images.append(img)
        filenames.append(filename)
        
    return images, filenames
        
def get_logos(dirname):
    logos = []
    if dirname is None or not os.path.exists(dirname):
        return logos
    
    filelist = os.listdir(dirname)
    for filename in filelist:
        if ('logo' in filename and 'png' in filename):
            logo = cv2.imread(dirname + "/" + filename)
            logos.append(logo)
    return logos

def resize_img(img, size):
    img = img.resize(size)
    return img

def get_capture_imgs(dirname):
    return get_imgs(dirname, "capture")

    
def get_imgs(dirname, name=None, ext=".png"):
    filelist= os.listdir(dirname)
    imagefiles = []
    images = []
    for filename in filelist:
        if name is None:
            if ext in filename:
                imagefiles.append(filename)
                images.append(cv2.imread(filename))
        elif name in filename and ext in filename:
            print 'here', dirname + "\\" + filename
            imagefiles.append(filename)
            img = cv2.imread(dirname + "\\" + filename)
            images.append(img)
    return imagefiles, images

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

def fg2gray(rgb, grayval):
    gray = grayimage(rgb)
    fg = np.where(gray < 250)
    gray[fg] = grayval
    rgb_copy = rgb.copy()
    rgb_copy[:,:,0] = gray
    rgb_copy[:,:,1] = gray
    rgb_copy[:,:,2] = gray
    return rgb_copy
    
def stringlist_from_txt(filepath):
    txtfile = open(filepath, "r")
    list_of_strings = []
    for val in txtfile.readlines():
        list_of_strings.append(val)
    txtfile.close()
    return list_of_strings

def list_of_vecs_from_txt(filepath, n=None):
    txtfile = open(filepath, "r")
    
    list_of_vecs = []
    for line in txtfile:
        values = line.split()
        if n is None:
            n = len(values)
        vec = []
        for i in range(0, n):
            vec.append(values[i])
        list_of_vecs.append(vec)
    txtfile.close()
    return list_of_vecs    

def strings2ints(stringlist):
    int_list = []
    for s in stringlist:
        int_list.append(int(s))
    return int_list

def min_dist_bbox(px, py, tlx, tly, brx, bry):
    dist = -1.0
    if (px < tlx):
        if (py < tly):
            dist = (px-tlx)*(px-tlx) + (py-tly)*(py-tly)
        elif (tly <= py and py <= bry):
            dist = (px-tlx)*(px-tlx)
        else:
            dist = (px-tlx)*(px-tlx) + (py-bry)*(py-bry)
    elif (tlx <= px and px <= brx):
        if (py < tly):
            dist = (py-tly)*(py-tly)
        elif (tly <= py and py <= bry):
            dist = 0.0
        else:
            dist = (py-bry)*(py-bry)
    else:
        if (py < tly):
            dist = (px-brx)*(px-brx) +(py-tly)*(py-tly)
        elif (tly <= py and py <= bry):
            dist = (px-brx)*(px-brx)
        else:
            dist = (px-brx)*(px-brx) + (py-bry)*(py-bry)
    
    return math.sqrt(dist)
        

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
    
def groupimages(list_of_imgobjs):
    minx = sys.maxint
    miny = sys.maxint
    maxx = -1
    maxy = -1
    for obj in list_of_imgobjs:
        minx = min(minx, obj.tlx)
        miny = min(miny, obj.tly)
        maxx = max(maxx, obj.brx)
        maxy = max(maxy, obj.bry)
    w = maxx - minx + 1
    h = maxy - miny + 1
    
    groupimg = np.ones((h, w, 3), dtype=np.uint8)*255
    for imgobj in list_of_imgobjs:
        resize_img = np.ones((h,w,3), dtype=np.uint8)*255
        tlx = imgobj.tlx - minx
        tly = imgobj.tly - miny
        objh, objw = imgobj.img.shape[:2]
        resize_img[tly:tly+objh, tlx:tlx+objw] = imgobj.img
        mask = pf.fgmask(resize_img, threshold=225, var_threshold=100)
        idx = mask != 0
        groupimg[idx] = resize_img[idx]
    return groupimg

def showimages(list_of_images, title="show images"):
    if list_of_images is None:
        return
    htotal = 0
    wtotal = 0
    hmax = 0
    wmax = 0
    for img in list_of_images:
        if img is None:
            continue
        h, w = img.shape[:2]
        htotal += h
        wtotal += (w + 10)
        hmax = max(hmax, h)
        wmax = max(wmax, w)
        
    view = sp.zeros((hmax, wtotal, 3), sp.uint8)
    curw = 0
    for img in list_of_images:
        if img is None:
            continue
        h,w = img.shape[:2]
        if (len(img.shape) == 2):
            view[:h,curw:curw+w, 0] = img
            view[:h,curw:curw+w,1] = img
            view[:h,curw:curw+w,2] = img
        else:
            view[:h,curw:curw+w, 0] = img[:,:,0]
            view[:h,curw:curw+w, 1] = img[:,:,1]
            view[:h,curw:curw+w, 2] = img[:,:,2]
        curw = curw+w+10
    if hmax == 0 or wtotal == 0:
        return
    cv2.namedWindow(title, cv2.WINDOW_AUTOSIZE)
    cv2.imshow(title, view)
    cv2.waitKey()
    
def saveimage(img, outdir, filename):
    if not os.path.exists(os.path.abspath(outdir)):
        os.makedirs(os.path.abspath(outdir))
#     if not os.path.isfile(os.path.abspath(outdir + "/" + filename)):
    cv2.imwrite(outdir + "/" + filename, img)
#     print 'util.saveimage', (outdir+"/" +filename)
    

def diff(data):
    diffdata = []
    for i in range(0, len(data)-1):
        diffdata.append(abs(data[i+1]-data[i]))
    return diffdata

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


def get_keyframe_ids_framediff(framediff_txt, thres=200):
    framediff = stringlist_from_txt(framediff_txt)
    framediff = strings2ints(framediff)    
    keyframe_ids = []

    print 'threshold', thres
    capturing = False
    fid = 0
    for diff in framediff:
            if diff < thres and not capturing:                
                    keyframe_ids.append(int(fid))
                    capturing = True
            elif diff > thres:
                capturing = False
            fid += 1
    return keyframe_ids    
