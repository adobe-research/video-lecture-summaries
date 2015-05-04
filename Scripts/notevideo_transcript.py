'''
Created on Apr 29, 2015

@author: Valentina
'''


import process_aligned_json as pjson
import sys

def format_tstring(sec):
    mm = sec/60
    ss = sec - mm*60
    string = "%i:%02i"%(mm,ss)
    return string
    

if __name__ == "__main__":

    scriptpath = sys.argv[1]
    outfilename = sys.argv[2]
    max_dur = 3000.0
    list_of_words = pjson.get_words(scriptpath)
    
    txtfile = open(outfilename, "w")
    lastt = 0.0
    text = []
    count = 0
    nwords = len(list_of_words)
    txtfile.write("{\n \"data\":[\n")
    
    for word in list_of_words:        
        if not word.issilent:
            text.append(word)
        count += 1
        dur = word.endt-lastt
        
        if (dur > max_dur or count == nwords):
            time = int(text[0].startt/1000.0)
            transcript = ""
            for i in range(0, len(text)):
                w = text[i]
                if i == 0:
                    transcript = transcript + w.original_word
                else:
                    transcript = transcript + " " + w.original_word           
            txtfile.write("\
     {\n \
    \"time\": %i,\n \
    \"text\": \"%s\"\n \
    }" %(time, transcript))
            if count != nwords:
                txtfile.write(",\n")
            lastt = text[-1].endt
            text = []
    
    txtfile.write("\n]\n}")
            
    txtfile.close()
    
