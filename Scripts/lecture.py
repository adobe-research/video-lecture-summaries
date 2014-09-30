#!/usr/bin/env python
from video import Video, Keyframe
import process_aligned_json as pjson
import processvideo as pvideo
import processframe as pframe
import cv2
import util
import os

class Lecture:
    def __init__(self, video_path, aligned_transcript_path):
        self.video_path = video_path
        self.video = Video(video_path)        
        self.aligned_transcript_path = aligned_transcript_path
        self.list_of_words = pjson.get_words(aligned_transcript_path)
        self.default_objects = []    
        
    def segment_script(self, list_of_t):        
        segments = [ [] for i in range(0, len(list_of_t))]
        sentences = pjson.get_sentences(self.list_of_words)        
        temp = [] + list_of_t
        temp.append(float("inf"))
        
        for stc in sentences:
            for idx in range(0, len(temp)):
                t = temp[idx]                
                if stc[len(stc)-1].endt <= t:
                    seg = min(idx, len(segments)-1)
                    for word in stc:
                        segments[seg].append(word)
                    break            
        return segments
    
    def capture_keyframes_ms(self, list_of_t, outdir="."):
        return self.video.captureframes_ms(list_of_t, outdir)
    
    def capture_keyframes_fid(self, fnumbers, outdir = "."):
        return self.video.captureframes_fid(fnumbers, outdir)
    
    def assign_keyframe_to_words(self, emph_words=["here", "here,", "here."], outdir = "temp"):
        startts = []
        endts = []

        for word in self.list_of_words:
            if word.original_word in emph_words:
                endts.append(word.endt) # 1 second buffer
                startts .append(word.startt)
        if (len(startts) == 0):
            return

        endframes = self.capture_keyframes_ms(endts, "temp")
        startframes = self.capture_keyframes_ms(startts, "temp")
  
        i = 0
        for word in self.list_of_words:
            if word.original_word in emph_words:
                word.keyframe = endframes[i]
                diff = cv2.absdiff(endframes[i].frame, startframes[i].frame)
                diff = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
                ret, mask = cv2.threshold(diff, 100, 255, cv2.THRESH_BINARY)
                word.mask = mask                
                #highlight_frame = pframe.highlight(word.keyframe.frame, word.mask)
                word.highlight_path = word.keyframe.frame_path #outdir + "/word_highlight_" + ("%06i" % word.startt) + ".png"
                #cv2.imwrite(highlight_path, highlight_frame)
                #word.highlight_path = os.path.abspath(highlight_path)
                i += 1         
                
    def segment(self, list_of_t, outdir="temp"):
        keyframes = self.capture_keyframes_ms(list_of_t, outdir)
        script_segments = self.segment_script(list_of_t)
        prevt = 0
        list_of_lecsegs = []
        for i in range(0, len(list_of_t)):
            t = list_of_t[i]
            lecseg = LectureSegment(prevt, t, keyframes[i], script_segments[i])
            list_of_lecsegs.append(lecseg)
            prevt = t
        
        return list_of_lecsegs
               

class LectureSegment:
    def __init__(self, startt=-1, endt=-1, keyframe=None, list_of_words=[], title=''):        
        self.startt = startt
        self.endt = endt
        self.keyframe = keyframe
        self.list_of_words = list_of_words
        self.title = title        
        
    def num_nonsilent_words(self,):
        count = 0
        for word in self.list_of_words:
            if not word.issilent:
                count += 1
        return count
    
    def num_stcs(self, ):
        start_i = self.list_of_words[0].stc_idx
        end_i = self.list_of_words[-1].stc_idx
        return (end_i - start_i + 1)
    
    def getsentence(self, idx):
        num_stc = self.num_stcs()
        if (idx < 0 or idx >= num_stc):
            print "LectureSegment.getsentences(idx): sentence index out of bound"
								stc = []
								start_idx = self.list_of_words[0].stc_idx
        for word in self.list_of_words:
								    if word.stc_idx - start_idx == idx:
																stc.append(word)
												else:
																break
								return stc
	
        
    def display(self, ):
        print '---------------------------------------------------------------'
        print 'startt:', self.startt, 'end:', self.endt
        print 'image path', self.keyframe.frame_path
        for word in self.list_of_words:
            print word.original_word,
        print ''
        print '---------------------------------------------------------------'
        
    def merge_next(self, next_lecseg):
        #assert(self.endt == next_lecseg.startt)
        merged = LectureSegment()
        merged.startt = self.startt
        merged.endt = next_lecseg.endt
        merged.keyframe = next_lecseg.keyframe
        merged.keyframe.fg_mask = cv2.bitwise_or(self.keyframe.fg_mask, next_lecseg.keyframe.fg_mask)
        merged.keyframe.newobj_mask = cv2.bitwise_or(self.keyframe.newobj_mask, next_lecseg.keyframe.newobj_mask)        
        merged.list_of_words = self.list_of_words + next_lecseg.list_of_words        
        merged.title = self.title
        if (next_lecseg.title != ''):
            merged.title += " "
            merged.title += next_lecseg.title
        return merged
    
    def merge_prev(self, prev_lecseg):
        return prev_lecseg.merge_next(self)    

    