import nltk.data
import re
from sentence import Sentence
import sys
import processvideo

def find_time(regex, s):
    """Find time expression in s specified by regex"""
    r = re.findall(regex, s)
    if (len(r) > 0):
        return r[0]
    else:
        print "starting time stamp not found"
        return -1
    

def get_sentences(filename, endtime):
    """Parse transcript and return list of time-stamped sentences"""
    stcs = []
    tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
    fp = open(filename)
    data = fp.read()
    slist = tokenizer.tokenize(data)
    tregex = "[0-9]+:[0-9]+"
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
            
        endt = time_in_sec(endt)
        
        # remove punctuation and get content
        content = re.sub(tregex, '', s)
        content = re.sub('\n', ' ', content)
        content =  content.lstrip(" ")
        stc = Sentence(content, startt, endt)
        print stc.content
        print "----------------------------------"
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
        sentencetxt.write("\t%i" % int(sentence.startt*fps))
        sentencetxt.write("\t%i\n" % int(sentence.endt * fps))
    sentencetxt.close()

def get_sentences_intime(sentences, tbegin, tend):
    segment = []
    for sentence in sentences:
        s_begin = sentence.startt
        s_end = sentence.endt
        if (s_begin >= tbegin and s_end <= tend):
            segment.append(sentence)
        if (s_begin > tend):
            return segment
    return segment


if __name__ == "__main__":
    
    pv = processvideo.ProcessVideo(sys.argv[1])
    print_sentences(sys.argv[2], sys.argv[3], pv.framerate, sys.argv[4])
    
    
   

