'''
Created on Nov 2, 2014

@author: hijungshin
'''

import sys
from lecture import Lecture
from visualobjects import VisualObject
from writehtml import WriteHtml
import util
from figure import Figure
import numpy as np

class SummarySentence:
    def __init__(self, list_of_words):
        self.list_of_words = list_of_words
        self.startt = list_of_words[0].startt
        self.endt = list_of_words[-1].endt
        self.list_of_objs = []
        self.visobj = None
    
    def figure(self, fig, list_of_objs):                
        self.list_of_objs = list_of_objs
        self.visobj = fig.highlight_objs(list_of_objs)


class Summary:
    def __init__(self, lec, list_of_figures):
        self.lec = lec
        self.list_of_stcs = lec.list_of_stcs
        self.list_of_figures = list_of_figures
        """initialize stc-figure correspondence"""
        self.stc_fig_ids = Summary.fig_ids_per_stc(self.list_of_stcs, self.list_of_figures, self.lec.video)
        
        """initialize Sentences"""
        self.list_of_Stcs = []
        for stc in self.list_of_stcs:
            self.list_of_Stcs.append(SummarySentence(stc))
            
            
        for i in range(0, len(self.list_of_figures)):
            fig = self.list_of_figures[i]
            """ids of stcs that belong to figure_i"""
            fig_stcs = []
            for j in range(0, len(self.stc_fig_ids)): 
                """for each sentence, if it overlaps with figure i"""
                if (self.stc_fig_ids[j] == i):
                    fig_stcs.append(j)
                    
            self.put_figure_to_Stcs(fig, fig_stcs, self.lec.video)                
            
            
    def put_figure_to_Stcs(self, fig, stc_ids, video):
#         print 'num associated stcs', len(stc_ids)
        if len(stc_ids) == 0:
            return
        stc_objs = [[] for x in range(0, len(stc_ids))]
        for obj in fig.list_of_newobjs:
            obj_startt = self.lec.video.fid2ms(obj.start_fid)
            obj_endt = self.lec.video.fid2ms(obj.end_fid)
            
            min_dist = float("inf")
            for i in range(0, len(stc_ids)): 
                """for stcs that belong to this figure"""
                stc_id = stc_ids[i]
                stc = self.list_of_stcs[stc_id]
                stc_startt = stc[0].startt
                stc_endt = stc[-1].endt
                dist = Summary.obj_stc_distance(obj, stc, video)
                if dist < min_dist:
#                     for word in stc:
#                         print word.original_word
#                     print 'obj_startt', obj_startt, 'obj_endt', obj_endt, 'stc_start', stc_startt, 'stc_endt', stc_endt, 'dist', dist
                    min_dist = dist
                    best_stc = i
#             util.showimages([obj.img], "obj")
#             print 'best_stc id', best_stc
            stc_objs[best_stc].append(obj)
        
        
        for i in range(0, len(stc_ids)):
            stc_id = stc_ids[i]
            Stc = self.list_of_Stcs[stc_id]
            Stc.figure(fig, stc_objs[i])        
        
        
    @staticmethod
    def fig_ids_per_stc(list_of_stcs, list_of_figs, video):        
        best_fig_ids = []
        for stc in list_of_stcs:
            min_dist = float("inf")
            best_fig_id = -1
            for fig_id in range(0, len(list_of_figs)):
                fig = list_of_figs[fig_id]
                dist = Summary.fig_stc_distance(fig, stc, video)
                if (dist < min_dist): 
                    min_dist = dist
                    best_fig_id = fig_id
            if (min_dist <= 0):
                best_fig_ids.append(best_fig_id)
            else:
                best_fig_ids.append(-1)
        return best_fig_ids
                
    @staticmethod
    def fig_stc_distance(fig, stc, video):
        stc_start = video.ms2fid(stc[0].startt)
        stc_end = video.ms2fid(stc[-1].endt)
        if (fig.end_fid <= stc_start):
            dist = 1.0 * (stc_start - fig.end_fid)
        elif (fig.start_fid >= stc_end):
            dist = 1.0 * (fig.start_fid - stc_end)
        else:
            dist = max(fig.start_fid, stc_start) - min(fig.end_fid, stc_end)
        return dist
    
    
    @staticmethod
    def obj_stc_distance(obj, stc, video):
        stc_start = video.ms2fid(stc[0].startt)
        stc_end = video.ms2fid(stc[-1].endt)
        if (obj.end_fid <= stc_start):
            dist = 1.0 * (stc_start - obj.end_fid)
    #         print 'obj before stc', dist
        elif (obj.start_fid >= stc_end):
            dist = 1.0 * (obj.start_fid - stc_end)
    #         print 'obj passed stc', dist
        else:
            dist = max(obj.start_fid, stc_start) - min(obj.end_fid, stc_end) 
    #         print 'overlap', dist
        return dist
    

if __name__ == "__main__":
    videopath = sys.argv[1]
    scriptpath = sys.argv[2]
    objdir = sys.argv[3]
    linetxt = sys.argv[4]
    panoramapath = sys.argv[5]
    lec = Lecture(videopath, scriptpath)
    print 'fps', lec.video.fps
    list_of_objs = VisualObject.objs_from_file(lec.video, objdir)
    line_ids = util.stringlist_from_txt(linetxt)
    line_ids = util.strings2ints(line_ids)
    
    figuredir = objdir + "/line_figures"
    list_of_figures = Figure.getfigures(list_of_objs, line_ids, figuredir)
    
    summary = Summary(lec, list_of_figures)    
    
    html = WriteHtml(objdir + "/linear_summary.html", "Linear Summary", stylesheet="../Mainpage/summaries.css")
    html.figure(panoramapath, width="98%")
    html.figure_script(summary)
    html.closehtml()
    