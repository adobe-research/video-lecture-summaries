#!/usr/bin/env python
from video import Video, Keyframe
class Lecture:
    def __init__(self, video, aligned_transcript):
        self.video = video
        self.transcript = aligned_transcript

class LectureSegment:
    def __init__(self, ):
        self.startt
        self.endt
        self.keyframe
        self.mask
        self.list_of_words