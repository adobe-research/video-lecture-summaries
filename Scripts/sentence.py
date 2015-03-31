'''
Created on Mar 9, 2015

@author: hijungshin
'''

class Sentence:
        def __init__(self, list_of_words, video, stcid):
            self.list_of_words = list_of_words
            self.startt = list_of_words[0].startt
            self.endt = list_of_words[-1].endt
            self.stcstroke = None
            self.video = video
            self.id = stcid
            self.start_fid = self.video.ms2fid(self.startt)
            self.end_fid = self.video.ms2fid(self.endt)
            self.subline = None
