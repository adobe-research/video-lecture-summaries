#!/usr/bin/env python
import sys
import os
import cv2
import processframe as pf
from writehtml import WriteHtml

def get_objectmasks(keyframes):
    objlist = []
    objectmasks = []
    index = 0
    for keyframe in keyframes:
        print 'keyframe', index
        index += 1
        keyframe_mask = pf.fgmask(keyframe)
        obj, objmask = pf.getnewobj((keyframe, keyframe_mask), objlist)            
        newobj, newobjmask = pf.croptofg(obj, objmask)
        if (newobj == None):
            objectmasks.append(None)
            continue
        objectmasks.append(objmask)    
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

    objectmasks = get_objectmasks(keyframes)          
    
    highdir = "highlight"
    if not os.path.exists(dirname + "\\" + highdir):
        os.makedirs(dirname + "\\"+ highdir)
        
    fgdir = "foreground"
    if not os.path.exists(dirname + "\\" + fgdir):
        os.makedirs(dirname + "\\"+ fgdir)
        
    for i in range(0, len(keyframefiles)):
        if (objectmasks[i] != None):
            keyframe_mask = pf.fgmask(keyframes[i])
            fgimg = pf.alphaimage(keyframes[i], keyframe_mask)
            fgfile = "foreground_"+("%06i" %i)+".png"
            cv2.imwrite(dirname+"\\"+ fgdir + "\\" + fgfile, fgimg)
            
    fgfiles = []
    fgimages =  []
    filelist = os.listdir(dirname+"\\"+fgdir)
    for filename in filelist:
        if "foreground" in filename and ".png" in filename:
            fgimages.append(cv2.imread(dirname + "\\" + fgdir + "\\"+ filename))
            fgfiles.append(filename)    
                
    html = WriteHtml(dirname + "\\sequential_highlight.html", title = "sequential highlighting")    
    html.openbody()
    html.opentable(border=3)
    html.opentablerow()
    for i in range(0, len(fgfiles)):
        html.opentablecell()
        fgfile = "foreground_"+("%06i" %i)+".png"
        html.imagelink(fgdir + "\\" +fgfiles[i], 500)
        html.closetablecell()
    html.closetablerow()
    
    html.opentablerow()
    index = 0
    for i in range(0, len(keyframes)):
        if (objectmasks[i] != None):
            html.opentablecell()
            print fgfiles[index]
            highimg = pf.highlight(fgimages[index], objectmasks[i])
            index += 1
            highfile = "highlight_"+str(i)+".png"
            cv2.imwrite(dirname+"\\"+ highdir + "\\" + highfile, highimg)
            html.imagelink(highdir + "\\" +highfile, 500)
            html.closetablecell()
    html.closetablerow()
    
    html.closetable()
    html.closebody()
    html.closehtml()
    
    