import nltk.data
import re
from sentence import Sentence
import sys
import processvideo
import os

def find_time(regex, s):
    """Find time expression in s specified by regex"""
    r = re.findall(regex, s)
    if (len(r) > 0):
        return r[0]
    else:
        print "starting time stamp not found"
        return -1
    
def add_space_aft_regex(data, regex):
    processed = re.sub(regex, r'\1 ', data)   
    return processed

def get_timed_segments(filename, endtime=None):
    fp = open(filename)
    data = fp.read()
    slist = data.split("\n")
    tregex = r"([0-9]+:[0-9][0-9])"
    stcs = []
    for i in range(0, len(slist)):
        startt = find_time(tregex, slist[i])
        startt = time_in_sec(startt)
        if (i < len(slist)-1):
            endt = find_time(tregex, slist[i+1])            
            endt = time_in_sec(endt)
        elif endtime != None and endtime > startt:            
            endt = endtime
        else: # end time not specified
            endt = startt + 10            
        content = re.sub(tregex, '', slist[i])
        content = re.sub('\n', ' ', content)
        content =  content.lstrip(" ")
        stc = Sentence(content, startt, endt)
        stcs.append(stc)
        
        #print stc.startt, stc.endt, stc.content
    return stcs
    

def get_sentences(filename, endtime):
    """Parse transcript and return list of time-stamped sentences"""
        
    stcs = []
    tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
    fp = open(filename)
    data = fp.read()
    
    #preprocess
    tregex = r"([0-9]+:[0-9][0-9])"
    data = add_space_aft_regex(data, tregex)
    slist = tokenizer.tokenize(data)
    #print len(slist)
    
    for i in xrange(0, len(slist)):
        # find start time
        s = slist[i]
        cur = i
        startt = find_time(tregex, slist[cur])
        
        while startt == -1 and cur >= 0:
            cur -= 1
            startt = find_time(tregex, slist[cur])
        if (startt == -1):
            startt = 0
        else:
            startt = time_in_sec(startt)

        # find end time        
        cur = i+1
        if cur == (len(slist)):
            endt = endtime
        else:
            endt = find_time(tregex, slist[cur])
            
        while endt == -1 and cur < len(slist):
            cur += 1
            endt = find_time(tregex, slist[cur])
        
        #print (endt)            
        endt = time_in_sec(endt)
        
        # remove punctuation and get content
        content = re.sub(tregex, '', s)
        content = re.sub('\n', ' ', content)
        content =  content.lstrip(" ")
        stc = Sentence(content, startt, endt)
        #print stc.content
        #print "----------------------------------"
        stcs.append(stc)
    return stcs
        

def time_in_sec(time):
    """Return time in seconds by parsing input string [0-9]+:[0-9]+"""
    list = time.split(':');
    minute = float(list[0])
    sec = float(list[1])
    return minute*60.0 + sec

def print_sentencetimes(transcript="transcript.txt", time="10:00", fps=15.0, outtxt="sentencetime.txt"):
    my_sentences = get_sentences(transcript, time)
    sentencetimetxt = open(outtxt, "w+")
    sentencetimetxt.write("%i\n" % 1)
    for sentence in my_sentences:
        endtime = sentence.endt
        sentencetimetxt.write("%i\n" % int(endtime*fps))
    sentencetimetxt.close()
    

def print_sentences(transcript="transcript.txt", time="10:00", fps=15.0, outtxt="sentences.txt"):
    my_sentences = get_sentences(transcript, time)
    sentencetxt = open(outtxt, "w+")
    for sentence in my_sentences:
        sentencetxt.write("%s" % sentence.content)
        sentencetxt.write("\t%i" % int(sentence.startt))
        sentencetxt.write("\t%i\n" % int(sentence.endt))
    sentencetxt.close()

def sentences_to_slides(sentences, endts):
    slidetexts = []
    eps = 3.0
    count = 0
    #print 'num segments', len(sentences)
    for endt in endts:
        #print 'endt of frame', endt
        text = []
        for i in range(count, len(sentences)):                    
            sentence = sentences[i]
            #print 'endt of sentence', sentence.endt
            s_begin = sentence.startt
            s_end = sentence.endt
            #print s_end
            if (s_end <= endt+eps):
                text.append(sentence)
            else:
                count = i
                break
        slidetexts.append(text)
    
    # add rest of text to last slide
    text = slidetexts[len(slidetexts)-1]
    for i in range(count, len(sentences)):
        sentence = sentences[i]
        text.append(sentence)
        
    return slidetexts


if __name__ == "__main__":
    
    pv = processvideo.ProcessVideo(sys.argv[1])
    print_sentences(sys.argv[2], sys.argv[3], pv.framerate, sys.argv[4])
    
    
   

