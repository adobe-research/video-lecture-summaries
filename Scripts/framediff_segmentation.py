#!/usr/bin/env python
import processvideo 
import os
import ntpath
import util
import numpy as np
import matplotlib.pyplot as plt
import sys
from scipy.signal import argrelextrema
from lecture import Lecture, LectureSegment
from writehtml import WriteHtml
import processframe as pframe

    #videolist = ["..\\SampleVideos\\more\\armando1\\armando1.mp4", "..\\SampleVideos\\more\\armando2\\armando2.mp4"]
                 #"..\\SampleVideos\\more\\hwt1\\hwt1.mp4" , "..\\SampleVideos\\more\\hwt2\\hwt2.mp4"]
                 #"..\\SampleVideos\\more\\khan1\\khan1.mp4", "..\\SampleVideos\\more\khan2\\khan2.mp4",
                 #"..\\SampleVideos\\more\\mit1\\mit1.mp4", "..\\SampleVideos\\more\\mit2\\mit2.mp4",
                 #"..\\SampleVideos\\more\\mit3\\mit3.mp4",
                 #"..\\SampleVideos\\more\\tecmath1\\tecmath1.mp4", "..\\SampleVideos\\more\\tecmath2\\tecmath2.mp4",
                 #"..\\SampleVideos\\more\\udacity1\\udacity1.mp4", "..\\SampleVideos\\more\\udacity2\\udacity2.mp4",
                 #"..\\SampleVideos\\more\\pentimento1\\pentimento1.mp4",
                 #"..\\SampleVideos\\more\\slide1\\slide1.mp4"]
    
def test_init():
    videolist = ["..\\SampleVideos\\more\\khan1\\khan1.mp4"]    
    min_width = 5 #seconds
    for video in videolist:
               
        pv = processvideo.ProcessVideo(video)
       
        # Count frame difference
        print "Read framediff.txt"
        framedifftxt = pv.videoname+"_framediff.txt"
        framedifffile = open(framedifftxt, "r")
        counts = []
        for val in framedifffile.readlines():
            counts.append(int(val))
        
        # Smooth and subsample 1 frame per second
        print "Smooth and subsmaple 1 frame per second"
        smoothsample = util.smooth(np.array(counts))
        subsample = smoothsample[0:len(smoothsample):int(pv.framerate)]
        t = np.linspace(0, len(subsample)-1, len(subsample))        
        plt.plot(t, subsample, "bo-")
        plt.xlabel("time(sec)")       
        plt.ylabel("Frame Difference")
        plt.xlim(0, len(subsample))
        
        
        average = np.mean(subsample)
        thres = 0.10* average
        
        fn_filename = pv.videoname +"_framediff_absmin_keyframes.txt"
        keyframe = open(fn_filename, "w")
        frame = []
        fnumbers = []
        sec = 0
        capturing = False
        for diff in subsample:
            if diff < thres:
                if not capturing:                    
                    frame.append(int(sec))                    
                    plt.axvline(sec, color="g")
                    fnumbers.append(sec*pv.framerate)
                    keyframe.write("%i\n" % (sec*pv.framerate))
                    capturing = True
            elif diff > thres:
                capturing = False
            sec += 1
        plt.axhline(thres, color="r")
        plt.savefig(pv.videoname + "_framediff_absmin.jpg")
        plt.close()
        keyframe.close()
    
        #Capture Key Frames
        fnumbers = []
        frametxt = open(fn_filename, "r")
        for val in frametxt.readlines():
            fnumbers.append(int(val))
        array = np.array(fnumbers)
        frametxt.close()
        
        print fnumbers
        print "Capture Key Frames"
        capturedir = "_framediff_absmin_keyframes"
        if not os.path.exists(pv.videoname + capturedir):
            os.makedirs(pv.videoname + capturedir)
        pv.captureframes(fnumbers, pv.videoname + capturedir + "\\")
        
def get_keyframe_times(lecture, framediffs):
    smooth = util.smooth(np.array(framediffs))
    sub_smooth = smooth[0:len(smooth):int(lecture.video.fps)]
    avg = np.mean(sub_smooth)
    thres = 0.10 * avg
    keyframes_ms  = []
    capturing = False
    ms = 0
    for diff in sub_smooth:
            if diff < thres and not capturing:                
                    keyframes_ms.append(int(ms))
                    capturing = True
            elif diff > thres:
                capturing = False
            ms += 1000
    return keyframes_ms

def keyframe_masks_new_from_prev(list_of_keyframes):
    if (len(list_of_keyframes) == 0):
        return list_of_keyframes    
    
    prevframe = None
    for keyframe in list_of_keyframes:
        if (prevframe == None):
            prev_obj = []
        else:
            prev_obj = [prevframe.get_fgobj(includelogo=True)]
        keyframe.set_newobj_mask(prev_obj)
        prevframe  = keyframe
        
    return list_of_keyframes


if __name__ == "__main__":
    videopath = sys.argv[1]
    scriptpath = sys.argv[2]
    framediffpath = sys.argv[3]
    outdir = sys.argv[4]
    visual_thres = int(sys.argv[5])
        
    lecture = Lecture(videopath, scriptpath)
    lecture.assign_keyframe_to_words(outdir=outdir + "\\highlight")
    
    framediffs = util.stringlist_from_txt(framediffpath)
    framediffs = util.strings2ints(framediffs)
    keyframes_ms = get_keyframe_times(lecture, framediffs)
    
    keyframes = lecture.capture_keyframes_ms(keyframes_ms, outdir)    
    keyframes = keyframe_masks_new_from_prev(keyframes)

    text_segments = lecture.segment_script(keyframes_ms)
    prevt = 0
    list_of_lecsegs = []
    for i in range(0, len(keyframes_ms)):
        t = keyframes_ms[i]
        startt = prevt
        endt = t
        keyframe = keyframes[i]
        list_of_words = text_segments[i]
        lecseg = LectureSegment(startt, endt, keyframe, list_of_words)
        prevt = t
        list_of_lecsegs.append(lecseg)

     #merge segments with empty-object keyframes
    print "Merging segments"
    print "before: ", len(list_of_lecsegs)
    merged_lecsegs= []
    while (len(list_of_lecsegs) > 0):
        curseg = list_of_lecsegs.pop(0)       
        while (curseg.keyframe.new_visual_score() <= visual_thres and len(merged_lecsegs) > 0):
            prevseg = merged_lecsegs.pop()
            curseg = curseg.merge_prev(prevseg)
        if (curseg.keyframe.new_visual_score() <= visual_thres and len(list_of_lecsegs) > 0):
            nextseg = list_of_lecsegs.pop(0)
            curseg = curseg.merge_next(nextseg)
        merged_lecsegs.append(curseg)
    print "after: ", len(merged_lecsegs)
    list_of_lecsegs = merged_lecsegs
    
    print "Writing to html"
    html = WriteHtml(outdir + "/framediff_stc_vt_" +str(visual_thres)+".html", "Level of detail Summarization")
    html.openbody()       
    for lecseg in list_of_lecsegs:
        if (lecseg.num_nonsilent_words() > 0):
            html.lectureseg(lecseg, debug=True)
    html.closebody()
    html.closehtml()
    
        
    