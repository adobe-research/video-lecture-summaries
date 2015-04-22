'''
Created on Apr 21, 2015

@author: Valentina
'''

import numpy as np
import math
from visualobjects import VisualObject

class SublineBreaker:
    def __init__(self, subline, list_of_sentences):
        self.subline = subline
        self.list_of_stcstrokes = subline.list_of_stcstrokes
        self.list_of_sentences = list_of_sentences
        self.nobjs = len(subline.list_of_stcstrokes)
        self.nstcs = len(subline.list_of_sentences)
        self.linecost =  [[0 for x in range(self.nobjs)] for x in range(self.nobjs)]
        self.totalcost = [float("inf") for x in range(self.nobjs)]
        self.cuts = [-1 for x in range(self.nobjs)]
        self.best_line_id = [[-1 for x in range(self.nobjs)] for x in range(self.nobjs)]
        
    def breaklines(self):
        if (self.nstcs <= 3):
            return [self.subline.list_of_strokes]
        self.compute_totalcost()
        sub_sublines = self.getcutlines(self.nobjs-1)
        return sub_sublines    
    
    def compute_totalcost(self):
        self.totalcost[0] = avg_linecost([self.list_of_stcstrokes[0:1]], self.list_of_sentences)
        self.cuts[0] = -1
        self.best_line_id[0][0] = 0
        
        for i in range(1, self.nobjs):
            self.totalcost[i] = float("inf")
            for j in range(-1, i):
                newline = self.list_of_stcstrokes[j+1:i+1]
                if j == -1:
                    """single segment"""
                    cost_from_cut_j = avg_linecost([newline], self.list_of_sentences)
                    if (cost_from_cut_j < self.totalcost[i]):
                        self.totalcost[i] = cost_from_cut_j
                        self.cuts[i] = j
                        for k in range(0, i+1):
                            self.best_line_id[i][k] = 0
                else:
                    """get best segment up to stcstroke j"""
                    prevlines = self.getcutlines(j)
                    """cost to merge newline and prevline"""
                    lastline = prevlines[-1]
                    mergedline = lastline + newline
                    templines = prevlines[:]
                    templines[-1] = mergedline
                    cost_from_cut_j = avg_linecost(templines, self.list_of_sentences)
                    if (cost_from_cut_j < self.totalcost[i]):
                        self.totalcost[i] = cost_from_cut_j
                        self.cuts[i] = j
                        self.best_line_id[i][0:j+1] = self.best_line_id[j][0:j+1]
                        for k in range(j+1, i+1):
                            self.best_line_id[i][k] = len(prevlines) -1
                    
                    """cost to separate newline"""
                    templines = prevlines[:]
                    templines.append(newline)
                    cost_from_cut_j = avg_linecost(templines, self.list_of_sentences)
                    if (cost_from_cut_j < self.totalcost[i]):
                        self.totalcost[i] = cost_from_cut_j
                        self.cuts[i] = j
                        self.best_line_id[i][0:j+1] = self.best_line_id[j][0:j+1]
                        for k in range(j+1, i+1):
                            self.best_line_id[i][k] = len(prevlines) 
        
        
    def getcutlines(self, index):
        line_ids = self.best_line_id[index][0:index+1]
        nlines = len(np.unique(line_ids))
        bestlines = [[] for x in range(0, nlines)]
        i = 0
        for stcstroke in self.list_of_stcstrokes[0:index+1]:
            bestlines[line_ids[i]].append(stcstroke)
            i += 1
        return bestlines
    
def avg_linecost(list_of_lines, list_of_sentences):
    nlines= len(list_of_lines)
    nword_score = 0.0
    nstc_score = 0.0
    for list_of_stcstrokes in list_of_lines:
        stcids = [stcstroke.stc_id for stcstroke in list_of_stcstrokes]
        stcids = np.unique(stcids)
        nstc = len(stcids)
        if nstc < 3:
            nstc_score += abs(nstc-3)
        else:
            nstc_score += 2*abs(nstc-3)
        nwords = 0
        for i in stcids:
            stc = list_of_sentences[i]
            nwords += len(stc.list_of_words)
        if nwords < 50:
            nword_score += abs(nwords-50)/50.0
        else:
            nword_score += 2*abs(nwords-50)/50.0
        
        
#         nword_score += abs(nwords-75)/25.0
#     nword_score /= nlines    
    nstc_score /= nlines
        
    overlap_penalty = 0.0
    for i in range(0, nlines):
        curline = list_of_lines[i]
        curline_objs = [stcstroke.obj for stcstroke in curline]
        for j in range(i+1, len(list_of_lines)):
            nextline = list_of_lines[j]
            nextline_objs = [stcstroke.obj for stcstroke in nextline]
            overlap = VisualObject.overlap_list(curline_objs, nextline_objs)
            overlap_penalty += overlap
            
    time_gap_penalty = 0.0
    for i in range(0, nlines-1):
        curline = list_of_lines[i]
        nextline = list_of_lines[i+1]
        cur_endstroke = curline[-1].list_of_strokes[-1]
        cur_endt = cur_endstroke.video.fid2ms(cur_endstroke.obj.end_fid)
        next_startstroke = nextline[0].list_of_strokes[0]
        next_startt = next_startstroke.video.fid2ms(next_startstroke.obj.start_fid)
        tgap = (next_startt - cur_endt)/1000.0
        time_gap_penalty += 1.0/tgap
    
    score = nword_score + overlap_penalty #+ time_gap_penalty
    
    return score 
        
            
            