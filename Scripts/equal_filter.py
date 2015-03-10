'''
Created on Mar 8, 2015

@author: hijungshin
'''

import sys
import util
from visualobjects import VisualObject
import  cv2
import lecturevisual
import numpy as np
import os
from scipy import ndimage


def filter1():
    chardir = sys.argv[1]
    equaltxt = chardir + "/equal.txt"
    panorama = cv2.imread(sys.argv[2])
    
    list_of_charobjs = VisualObject.objs_from_file(None, chardir)
    equals = util.stringlist_from_txt(equaltxt)
    equals = util.strings2ints(equals)
    is_equals = []
    for i in range(0, len(list_of_charobjs)):
        charobj = list_of_charobjs[i]
        if (equals[i] == 0):
            is_equals.append(0)
            i += 1
            continue
        """Check width/height ratio"""
        w = float(charobj.getwidth())
        h = float(charobj.getheight())
        print 'h/w', h/w
        if (h/w> 2.5 or h/w < 0.3):
            is_equals.append(0)
            i += 1
            continue
        
        maxoverlap = 0.0
        for other in list_of_charobjs:
            if other == charobj:
                overlap = 0.0
            else:
                overlap = VisualObject.overlap(other, charobj)
            maxoverlap = max(maxoverlap, overlap)
        
        if (maxoverlap > 0.0):
            is_equals.append(0)
        else:
            is_equals.append(1)
            cv2.rectangle(panorama, (charobj.tlx, charobj.tly), (charobj.brx, charobj.bry), (0,0,255), 2)
    num_equals = np.count_nonzero(np.array(is_equals))
    print 'num equals:', num_equals
    util.showimages([panorama], "result")
    util.write_ints(is_equals, chardir + "/equal1.txt")
    util.saveimage(panorama, chardir, "equal_symbols_1.png")
    
def filter2():
    videopath = sys.argv[1]
    panoramapath = sys.argv[2]
    objdir = sys.argv[3]
    scriptpath = sys.argv[4]
    chardir = objdir + "/xcut"
    equaltxt = chardir + "/equal1.txt"
    equals = util.stringlist_from_txt(equaltxt)
    equals = util.strings2ints(equals)
    
    visuals = lecturevisual.getvisuals(videopath, panoramapath, objdir, scriptpath)
    list_of_chars = visuals[5]
    is_equals = []
    panorama = visuals[0]
    avgw = 0.0
    avgh = 0.0
    count = 0.0
    for i in range(0, len(list_of_chars)):
        if equals[i] == 1:
            avgw += list_of_chars[i].obj.getwidth()
            avgh += list_of_chars[i].obj.getheight()
            count += 1.0
    avgw /= count
    avgh /= count
    
    for i in range(0, len(list_of_chars)):
        if equals[i] == 0:
            is_equals.append(0)
            i += 1
            continue
        
        char = list_of_chars[i] 
        symbolpath = chardir + "/symbols_fill/" + os.path.basename(char.obj.imgpath)
        symbol = cv2.imread(symbolpath, 0)
        label_im, num_labels = ndimage.label(symbol)
#         util.showimages([symbol], "%i"%num_labels)
        if (char.obj.getwidth() > 2* avgw or char.obj.getheight() > 2 * avgh
            or char.obj.getwidth() <= 2 or char.obj.getheight() <= 2):
            is_equals.append(0)
            i += 1
            continue

        if (num_labels < 2 or num_labels >3):
            is_equals.append(0)
            i += 1
            continue
       
        linegroup = char.stroke.stcgroup.subline.linegroup
        chars_in_same_line = []
        for subline in linegroup.list_of_sublines:
            for stroke in subline.list_of_strokes:
                chars_in_same_line += stroke.list_of_chars
        
        close = False
        for otherchar in chars_in_same_line:
            if (otherchar == char):
                continue
            else:
                xdist = VisualObject.signed_xgap_distance(char.obj, otherchar.obj)
                ydist = VisualObject.signed_ygap_distance(char.obj, otherchar.obj)
                if (xdist <6 and ydist < 10):
                    is_equals.append(0)
                    close = True
                    break
        if close:
            is_equals.append(0)
            i += 1
            continue
        else:
            is_equals.append(1)
            cv2.rectangle(panorama, (char.obj.tlx, char.obj.tly), (char.obj.brx, char.obj.bry), (0,0,255), 2)

    num_equals = np.count_nonzero(np.array(is_equals))
    print 'num equals:', num_equals
#     util.showimages([panorama], "result")
    util.write_ints(is_equals, chardir + "/equal2.txt")
    util.saveimage(panorama, chardir, "equal_symbols_2.png")
    
    
if __name__ == "__main__":
    filter2()
    
    
        
                