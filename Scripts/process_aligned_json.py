#!/usr/bin/env python
import re
from matplotlib import pyplot as plt
from video import Video
import cv2
import numpy as np
import processframe as pf

class Word:
    def __init__(self, original_word, aligned_word, startt, endt, line_idx, speaker):
        self.original_word = original_word
        self.aligned_word = aligned_word
        self.startt = float(startt)*1000
        self.endt = float(endt)*1000
        self.duration = self.endt - self.startt
        self.rep_time = self.endt - self.duration/2.0
        self.line_idx = int(line_idx)
        self.speaker = speaker
        self.issilent = (original_word == "{p}")
        self.keyframe = None
        self.mask = None
        self.highlight_path = None
        self.stc_idx = -1
        
def get_sentences(list_of_words):
    if (len(list_of_words) <= 0):
        return []
    num_stc = list_of_words[len(list_of_words) - 1].stc_idx + 1
    if (num_stc <= 0):
        return []
    sentences = [[] for i in range(0, num_stc)]    
    for word in list_of_words:        
        sentences[word.stc_idx].append(word)
    return sentences


def assign_frame_to_words(video, list_of_words):
    cap = cv2.VideoCapture(video.filepath)
    
    prevframe = np.empty((video.height, video.width, 3), dtype=np.uint8)
    i = 0
    while (cap.isOpened()):
        ret, frame = cap.read()
        if (ret == True and i < len(list_of_words)):
            word = list_of_words[i]
            word_time = word.startt * 1000
            frame_time = cap.get(0)
            #print 'frame time', frame_time
            #print 'word time', word_time
            if (frame_time >= word_time ):
                diff = cv2.absdiff(frame, prevframe)
                diff = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
                ret, mask = cv2.threshold(diff, 100, 255, cv2.THRESH_BINARY)
                #highlight_frame = pf.highlight(frame, mask)
                word.frame = frame
                word.mask = mask
                i += 1
                #print word.original_word
                #cv2.imshow("word frame", word.frame)
                #cv2.imshow("word mask", word.mask)
                #cv2.waitKey()
        else:
            break
        prevframe = frame
    return list_of_words

def get_words(aligned_json):
    fp = open(aligned_json)    
    line = fp.readline()
    list_of_words = []
    stc_idx = 0
    while(True):
        if not line:
            break
        if ("{" in line):
            word = parse_word(fp)
            word.stc_idx = stc_idx
            if ('.' in word.original_word):
                stc_idx += 1
            list_of_words.append(word)
        line = fp.readline()
    return list_of_words
    
def parse_word(fp):
    original_word = ''
    aligned_word = ''
    speaker = ''
    line_idx = -1
    startt = -1.0
    endt = -1.0
    
    line = fp.readline()    
    while (line != None):
        if ("\"end\":" in line):
            temp = line.split(':')
            endt = re.findall("\d+.\d+", temp[1])
            endt = endt[0]
        elif ("\"start\":" in line):
            temp = line.split(':')
            startt = re.findall("\d+.\d+", temp[1])
            startt = startt[0]
        elif ("\"word\":" in line):
            temp = line.split(':')
            original_word = re.findall('"([^"]*)"', temp[1])
            original_word = original_word[0]
        elif("\"alignedWord\":" in line):
            temp = line.split(':')
            aligned_word = re.findall('"([^"]*)"', temp[1])
            aligned_word = aligned_word[0]
        elif("\"line_idx\":" in line):
            temp = line.split(':')
            line_idx = re.findall("\d+", temp[1])
            line_idx = line_idx[0]
        elif("\"speaker\":" in line):
            temp = line.split(':')
            speaker = re.findall('"([^"]*)"', temp[1])
            speaker = aligned_word[0]
        elif ("}" in line):
            return Word(original_word, aligned_word, startt, endt, line_idx, speaker)
        line = fp.readline()
        
def plot_silence(list_of_words):
    starttime = list_of_words[0].startt
    endtime = list_of_words[len(list_of_words)-1].endt
    ts = []
    ys = []
    half_duration = []
    for word in list_of_words:
        if word.issilent:
            t = word.startt + word.duration/2.0
            ts.append(t)
            ys.append(word.duration)
            half_duration.append(word.duration/2.0)
            
    
    plt.errorbar(ts, ys, xerr = half_duration, fmt='o')
    plt.xlim((starttime, endtime))
    plt.title("Silence")
    plt.savefig("silence_plot.png")
    plt.close()
            

    
