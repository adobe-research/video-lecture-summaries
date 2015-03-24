'''
Created on Mar 9, 2015
@author: hijungshin
'''

import sys
from visualobjects import VisualObject
import process_aligned_json as pjson
from video import Video
import numpy as np
from writehtml import WriteHtml
import os

def link_stc_per_obj():
    videopath = sys.argv[1]
    scriptpath = sys.argv[2]
    objdir = sys.argv[3]
    
    video = Video(videopath)
    list_of_objs = VisualObject.objs_from_file(video, objdir)
    list_of_words = pjson.get_words(scriptpath)
    list_of_stcs = pjson.get_sentences(list_of_words)
    
    closest_stc_ids = []
    n_sentences = len(list_of_stcs)
    """for each object, if it overlaps with stc, find most overlapping stc"""
    for obj in list_of_objs:
        min_dist = float("inf")
        closest_stc_id = -1
        for i in range(0,  n_sentences):
            sentence = list_of_stcs[i]
            dist = VisualObject.obj_stc_distance(obj, sentence)
            if (dist < 0 and dist < min_dist):
                min_dist = dist
                closest_stc_id = i
        closest_stc_ids.append(closest_stc_id)
    
#     util.write_ints(closest_stc_ids, objdir + "/stc_ids_2.txt")
    
    figdir = objdir + "/sentence_obj_test"
    if not os.path.exists(os.path.abspath(figdir)):
        os.makedirs(os.path.abspath(figdir))
    html = WriteHtml(figdir + "/sentence_obj.html", stylesheet ="../Mainpage/stc_obj.css")
    obj_stcids = np.array(closest_stc_ids)
    html.opentable()
    for i in range(0, len(list_of_stcs)):
        html.opentablerow()
        cur_stc = list_of_stcs[i]
        indices_of_objs = np.where(obj_stcids == i)[0]
        cur_objs = [list_of_objs[x] for x in indices_of_objs]
        if (len(cur_objs)> 0):
            cur_obj = VisualObject.group(cur_objs,  figdir)
        else: 
            cur_obj = None
        
        html.opentablecell()
        html.writestring("%s.  " %(i+1))
        html.write_list_of_words(cur_stc)
        html.closetablecell()
        
        html.opentablecell()
        if (cur_obj is not None):
            html.image(cur_obj.imgpath)
        html.closetablecell()
        
        html.closetablerow()
    html.closetable()
    
    html.closehtml()

    
    
if __name__ == "__main__":
    link_stc_per_obj()
        