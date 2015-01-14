'''
Created on Dec 1, 2014

@author: hijungshin
'''

from lecture import Lecture
from writehtml import WriteHtml
from visualobjects import VisualObject
import sys
import os
import util
from linebreak import LineBreaker
import numpy as np
from linear_summary import Summary


def sentence_objs(lec, list_of_objs):
    stc_objs = [[] for i in range(0, len(lec.list_of_stcs))]
    stc_obj_ids = [[] for i in range(0, len(lec.list_of_stcs))]
    
    obj_id = 0
    for obj in list_of_objs:
        max_score = -1.0*float("inf")
        best_stc = 0
        for i in range(0, len(lec.list_of_stcs)):
            stc = lec.list_of_stcs[i]
            score = Summary.obj_stc_distance(obj, stc, lec.video)
            if score > max_score:
                max_score = score
                best_stc = i
        stc_objs[best_stc].append(obj)
        stc_obj_ids[best_stc].append(obj_id)
        obj_id += 1
        
    return stc_objs, stc_obj_ids

def sentence_figures(stc_obj_ids, obj_figure_ids, list_of_objs, list_of_figures):
    stc_figure_ids = []
    stc_figures = []
    for i in range(0, stc_obj_ids):
        obj_ids_in_stc = stc_obj_ids[i]

        # get figure numbers that contain this object
        figure_ids = []
        max_end_fid = -1
        for obj_id in obj_ids_in_stc:
            figure_id = obj_figure_ids[obj_id]
            figure_ids.append(figure_id)
            max_end_fid = max(max_end_fid, list_of_objs[obj_id].end_fid)
        figure_ids = set(figure_ids)
        stc_figure_ids.append(figure_ids)
        
        #get figures
        figure_lineobjs = []
        for fid in figure_ids:
            lineobj = list_of_figures[fid]
            for member in lineobj.members:
                if member.end_fid <= max_end_fid:
                    figure_lineobjs.append(member)
        
        stcobj = VisualObject.group(figure_lineobjs, stcdir)    
        stc_figures.append(stcobj)
    return stc_figures, stc_figure_ids

if __name__ == "__main__":
    videopath = sys.argv[1]
    scriptpath = sys.argv[2]
    objdir = sys.argv[3]
    stcdir = objdir + "/sentences"
    
    if not os.path.exists(os.path.abspath(stcdir)):
        os.makedirs(os.path.abspath(stcdir))
    
    lec = Lecture(videopath, scriptpath)
    list_of_objs = VisualObject.objs_from_file(lec.video, objdir)

    breaker = LineBreaker(lec, list_of_objs, objdir, debug=False)
    breaker_line_objs, [], [] = breaker.dynamic_lines_v3()
    
    # for each stc assign object that belongs to them
    stc_objs, stc_obj_ids = sentence_objs(lec, list_of_objs)
    
        
    html = WriteHtml(stcdir + "/sentences_context_figures.html", title="Sentence Objects")
    html.opentable(border = 3)
    new_objs = []
    for i in range(0, len(lec.list_of_stcs)):
        stc = lec.list_of_stcs[i]
        start_fid = lec.video.ms2fid(stc[0].startt)
        end_fid = lec.video.ms2fid(stc[-1].endt)
        
        # get objects that belong to sentence
        obj_ids_in_stc = stc_obj_ids[i]
        # get figure numbers that contain this object
        figure_ids = []
        max_end_fid = -1
        for obj_id in obj_ids_in_stc:
            figure_id = breaker.bestid[obj_id]
            figure_ids.append(figure_id)
            max_end_fid = max(max_end_fid, list_of_objs[obj_id].end_fid)
        figure_ids = np.unique(figure_ids)
        #get figures
        figure_lineobjs = []
        for id in figure_ids:
            lineobj = breaker_line_objs[id]
            for member in lineobj.members:
                if member.end_fid <= max_end_fid:
                    figure_lineobjs.append(member)
        
        stcobj = VisualObject.group(figure_lineobjs, stcdir)    
        if stcobj is not None:    
            new_objs.append(stcobj)
        
        
        html.opentablerow()
        html.opentablecell()
        html.writestring(str(start_fid))
        html.breakline()
        html.paragraph_list_of_words(stc)
        html.writestring(str(end_fid))
        html.breakline()
        html.closetablecell()
        html.opentablecell()
        if stcobj is not None:
            html.figure(stcobj.imgpath, caption=str(stcobj.start_fid) + " " + str(stcobj.end_fid))
        html.closetablecell()
        html.closetablerow()
    html.closetable()
    html.closehtml()
    VisualObject.write_to_file(stcdir+"/obj_info.txt", new_objs)