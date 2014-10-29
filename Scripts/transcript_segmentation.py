'''
Created on Oct 28, 2014

@author: hijungshin
'''

import sys
import util
from lecture import Lecture
from writehtml import WriteHtml

def write_to_html(html, segments):
    html.opendiv()
    html.opentable()
    for seg in segments:
        html.opentablerow()
        html.opentablecell()
        for stc in seg:
            html.paragraph_list_of_words(stc)
        html.closetablecell()
        html.closetablerow()
    html.closetable()
    html.closediv()
    return

def get_segment_ids(filepath):
    txtfile = open(filepath)
    line = txtfile.readline()
    line = line.replace('[', '')
    line = line.replace(']', '')
    ids = line.split(',')
    ids = util.strings2ints(ids)
    return ids

if __name__ == "__main__":
    jsonfile = sys.argv[1]
    segfile = sys.argv[2]
    htmlfile = sys.argv[3]
    
    lec = Lecture(None, jsonfile)
    list_of_stc_ids = get_segment_ids(segfile)
    segments = lec.segment_script_stcs(list_of_stc_ids)
    
    html = WriteHtml(htmlfile, "Transcript Segmentation")
    write_to_html(html, segments)
    html.closehtml()