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
import os
import processframe as pf
import overlap

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
        self.totalcost = [float("inf") for x in range(n)]
        self.bestid = [-1 for x in range(n)]
        self.cuts = [0 for x in range(n)]
        self.start_obj_idx = []
        self.end_obj_idx = []
        self.debug = debug
        self.objdir = objdir
        self.linedir = self.objdir + "/lines"
        
    def initial_obj_cost(self):
        return -1e7
        
    def dynamic_lines_version1(self, optsec):
        n = self.numobjs#n = len(self.list_of_objs)
        video = self.lec.video
        list_of_objs = self.list_of_objs
        # compute cost of lines
        #linecost = [[0 for x in range(n)] for x in range(n)]
        for i in range(0, n):
            """linecost[i][i]: single object line """
            curobj = list_of_objs[i]
            if (curobj.start_fid == 0 and curobj.end_fid == 0):
                self.linecost[i][i] = self.initial_obj_cost()
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
            for j in range(0, i+1):
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
    
    def dynamic_lines(self):
        self.compute_costs_v3()
        self.compute_cuts_v3()
        return self.get_opt_lines()
    
    def _lines(self): 
        self.compute_greedy_cuts()
        lines =  self.cutlines_nonlinear(self.numobjs)
        lineobjs = []
        for line in lines:
            lineobj = VisualObject.group(line, self.linedir)
            lineobjs.append(lineobj)
        return lineobjs, [], []
    
    def get_opt_lines(self):
        n = self.numobjs
        self.line_objs = []    
        self.line_objs = self.getcutlines(n-1)
        self.line_objs.reverse()
        self.start_obj_idx.reverse()
        self.end_obj_idx.reverse()
        VisualObject.write_to_file(self.linedir + "/obj_info.txt", self.line_objs)
        return self.line_objs, self.start_obj_idx, self.end_obj_idx
    
    def compute_cuts(self):
        n = self.numobjs
        """ compute minimum cost line break """
        for i in range(0, n):
            self.totalcost[i] = float("inf")
            """ c[i] = min (c[j-1] + lc[j,i]) for all j<=i"""
            for j in range(0, i+1):
                if j == 0:
                    cost = self.linecost[j][i]
                else:
                    cost = self.totalcost[j-1] + self.linecost[j][i]
                if (cost < self.totalcost[i]):
                    self.totalcost[i] = cost
                    self.cuts[i] = j # means [j-i] is good cut       
#             print 'self.totalcost[',i,']=', self.totalcost[i]
        print self.totalcost
        
    def compute_greedy_cuts(self):
        n = self.numobjs
        self.totalcost[0] = linecost_v3(self.list_of_objs[0:1])
        self.cuts[0] = 0
        self.bestid[0] = 0
        for i in range(1, n):
            newobj = self.list_of_objs[i]
            mincost = float("inf")
            j = i -1
            cj = self.totalcost[j]
            minaddcost = float("inf")
            prevlines = []
                
            prevlines = self.cutlines_nonlinear(i-1)
            bestline = 0
            for idx in range(0, len(prevlines)):
                line = prevlines[idx]
                add = addcost_v3(line, newobj)
#                 if (len(prevlines) == 5):
#                     print 'i', i, 'prev line idx', idx, 'of', len(prevlines) 
#                     print 'addcost', add
#                     tempobj = VisualObject.group(line, "temp")
#                     util.showimages([tempobj.img, newobj.img])

                if (add < minaddcost):
                    bestline = idx
                    minaddcost = min(add, minaddcost)
            newlinecost = linecost_v3(self.list_of_objs[i:i+1])
#             print 'newlinecost', newlinecost
#             util.showimages([newobj.img])
            if (newlinecost < minaddcost):
                minaddcost = newlinecost
                bestline = len(prevlines)
            jcost = cj + minaddcost

            if (jcost < mincost):
                mincost = jcost
                self.totalcost[i] = mincost
                self.cuts[i] = j
            self.bestid[i] = bestline
        print 'totalcost', self.totalcost
        print 'cuts', self.cuts
        print 'bestid', self.bestid
                
                
    def compute_costs_v1(self, optsec):
        n = self.numobjs#n = len(self.list_of_objs)
        video = self.lec.video
        list_of_objs = self.list_of_objs
        # compute cost of lines
        #linecost = [[0 for x in range(n)] for x in range(n)]
        for i in range(0, n):
            """linecost[i][i]: single object line """
            curobj = list_of_objs[i]
            if (curobj.start_fid == 0 and curobj.end_fid == 0):
                self.linecost[i][i] = self.initial_obj_cost()
            else:
                self.badness[i][i] = line_badness(list_of_objs[i:i+1], optsec, video.fps)
                penalty = self.cut_penalty(i, i+1)
                self.linecost[i][i] = self.badness[i][i] + penalty
            
            
            for j in range(i+1, n):
                self.badness[i][j] = line_badness(list_of_objs[i:j+1], optsec, video.fps)
                penalty = self.cut_penalty(j, j+1)
                self.linecost[i][j] = self.badness[i][j] + penalty
                
    def compute_costs_v2(self):
        n = self.numobjs
        list_of_objs = self.list_of_objs
        for i in range(0, n):
    
            for j in range(i, n):
                self.linecost[i][j] = -1.0* VisualObject.compactness(list_of_objs[i:j+1])
#                        temp = VisualObject.group(list_of_objs[i:j+1], "temp")
#                     print 'self.linecost', self.linecost[i][j]
#                     util.showimages([temp.img])
#             print self.linecost[i]
#             util.showimages(self.list_of_objs[0].img)

    def compute_costs_v3(self):
        n = self.numobjs
        list_of_objs = self.list_of_objs
        for i in range(0, n):
            self.linecost[i][i] = 0
            for j in range(i+1, n):
                self.linecost[i][j] = self.linecost[i][j-1] + addcost_v3(list_of_objs[i:j], list_of_objs[j])
#                 if (i == 5):
#                 temp = VisualObject.group(list_of_objs[i:j+1], "temp")
#                 print 'self.linecost', self.linecost[i][j]
#                 util.showimages([temp.img])
#             print self.linecost[i]
#             util.showimages(self.list_of_objs[0].img)         
                
    def compute_costs(self):
        n = self.numobjs
        video = self.lec.video
        list_of_objs = self.list_of_objs
        # compute cost of lines
        #linecost = [[0 for x in range(n)] for x in range(n)]
        for i in range(0, n):
            """linecost[i][i]: single object line """
            curobj = list_of_objs[i]
            if (curobj.start_fid == 0 and curobj.end_fid == 0):
                self.badness[i][i] = -100
                self.linecost[i][i] = self.badness[i][i]

            for j in range(i+1, n):
                nextobj = list_of_objs[j:j+1][0]
                self.badness[i][j] = self.linecost[i][j-1] + self.addcost(list_of_objs[i:j], nextobj)
                self.linecost[i][j] = self.badness[i][j]
                
    def addcost(self, list_of_objs, newobj):
        if newobj is None:
            return 0
        penalty = 0
        cx = (newobj.tlx + newobj.brx)/2.0
        cy = (newobj.tly + newobj.bry)/2.0
        z1minx, z1miny, z1maxx, z1maxy = VisualObject.bbox(list_of_objs)
        z1width = z1maxx - z1minx + 1
        xpad = 30
        ypad = min(max(30, 2500.0/z1width), 50)
        z1minx -= xpad
        z1miny -= ypad
        z1maxx += xpad
        z1maxy += ypad
        
        if z1miny <= cy and cy <= z1maxy:
            additem = -100
            if newobj.brx >= z1minx and newobj.tlx <= z1maxx: # in bbox 
                penalty = 0
            elif newobj.brx < z1minx: # inline left:
                penalty = z1minx - newobj.brx + xpad
            elif newobj.tlx > z1maxx: #inline right:
                penalty = newobj.tlx - z1maxx + xpad
            else:
                print 'linebreak.addcost ERROR: inline, not in bbox, neither left nor right'
            if penalty > 100:
                penalty += 500
                additem = 0

        else:
            xpenalty = abs(z1maxx - newobj.tlx)
            if cy > z1maxy:
                ypenalty = cy-z1maxy + ypad
            elif cy < z1miny:
                ypenalty = z1miny - cy + ypad
            else:
                ypenalty = 0
                print 'linebreak.addcost ERROR: should never get here'
            penalty = xpenalty + ypenalty
            additem = 2000
#             if list_of_objs[0].start_fid == 2760:
#             print 'penalty', penalty, 'additem', additem, '=', penalty+additem
#             templine = VisualObject.group(list_of_objs,"temp")
#             util.showimages([templine.img, newobj.img], "line and newobj")
        return additem + penalty  
    
    def addcost_v2(self, list_of_objs, newobj):
        if newobj is None:
            return 0
        cx = (newobj.tlx + newobj.brx)/2.0
        cy = (newobj.tly + newobj.bry)/2.0
        z1minx, z1miny, z1maxx, z1maxy = VisualObject.bbox(list_of_objs)
        xpenalty = 0 
        ypenalty = 0
        if z1miny <= cy and cy <= z1maxy: # definitely in-line
            additem = -100
            if newobj.brx >= z1minx and newobj.tlx <= z1maxx: # in bbox 
                penalty = 0
            elif newobj.brx < z1minx: # inline left:
                penalty = z1minx - newobj.brx
            elif newobj.tlx > z1maxx: #inline right:
                penalty = newobj.tlx - z1maxx
            else:
                print 'linebreak.addcost ERROR: inline, not in bbox, neither left nor right'

        else:           
            xpenalty = abs(z1maxx - newobj.tlx)
            if cy > z1maxy:
                ypenalty = cy-z1maxy
            elif cy < z1miny:
                ypenalty = z1miny - cy
            else:
                ypenalty = 0
                print 'linebreak.addcost ERROR: should never get here'
            penalty = xpenalty + ypenalty
            if (newobj.tlx > z1maxx and xpenalty > 100):
                additem = 2000
            if (newobj.brx < z1minx and xpenalty > 100):
                additem = 2000
            if (xpenalty > 100 and ypenalty > 20):
                additem = 2000
            else:
                additem = 0
#             additem = -100
#             if xpenalty > 100 and ypenalty > 100:
#                              
#         if list_of_objs[0].start_fid == 10460:
#             print 'xpenalty', xpenalty, 'ypenalty', ypenalty, 'additem', additem, '=', penalty+additem
#             templine = VisualObject.group(list_of_objs,"temp")
#             util.showimages([templine.img, newobj.img], "line and newobj")
        return additem + penalty   
    
    def cutlines_nonlinear(self, n):
        segments_unique = np.unique(self.bestid[0:n+1])
        n_segments = len(segments_unique)
        lines = [[] for i in range(0, n_segments)]
        for i in range(0, len(self.bestid[0:n+1])):
#             print 'i', i, 'of', (self.numobjs)
            idx = self.bestid[i]
            obj = self.list_of_objs[i]
            lines[idx].append(obj)
        return lines
        

    def getcutlines(self, n, line_dir=None):
        if line_dir is None:
            linedir = self.linedir
        else:
            linedir = line_dir 
        if not os.path.exists(linedir):
            os.makedirs(linedir)
        line = VisualObject.group(self.list_of_objs[self.cuts[n]:n+1], linedir)
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
        
        pt = 0
        xgap = VisualObject.xgap_distance(obj_i, obj_j)
        if (xgap < 0):
            px = 2.0 * xgap
        else:
            px = - 1.0 * xgap 
        ygap = VisualObject.ygap_distance(obj_i, obj_j)
        py = -1.0* VisualObject.ygap_distance(obj_i, obj_j)
        penalty = pt + 0.5*px + py
        
        self.xpenalty[i] = px
        self.ypenalty[i] = py
        self.tpenalty[i] = pt    
        return penalty       
    
    
    def write_to_html(self, html, objdir, list_of_objs=None):
        if (list_of_objs is None):
            list_of_objs = self.line_objs
        stc_idx = 0
        nfig = 1
        obj_idx = 0
        for obj_idx in range(0, len(list_of_objs)):
            obj = list_of_objs[obj_idx]
            t = self.lec.video.fid2ms(obj.end_fid)
            paragraph = []
#             while(self.lec.list_of_stcs[stc_idx][-1].endt < t):
# #                write sentence
#                 paragraph = paragraph + self.lec.list_of_stcs[stc_idx]
#                 stc_idx += 1
#                 if (stc_idx >= len(self.lec.list_of_stcs)):
#                     break
            html.paragraph_list_of_words(paragraph)
            html.figure(list_of_objs[obj_idx].imgpath, "Merged Figure %i" % nfig)
            if (self.debug):
#                 html.figure(self.line_objs[obj_idx].imgpath, "Original Figure %i" % nfig)
                start_id = self.start_obj_idx[obj_idx]
                end_id = self.end_obj_idx[obj_idx]
                i = str(start_id)
                j = str(end_id)
#                 html.image(objdir + "/" + self.list_of_objs[start_id].imgpath, classstring="debug")
#                 html.image(objdir + "/" + self.list_of_objs[end_id].imgpath, classstring="debug")
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

def getcutlines(cuts, list_of_objs, n, lineobjs):
    line = list_of_objs[cuts[n]:n+1]
    lineobjs.append(line)
    if cuts[n] == 0:
        return lineobjs
    else:
        return getcutlines(cuts, list_of_objs, cuts[n]-1, lineobjs) 

def linecost_v3(list_of_objs):
    linecost = 0
    for i in range(0, len(list_of_objs)):
        linecost += addcost_v3(list_of_objs[0:i], list_of_objs[i])
    return linecost

def addcost_v3(list_of_objs, newobj):
        if (len(list_of_objs) == 0):
            return 50
        if newobj is None:
            return 0
        cx = (newobj.tlx + newobj.brx) / 2.0
        cy = (newobj.tly + newobj.bry) / 2.0
        minx, miny, maxx, maxy = VisualObject.bbox(list_of_objs)
        if miny <= cy and cy <= maxy:
            if minx <= newobj.brx and newobj.tlx <= maxx:
                xcost = 0
                ycost = 0
                print 'in box'
                return -100
            elif newobj.brx < minx:  # inline-left
                xcost = minx - newobj.brx
                ycost = abs((maxy + miny) / 2.0 - cy)
                print 'inline left', 'xcost', xcost, 'ycost', ycost 
            elif newobj.tlx > maxx:  # inline-right
                xcost = newobj.tlx - maxx
                ycost = abs((maxy + miny) / 2.0 - cy)
                print 'inline right', 'xcost', xcost, 'ycost', ycost
            else:
                print 'linebreak.addcost Error: inline, not in box, neither left nor right'
            return xcost + ycost*0.25 - 50
        else:  # above or below
            if newobj.tly > maxy:  # above
                ycost = newobj.tly - maxy
            elif newobj.bry < miny:  # below
                ycost = miny - newobj.bry
            else:
                ycost = 0 # negative overlap
                ycost = -(min(newobj.bry, maxy) - max(newobj.tly, miny))
            xcost = min(abs(maxx - newobj.brx), abs(maxx-newobj.tlx))
            print 'above or below', 'xcost', xcost, 'ycost', ycost
        return xcost + ycost


def line_badness(list_of_objs, optsec, fps):
    fgpixcount = 0
    for obj in list_of_objs:
        fgmask = pf.fgmask(obj.img)
        fgpixcount += np.count_nonzero(fgmask)
#         print 'fgpixcount = ', np.count_nonzero(fgmask)
#         util.showimages([obj.img, fgmask], "object and mask")
    if fgpixcount > 2000:
        return 0
    else:
        return (2000 - fgpixcount)

            
if __name__ == "__main__":
    videopath = sys.argv[1]
    scriptpath = sys.argv[2]
    objdir = sys.argv[3]
    panoramapath = sys.argv[4]
    panorama = cv2.imread(panoramapath)
    
    lec = Lecture(videopath, None)
    print lec.video.fps
    img_objs = VisualObject.objs_from_file(lec.video, objdir)
    breaker = LineBreaker(lec, img_objs, objdir, debug=False)
    line_objs, start_obj_idx, end_obj_idx = breaker.greedy_lines()
    html = WriteHtml(objdir + "/dynamic_linebreak_test_v5.html", title="Test line break v5", stylesheet="../Mainpage/summaries.css")
    html.opendiv(idstring="summary-container")
    breaker.write_to_html(html, objdir, list_of_objs=line_objs)
    html.closediv()
    html.closehtml()
    
    
