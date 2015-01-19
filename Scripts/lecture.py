#!/usr/bin/env python
from video import Video, Keyframe
import process_aligned_json as pjson
import processvideo as pvideo
import processframe as pframe
#import lectureplot as lecplot
import cv2
import util
import os
from figure import Figure

class Lecture:
    def __init__(self, video_path, aligned_transcript_path):
        self.video_path = video_path
        if (self.video_path is not None):
            self.video = Video(video_path)   
        else:
            self.video = None
        self.aligned_transcript_path = aligned_transcript_path
        if aligned_transcript_path is not None:
            self.list_of_words = pjson.get_words(aligned_transcript_path)
            self.list_of_stcs = pjson.get_sentences(self.list_of_words)
        else:
            self.list_of_words = []
            self.list_of_stcs = []
        self.default_objects = []  
        self.cursorpos = []
        self.visual_objects = []  

        
    def segment_script(self, list_of_t):        
        segments = [ [] for i in range(0, len(list_of_t))]
        sentences = self.list_of_stcs
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
     
    
    def segment_script_stcs(self, list_of_stc_ids):
        segments = [ [] for i in range(0, len(list_of_stc_ids))]
        
        temp = 0
        for stc in self.list_of_stcs:
            idx = list_of_stc_ids[temp]
            if (stc[len(stc)-1].stc_idx < idx):
                segments[temp].append(stc)
            else:
                temp += 1
                segments[temp].append(stc)
        return segments
             
    
    def get_stc_end_times(self):
        endts = []
        for stc in self.list_of_stcs:
            endts.append(stc[-1].endt)
        return endts
    
    def capture_keyframes_ms(self, list_of_t, outdir="."):
        return self.video.captureframes_ms(list_of_t, outdir)
    
    def capture_keyframes_fid(self, fnumbers, outdir = "."):
        return self.video.capture_keyframes_fid(fnumbers, outdir)
    
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
    
    
    
    def assign_figs_to_stcs(self, list_of_figs):
        self.list_of_figs = list_of_figs
        self.best_fig_ids = []
        for stc in self.list_of_stcs:
            min_dist = float("inf")
            best_fig_id = -1
            for fig_id in range(0, len(list_of_figs)):
                fig = list_of_figs[fig_id]
                dist = Lecture.fig_stc_distance(fig, stc, self.video)
                if (dist < min_dist): 
                    min_dist = dist
                    best_fig_id = fig_id
            if (min_dist <= 0):
                self.best_fig_ids.append(best_fig_id)
            else:
                self.best_fig_ids.append(-1)
                
                
    @staticmethod
    def fig_stc_distance(fig, stc, video):
        stc_start = video.ms2fid(stc[0].startt)
        stc_end = video.ms2fid(stc[-1].endt)
        if (fig.end_fid <= stc_start):
            dist = 1.0 * (stc_start - fig.end_fid)
        elif (fig.start_fid >= stc_end):
            dist = 1.0 * (fig.start_fid - stc_end)
        else:
            dist = -1.0*min(fig.end_fid, stc_end) - max(fig.start_fid, stc_start)
        return dist
    
    @staticmethod
    def obj_stc_distance(obj, stc, video):
        stc_start = video.ms2fid(stc[0].startt)
        stc_end = video.ms2fid(stc[-1].endt)
        if (obj.end_fid <= stc_start):
            dist = -1.0 * (stc_start - obj.end_fid)
    #         print 'obj before stc', dist
        elif (obj.start_fid >= stc_end):
            dist = -1.0 * (obj.start_fid - stc_end)
    #         print 'obj passed stc', dist
        else:
            dist = min(obj.end_fid, stc_end) - max(obj.start_fid, stc_start)
    #         print 'overlap', dist
        return dist
    
    

               

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

    