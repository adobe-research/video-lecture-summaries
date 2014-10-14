#!/usr/bin/env python
import re
import processframe as pf
import cv2
import sys
import os
import scipy as sp
from writehtml import WriteHtml
import numpy as np

def getframenumber(filename):
    """filename must be xxx_####.ext"""
    tregex = "[0-9]+"
    framenumber = re.findall(tregex, filename)
    fn = int(framenumber[0])
    return fn

def compareframes_align(frame1, frame2, M):
    """Align two frames with SIFT features and then compare"""
    if (M == None):
        diff = cv2.absdiff(255-frame1, 255-frame2)
        return diff
    rows, cols = frame2.shape[0:2]
    frame2_align = cv2.warpPerspective(255-frame2, M, (cols,rows))
    diff = cv2.absdiff(255-frame1, frame2_align)
    return diff
    
def getclosestframes_time(list_of_frames, frame):
    fn = getframenumber(frame)
    
    for i in xrange(0, len(list_of_frames)-1):
        cframe1 = list_of_frames[i]
        cframe2 = list_of_frames[i+1]
        
        t1 = getframenumber(cframe1)
        t2 = getframenumber(cframe2)
      
        if (t1 == fn):
            return [cframe1]
        if (t1 < fn):
            if (fn < t2):
                return [cframe1, cframe2]
            elif(fn == t2):
                return [cframe2]
        elif (fn < t1 and i == 0):
            return [cframe1]
    return [list_of_frames[len(list_of_frames)-1]]

def getclosestframe(list_of_frames, frame):
    minscore = float("inf")
    for i in xrange(0, len(list_of_frames)):
        cframe = list_of_frames[i]
        M = pf.find_object_appx_thres(frame, cframe)
        diff = compareframes_align(frame, cframe, M)
        score = np.sum(diff)
        if (score < minscore):
            closest_frame = cframe
            minscore = score            
            closest_diff = diff
            index = i
    return closest_frame, closest_diff, minscore, index
    
if __name__ == "__main__":
    """Compare two keyframe selections and produce a score
    Takes in as argument
    dir for ground-truth keyframes,
    dir for testing keyframes,
    dir to save difference.
    Prints html file that show the score and matching frames"""
    
    videolist = ["armando1", "armando2",
                 "hwt1", "hwt2",
                 "khan1", "khan2",
                 "mit1", "mit2",
                 "mit3",
                 "tecmath1", "tecmath2",
                 "udacity1", "udacity2",
                 "pentimento1",
                 "slide1"]
    
    comparename = sys.argv[1]
    
    html = WriteHtml(comparename + "_keyframe_scoring.html")    
    html.openbody()
    
    test = ['recall', 'precision']
    allscores = []
        
    for video in videolist:
        print video
        videoname = video
        
        diff_dirpath = "..\\SampleVideos\\more\\" + videoname + "\\" + videoname + "_keyframe_diffs"
        if not os.path.exists(diff_dirpath):
                os.makedirs(diff_dirpath)
        scores = []    
        for testing in test:
            if ('precision' in testing):
                alg_dirpath = "..\\SampleVideos\\more\\"+ videoname + "\\" + videoname + "_manual_keyframes"
                groundtruth_dirpath = "..\\SampleVideos\\more\\" + videoname + "\\" + videoname + "_" + comparename
                html.opentable()
                html.opentablerow()
                html.opentablecell()
                html.writestring('Selected Frame')
                html.closetablecell()
                html.opentablecell()
                html.writestring('Closest Ground Truth Frame')
                html.closetablecell()
                html.opentablecell()
                html.writestring('Frame Difference')
                html.closetablecell()

                html.opentablecell()
                html.writestring('Score')    
                html.closetablecell()
                html.closetablerow()
                
                
            elif('recall' in testing):                
                alg_dirpath = "..\\SampleVideos\\more\\" + videoname + "\\" + videoname + "_" + comparename
                groundtruth_dirpath = "..\\SampleVideos\\more\\"+ videoname + "\\" + videoname + "_manual_keyframes"
                html.opentable()
                html.opentablerow()
                html.opentablecell()
                html.writestring('Ground Truth Frame')
                html.closetablecell()
                html.opentablecell()
                html.writestring('Closest Selected Frame')
                html.closetablecell()
                html.opentablecell()
                html.writestring('Frame Difference')
                html.closetablecell()

                html.opentablecell()
                html.writestring('Score')    
                html.closetablecell()
                html.closetablerow()
        
        
            alg_filelist = os.listdir(alg_dirpath)
            alg_imagefiles = []
            alg_images = []
            for filename in alg_filelist:   
                if "capture" in filename:
                    alg_imagefiles.append(str(filename))
                    alg_images.append(cv2.imread(alg_dirpath+"\\"+filename, 0))
                    
            groundtruth_filelist = os.listdir(groundtruth_dirpath)
            groundtruth_imagefiles = []
            for filename in groundtruth_filelist:
                if "capture" in filename:
                    groundtruth_imagefiles.append(str(filename))
                    
            framediff_score = 0.0                      
            
            
            for groundtruth_frame in groundtruth_imagefiles:
                print groundtruth_frame
                html.opentablerow()
                
                gray_tframe = cv2.imread(groundtruth_dirpath+"\\"+groundtruth_frame, 0)
                
                h,w = gray_tframe.shape
                normalize = h*w*255.0
                closestframes = getclosestframes_time(alg_imagefiles, groundtruth_frame)
                minscore = float("inf")
                for closeframe in closestframes:                 
                    gray_cframe = cv2.imread(alg_dirpath+"\\"+closeframe, 0)
                    M = pf.find_object_appx_thres(gray_tframe, gray_cframe)
                    diff = compareframes_align(gray_tframe, gray_cframe, M)
                    if (np.sum(diff) < minscore):
                        closestdiff = diff
                        closest_frame = closeframe
                        minscore = np.sum(diff)
                

                
                diffname = "diff_"+("%06i" % getframenumber(groundtruth_frame))+"_"+("%06i" % getframenumber(closest_frame)) + ".jpg"
                cv2.imwrite(diff_dirpath + "\\" + diffname, closestdiff)         
                html.opentablecell()
                html.imagelink(groundtruth_dirpath+"\\"+groundtruth_frame, 200)
                html.closetablecell()
                html.opentablecell()
                html.imagelink(alg_dirpath+"\\"+closest_frame, 200)
                html.closetablecell()
                html.opentablecell()
                html.imagelink(diff_dirpath+"\\"+diffname, 200)
                html.closetablecell()
                html.opentablecell()
                html.writestring(minscore *1.0/normalize)
                html.closetablecell()
     
                framediff_score += float(minscore / normalize)        
                html.closetablerow()
            html.closetable()
            average_score = float(framediff_score)/len(groundtruth_imagefiles)
            scores.append(average_score)
            allscores.append(average_score)
            
        
        for i in range(0, len(scores)):
            html.writestring("<h3>Average Frame Difference ("+test[i]+"): %f</h3>" % (scores[i]))                      
        
    tot_score = np.sum(np.array(allscores))
    html.writestring("<h1>Total Score: %f</h1>" % tot_score)
    html.closebody()
    html.closehtml()           