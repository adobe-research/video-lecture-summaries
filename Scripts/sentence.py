'''python subline_merge_subfigure.py ../SampleVideos/more/khan1/khan1_removelogo.avi ../SampleVideos/more/khan1/khan1_panorama/negate/panorama.png ../SampleVideos/more/khan1/khan1_removelogo_fgpixel_objs_noseg/cleanup/negate/consecutive/ ../alignments/khan1.json "3-D Divergence Theorem Intuition" ../SampleVideos/more/khan1/khan1_framepos.txt ../SampleVideos/more/khan1/khan1_cursorpos.txt

Created on Mar 9, 2015

@author: hijungshin
'''
import Levenshtein

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
            self.ref_words = []
            self.ref_names = []
            
        def contains_phrase(self, string_phrase):
            phrase_words = string_phrase.split()
            words = []
            for i in xrange(len(self.list_of_words) - len(phrase_words)):
                if phrase_words == self.list_of_words[i:i + len(phrase_words)]:
                    words.append(self.list_of_words[i + len(phrase_words) - 1])
            if len(words) > 0:
                return True, words
            else:
                return False, None 
            
        def getstring(self):
            s = ""
            for i in range(0, len(self.list_of_words)):
                word = self.list_of_words[i]
                if not word.issilent:
                    if len(s) > 0:
                        s += (" " + word.raw_word)
                    else:
                        s += word.raw_word
            return s
                        
                    
        @staticmethod
        def levenshtein_dist(s1, s2):
            st1 = s1.getstring()
            st2 = s2.getstring()
            dist = Levenshtein.distance(st1, st2)
            return dist