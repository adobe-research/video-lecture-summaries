#!/usr/bin/env python
import numpy as np
import cv2
import sys
import processframe as pf
from matplotlib import pyplot as plt
import os
import util
from PIL import Image
from writehtml import WriteHtml


def get_objectmasks(keyframes):
    objlist = []
    objectmasks = []
    for keyframe in keyframes:        
        keyframe_mask = pf.fgmask(keyframe)
        obj, objmask = pf.getnewobj((keyframe, keyframe_mask), objlist)
        objectmasks.append(objmask)        
        newobj, newobjmask = pf.croptofg(obj, objmask)
        if (newobj == None):
            continue
        objlist.append((newobj, newobjmask))
    return objectmasks

if __name__ == "__main__":
    
    dirname = sys.argv[1]
    filelist = os.listdir(dirname)
    keyframes = []
    keyframefiles = []
    for filename in filelist:
        if "capture" in filename and ".png" in filename:
            keyframes.append(cv2.imread(dirname + "\\" + filename))
            keyframefiles.append(filename)

    objlist = []        
    index = 0
    if (os.path.exists(dirname + "\\objects")):
        os.makedirs(dirname + "\\objects")
    
    for keyframe in keyframes:
        print 'keyframe', index
        keyframe_mask = pf.fgmask(keyframe)
        newobj, newobjmask = pf.getnewobj((keyframe, keyframe_mask), objlist)
        newobj, newobjmask = pf.croptofg(newobj, newobjmask)
        if (newobj == None):
            print 'no new object'
            index+=1
            continue
        objlist.append((newobj, newobjmask))
        objimage = Image.fromarray(newobj, "RGB")
        b, g, r = objimage.split()
        objimage = Image.merge("RGB", (r, g, b))
        maskimage = Image.fromarray(newobjmask).convert('L')
        objimage.putalpha(maskimage)
        objimage.save(dirname + "\\objects\\object" + str(index)+".png")
        index+=1
        
    html = WriteHtml(dirname + "\\objects.html")    
    html.opentable()
    
    for i in range(0, len(keyframefiles)):
        html.opentablerow()
        html.opentablecell()
        html.imagelink("objects\\"+keyframefiles[i], 500)
        html.closetablecell()
        
        objfile = "object" + str(i) + ".png"
        html.opentablecell()
        if (os.path.exists(dirname + "\\objects\\"+ objfile)):                       
            html.imagelink("objects\\"+objfile, 500)            
        else:
            html.writestring("no new object")
        html.closetablecell()
        html.closetablerow()

    
    html.closetable()
    html.closehtml()
        
        
    