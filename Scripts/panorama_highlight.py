#!/usr/bin/env python
import cv2
import sys
import processframe as pf
import os

if __name__ == "__main__":
    
    panorama_file = sys.argv[1]
    panorama = cv2.imread(panorama_file)
    
    keyframe_dir = sys.argv[2]
    filelist = os.listdir(keyframe_dir)
    keyframes = []
    for filename in filelist:
        if "capture" in filename and ".png" in filename:
            keyframes.append(cv2.imread(keyframe_dir + "\\" + filename))
       
    # identify new objects in each keyframe
    objectmasks = pf.get_objectmasks(keyframes)
    
    panorama_highlight = "panorama_highlight"
    if not os.path.exists(keyframe_dir + "\\" + panorama_highlight):
        os.makedirs(keyframe_dir + "\\"+ panorama_highlight)        

    
    # find frame in panorama
    ph, pw = panorama.shape[0:2]
    masks = []
    for i in range(0, len(keyframes)):
        keyframe = keyframes[i]
        objmask = objectmasks[i]
        if (objmask == None):
            continue
        
        M = pf.find_object_appx(panorama, keyframe)
        if (M == None):
            continue
        
        if not pf.isgoodmatch(M):
            continue
        
        # warp object mask to panorama
        warp_mask = cv2.warpPerspective(objmask, M, (pw, ph))
        #cv2.imshow("warp_mask before", warp_mask)
        for prevmask in masks:
            #negate prevmask: only parts previously not highlighted are eligible
            #cv2.imshow("prevmask", prevmask)
            negmask = cv2.bitwise_not(prevmask)            
            #cv2.imshow("negamsk", negmask)
            warp_mask = cv2.bitwise_and(negmask, warp_mask)
            #cv2.imshow("warp mask", warp_mask)
            #cv2.waitKey(0)
        masks.append(pf.expandmask(warp_mask))
        highlight = pf.highlight(panorama, warp_mask)
        #cv2.imshow("highlight", highlight)
        #cv2.waitKey(0)
        cv2.imwrite(keyframe_dir + "\\" + panorama_highlight + "\\panorama_highlight" + ("%06i" % i) + ".png", highlight)
        
        
    