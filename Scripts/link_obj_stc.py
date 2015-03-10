'''
Created on Mar 9, 2015

@author: hijungshin
'''

import sys
from visualobjects import VisualObject
import process_aligned_json as pjson
from video import Video
import util

if __name__ == "__main__":
    videopath = sys.argv[1]
    scriptpath = sys.argv[2]
    objdir = sys.argv[3]
    
    
    video = Video(videopath)
    list_of_objs = VisualObject.objs_from_file(video, objdir)
    list_of_words = pjson.get_words(scriptpath)
    list_of_stcs = pjson.get_sentences(list_of_words)
    
    closest_stc_ids = []
    n_sentences = len(list_of_stcs)
    for obj in list_of_objs:
        min_dist = float("inf")
        closest_stc_id = -1
        for i in range(0,  n_sentences):
            sentence = list_of_stcs[i]
            dist = VisualObject.obj_stc_distance(obj, sentence)
            if (dist < min_dist):
                min_dist = dist
                closest_stc_id = i
        closest_stc_ids.append(closest_stc_id)
    
    util.write_ints(closest_stc_ids, objdir + "/stc_ids.txt")