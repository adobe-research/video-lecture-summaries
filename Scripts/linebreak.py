'''
Created on Nov 14, 2014

@author: hijungshin
'''

from visualobjects import VisualObject
from kalman import KalmanFilter
import math
import util
import sys
import matplotlib.pyplot as plt
import numpy as np
import cv2
from lecture import Lecture
from writehtml import WriteHtml

class LineBreaker:
    def __init__(self, lec, list_of_objs, objdir="temp", debug=False):
        self.lec = lec
        self.list_of_objs = list_of_objs
        self.line_objs = []
        self.numobjs = len(list_of_objs)
        n = len(list_of_objs)
        self.linecost = [[0 for x in range(n)] for x in range(n)]
        self.badness = [[0 for x in range(n)] for x in range(n)]
        self.tpenalty = [0 for x in range(n)]
        self.xpenalty = [0 for x in range(n)]
        self.ypenalty = [0 for x in range(n)]
        self.totalcost = [0 for x in range(n)]
        self.cuts = [0 for x in range(n)]
        self.start_obj_idx = []
        self.end_obj_idx = []
        self.debug = debug
        self.objdir = objdir
        
        
    def dynamic_lines(self, optsec):
        n = self.numobjs#n = len(self.list_of_objs)
        video = self.lec.video
        list_of_objs = self.list_of_objs
        # compute cost of lines
        #linecost = [[0 for x in range(n)] for x in range(n)]
        for i in range(0, n):
            """linecost[i][i]: single object line """
            curobj = list_of_objs[i]
            if (curobj.start_fid == 0 and curobj.end_fid == 0):
                self.linecost[i][i] = -1.0*float("inf") #forced break for initial objects
            else:
                self.badness[i][i] = line_badness(list_of_objs[i:i+1], optsec, video.fps)
                penalty = self.cut_penalty(i, i+1)
                self.linecost[i][i] = self.badness[i][i] + penalty
            
            for j in range(i+1, n):
                self.badness[i][j] = line_badness(list_of_objs[i:j+1], optsec, video.fps)
                penalty = self.cut_penalty(j, j+1)
                self.linecost[i][j] = self.badness[i][j] + penalty
                
        """ compute minimum cost line break """
        for i in range(0, n):
            self.totalcost[i] = float("inf")
            """ c[i] = min (c[j-1] + lc[j,i]) for all j<=i"""
            for j in range(0, i):
                if j == 0:
                    cost = self.linecost[j][i]
                else:
                    cost = self.totalcost[j-1] + self.linecost[j][i]
                if (cost < self.totalcost[i]):
                    self.totalcost[i] = min(self.totalcost[i], cost)
                    self.cuts[i] = j # means [j-i] is good cut
        self.line_objs = []    
        self.line_objs = self.getcutlines(n-1)
        
        self.line_objs.reverse()
        self.start_obj_idx.reverse()
        self.end_obj_idx.reverse()
        return self.line_objs, self.start_obj_idx, self.end_obj_idx
    
    def getcutlines(self, n):
        line = VisualObject.group(self.list_of_objs[self.cuts[n]:n+1], self.objdir)
        self.start_obj_idx.append(self.cuts[n])
        self.end_obj_idx.append(n)
        self.line_objs.append(line)
        if self.cuts[n] == 0:
            return self.line_objs
        else:
            return self.getcutlines(self.cuts[n]-1) 
     
     
    def cut_penalty(self, i, j):
        if (i < len(self.list_of_objs)):
            obj_i = self.list_of_objs[i]
        else: 
            obj_i = None
        if (j < len(self.list_of_objs)):
            obj_j = self.list_of_objs[j]
        else:
            obj_j = None
        if obj_i is None or obj_j is None:
            return 0
        pt = -1.0*VisualObject.gap_frames(obj_i, obj_j)
        px = -1.0*VisualObject.xgap_distance(obj_i, obj_j)
        py = -5.0*VisualObject.ygap_distance(obj_i, obj_j)
        penalty = pt + px + py
        
        self.xpenalty[i] = px
        self.ypenalty[i] = py
        self.tpenalty[i] = py    
        return penalty       
    
    
    def output_lines(self, html, objdir):
        stc_idx = 0
        nfig = 1
        obj_idx = 0
        for obj_idx in range(0, len(self.line_objs)):
            obj = self.line_objs[obj_idx]
            t = self.lec.video.fid2ms(obj.end_fid)
            paragraph = []
            while(self.lec.list_of_stcs[stc_idx][-1].endt < t):
                #write sentence
                paragraph = paragraph + self.lec.list_of_stcs[stc_idx]
                stc_idx += 1
                if (stc_idx >= len(self.lec.list_of_stcs)):
                    break
            html.paragraph_list_of_words(paragraph)
            html.figure(obj.imgpath, "Figure %i" % nfig)
            if (self.debug):
                start_id = self.start_obj_idx[obj_idx]
                end_id = self.end_obj_idx[obj_idx]
                i = str(start_id)
                j = str(end_id)
                html.image(objdir + "/" + self.list_of_objs[start_id].imgpath, classstring="debug")
                html.image(objdir + "/" + self.list_of_objs[end_id].imgpath, classstring="debug")
                html.writestring("<p class=\"debug\">")
                html.writestring("objects " + i + " - " + j + "<br>")
                html.writestring("line badness["+i+"]["+j+"] = " + str(self.badness[start_id][end_id]) + "<br>")
                html.writestring("t penalty = " + str(self.tpenalty[end_id]) +"<br>" )      
                html.writestring("x penalty = " + str(self.xpenalty[end_id]) +"<br>" ) 
                html.writestring("y penalty = " + str(self.ypenalty[end_id]) +"<br>" )             
                html.writestring("</p>")
            nfig += 1    
            
    
    
def is_jump(lineobjs, obj):
    return False

def yctr_distance(list_of_objs, i, j):
    """distance between y coordinates of the center of object i and object j"""
    obj_i = list_of_objs[i]
    obj_j = list_of_objs[j]
    i_ctr = (obj_i.tly + obj_i.bry)/2.0
    j_ctr = (obj_j.tly + obj_j.bry)/2.0
    return abs(i_ctr - j_ctr)

def time(lineobjs, obj, fps): 
    start_fid = lineobjs[0].start_fid
    end_fid = obj.end_fid
    nframes = end_fid - start_fid
    sec = nframes/fps
    return sec
    
def num_words():
    return -1

def visual_content():
    return -1


def is_cut(lineobjs, obj, fps, min_gap, maxt, max_words, max_visual):
    if frame_gap(lineobjs, obj) < min_gap:
        return False
    if time(lineobjs, obj) > maxt:
        return True
    if num_words() > max_words:
        return True
    if visual_content() > max_visual:
        return True 
    if is_jump(lineobjs, obj):
        return True
    return False

def inline_y(ymin, ymax, curobj):   
    minvar = (ymax - ymin)/5.0
    maxvar = (ymax - ymin)/5.0  
    if (curobj.bry >= ymin - minvar):
        if (curobj.tly <= ymax + maxvar):
            return True
        return False
    return False


def linescore(list_of_objs, i, j):
    return 0

def show_inline_region(panorama, objs_in_line, miny, maxy, curobj):

    var1 = (maxy - miny)/5.0
    var2 = (maxy - miny)/5.0  
    
    pcopy = panorama.copy()
    curline = VisualObject.group(objs_in_line, "temp")
    # current line object
    cv2.rectangle(pcopy, (curline.tlx, curline.tly), (curline.brx, curline.bry), (0,0,255), 3)
    # inline region
    cv2.rectangle(pcopy, (curline.tlx, int(miny - var1)), (curline.brx, int(maxy + var2)), (255, 0, 0), 1)
    cv2.rectangle(pcopy, (curobj.tlx, curobj.tly), (curobj.brx, curobj.bry), (0,100,0), 3)
    util.showimages([pcopy])
    

def greedy_break(lec, list_of_objs, objdir, min_gap, maxt, max_words, max_visual):
    lineobjs = []
    objs_in_line = []
    for obj in list_of_objs:
        if is_cut(objs_in_line, obj, lec.video.fps, min_gap, maxt, max_words, max_visual):
            line = VisualObject.group(objs_in_line, objdir)
            lineobjs.append(line)
            objs_in_line = []
        else:
            objs_in_line.append(obj)
    return lineobjs    

   

def line_badness(list_of_objs, optsec, fps):
    badness = 0
    nframes = VisualObject.duration_frames(list_of_objs[0], list_of_objs[-1])
    badness += abs(optsec - 1.0*nframes/fps)
    return 100*badness


def greedy_lines(list_of_objs, panorama):
    lineobjs = []    
    initobj = list_of_objs[0]    
    objs_in_line = [initobj]  
    minys = []  
    maxys = []
    miny = initobj.tly
    maxy = initobj.bry
    minys.append(initobj.tly)
    maxys.append(initobj.bry)
    for i in range(1, len(list_of_objs)):
        curobj = list_of_objs[i]
#         show_inline_region(panorama, objs_in_line, miny, maxy, curobj)
        if inline_y(miny, maxy, curobj):
            miny = min(miny, curobj.tly)
            maxy = max(maxy, curobj.bry)
            objs_in_line.append(curobj)           
        else:
            line = VisualObject.group(objs_in_line, "temp")
#             util.showimages([line.img, curobj.img], "lineobject")
            lineobjs.append(line)
            objs_in_line = []
            objs_in_line.append(curobj)
            miny = curobj.tly
            maxy = curobj.bry
    line = VisualObject.group(objs_in_line)
#     util.showimages([line.img], "temp")
    lineobjs.append(line)
    return lineobjs


            
if __name__ == "__main__":
    videopath = sys.argv[1]
    scriptpath = sys.argv[2]
    objdir = sys.argv[3]
    panoramapath = sys.argv[4]
    panorama = cv2.imread(panoramapath)
    
    lec = Lecture(videopath, scriptpath)
    print lec.video.fps
    img_objs = VisualObject.objs_from_file(lec.video, objdir)
    breaker = LineBreaker(lec, img_objs, objdir, debug=True)
    line_objs = breaker.dynamic_lines(optsec=120)
    
    html = WriteHtml(objdir + "/dynamic_linebreak_debug.html", title="Optimal line break", stylesheet="../Mainpage/summaries.css")
    html.opendiv(idstring="summary-container")
    breaker.output_lines(html, objdir)
    html.closediv()
    html.closehtml()
    
    
