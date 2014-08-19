#!/usr/bin/env python
from video import Video, Keyframe
import process_aligned_json as pjson
import processvideo as pvideo

class Lecture:
    def __init__(self, video_path, aligned_transcript_path):
        self.video_path = video_path
        self.video = Video(video_path)        
        self.aligned_transcript_path = aligned_transcript_path
        self.list_of_words = pjson.get_words(aligned_transcript_path)                
        
    def segment_script(self, list_of_t):
        idx = 0
        segments = [ [] for i in range(0, len(list_of_t))]
        for word in self.list_of_words:            
            if (idx < len(list_of_t)):
                t = list_of_t[idx]
            else:
                t = float("inf")
                idx = len(list_of_t) - 1
            if word.endt > t:
                idx = min(idx+1, len(segments)-1)
            segments[idx].append(word)
        return segments
    
    def capture_keyframes_ms(self, list_of_t, outdir="."):
        return self.video.captureframes_ms(list_of_t, outdir)
    
    def capture_keyframes_fid(self, fnumbers, outdir = "."):
        return self.video.captureframes_fid(fnumbers, outdir)    

class LectureSegment:
    def __init__(self, ):        
        self.startt = -1
        self.endt = -1
        self.keyframe = None
        self.mask = None
        self.list_of_words = []
        self.title =''        
        
    def display(self, ):
        print '---------------------------------------------------------------'
        print 'startt:', self.startt, 'end:', self.endt
        print 'image path', self.keyframe.frame_path
        for word in self.list_of_words:
            print word.original_word,
        print ''
        print '---------------------------------------------------------------'