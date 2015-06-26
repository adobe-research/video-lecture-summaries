'''
Created on Mar 8, 2015

@author: hijungshin
'''

from visualobjects import VisualObject
from video import Video
import sys
import os
import util
import numpy as np
import process_aligned_json as pjson
from sentence import Sentence
import cv2
import label
from sublinebreak import SublineBreaker

class Character:
    def __init__(self, charobj):
        self.obj = charobj
        self.stroke = None

class Stroke:
    def __init__(self, strokeobj, video):
        self.obj = strokeobj
        self.video = video
        self.list_of_chars = []
        self.stcgroup = None

class StcStroke:
    def __init__(self, subline, list_of_strokes, stc_id, sentence, stcstrokedir):
        self.subline = subline
        self.list_of_strokes = list_of_strokes
        for stroke in list_of_strokes:
            stroke.stcgroup = self
        self.stc_id = stc_id
        self.stc = sentence
        if sentence is not None:
            sentence.stcstroke = self
        self.obj = VisualObject.group([stroke.obj for stroke in self.list_of_strokes], stcstrokedir, imgname = "sentence%06i.png"%(stc_id) )
        self.objdir = stcstrokedir
        
    def obj_upto_inline(self,figdir):
        linegroup = self.subline.linegroup
        sub_id = self.subline.sub_line_id
        list_of_objs = []
        for i in range(0, sub_id): #all previous sublines
            grayobj = linegroup.list_of_sublines[i].obj.copy()
            grayobj.img = util.fg2gray(grayobj.img, 175)
            list_of_objs.append(grayobj)
        for stcstroke in self.subline.list_of_stcstrokes:
            list_of_objs.append(stcstroke.obj)
            if stcstroke == self:
                break

        obj = VisualObject.group(list_of_objs, figdir, "line%i_upto_sub%i_stc%i.png"%(linegroup.line_id, sub_id, self.stc_id))
        return obj

    def obj_inline(self,figdir):
        linegroup = self.subline.linegroup
        sub_id = self.subline.sub_line_id
        list_of_objs = []
        for i in range(0, sub_id): #all previous sublines
            grayobj = linegroup.list_of_sublines[i].obj.copy()
            grayobj.img = util.fg2gray(grayobj.img, 175)
            list_of_objs.append(grayobj)
        for stcstroke in self.subline.list_of_stcstrokes:
            if stcstroke == self:
                list_of_objs.append(stcstroke.obj)
                break
            else:
                grayobj = stcstroke.obj.copy()
                grayobj.img = util.fg2gray(grayobj.img, 175)
                list_of_objs.append(grayobj)
        obj = VisualObject.group(list_of_objs, figdir, "line%i_upto_sub%i_stc%i.png"%(linegroup.line_id, sub_id, self.stc_id))
        return obj
    
    def obj_inline_range(self,figdir, id1, id2):
        linegroup = self.subline.linegroup
        sub_id = self.subline.sub_line_id
        list_of_objs = []
        for i in range(0, sub_id): #all previous sublines
            grayobj = linegroup.list_of_sublines[i].obj.copy()
            grayobj.img = util.fg2gray(grayobj.img, 175)
            list_of_objs.append(grayobj)
        for j in range(0, len(self.subline.list_of_sentences)):
            sentence = self.subline.list_of_sentences[j]
            if sentence.stcstroke is None:
                continue;
            stcstroke = sentence.stcstroke
            if id1 <= j and j <= id2:
                list_of_objs.append(stcstroke.obj)
            else:
                grayobj = stcstroke.obj.copy()
                grayobj.img = util.fg2gray(grayobj.img, 175)
                list_of_objs.append(grayobj)
            if stcstroke == self:
                break;
        obj = VisualObject.group(list_of_objs, figdir, "line%i_upto_sub%i_stc%i.png"%(linegroup.line_id, sub_id, self.stc_id))
        return obj
    
    
class SubLine:
    def __init__(self, list_of_strokes, line_id, sub_line_id, sublinedir):
        self.list_of_strokes = list_of_strokes
        self.line_id = line_id
        self.sub_line_id = sub_line_id     
        self.list_of_sentences = []   
        self.list_of_stcstrokes = []
        self.linegroup = None
        self.obj_in_line = None
        self.obj = VisualObject.group([stroke.obj for stroke in self.list_of_strokes], sublinedir, imgname = "line%06i_%06i.png" % (self.line_id, self.sub_line_id))
        self.objdir = sublinedir
        self.list_of_labels = []
        self.list_of_subsublines = []
        
    def add_label(self, pos):
        n = len(self.list_of_labels)
        lb = label.getlabels(len(self.list_of_labels), 1)
        lb[0].changepos(pos)
        self.list_of_labels.append(lb[0])
        return '[Figure %i - %i (%s)]' % (self.line_id+1, self.sub_line_id+1, chr(ord('a') +n))
        
        
    def link_stcstrokes(self, stcstrokedir):
        """link each stroke in self.list_of_strokes to one and only one of self.list_of_stcs"""
        n_stcs = len(self.list_of_sentences)
        if (n_stcs == 0):
            stcstroke = StcStroke(self, self.list_of_strokes, -1, None, stcstrokedir)
            self.list_of_stcstrokes.append(stcstroke)
            return
        
        closest_stc_ids = []
        for stroke in self.list_of_strokes:
            min_dist = float("inf")
            closest_stc_id = -1
            for i in range(0, n_stcs):
                stc = self.list_of_sentences[i]
                dist = VisualObject.obj_stc_distance(stroke.obj, stc.list_of_words, stc.video)
                if (dist < min_dist):
                    min_dist = dist
                    closest_stc_id = i
            closest_stc_ids.append(closest_stc_id)
            
        closest_stc_ids = np.array(closest_stc_ids)
        for i in range(0, n_stcs):
            stc = self.list_of_sentences[i]
            stroke_ids = np.where(closest_stc_ids == i)[0]
            if (len(stroke_ids) > 0):
                stc_list_of_strokes = [self.list_of_strokes[x] for x in stroke_ids]
                stcstroke = StcStroke(self, stc_list_of_strokes, stc.id, stc, stcstrokedir)
                self.list_of_stcstrokes.append(stcstroke)
                
        
    def link_linegroup(self, linegroup):
        self.linegroup = linegroup
        list_of_imgobjs = []
        for subline in linegroup.list_of_sublines:
            if subline == self:
                for stroke in subline.list_of_strokes:
                    list_of_imgobjs.append(stroke.obj)
            else:
                for stroke in subline.list_of_strokes:
                    grayobj = stroke.obj.copy()
                    grayobj.img = util.fg2gray(stroke.obj.img, 200)
                    list_of_imgobjs.append(grayobj)
        self.obj_in_line = VisualObject.group(list_of_imgobjs, self.objdir, imgname="inline%06i_%06i.png" % (self.line_id, self.sub_line_id))


class LineGroup:
    def __init__(self, list_of_sublines, line_id, linedir):
        self.list_of_sublines = list_of_sublines
        self.line_id = line_id
        self.linedir = linedir
        list_of_objs = []
        for i in range(0, len(list_of_sublines)):
            subline = list_of_sublines[i]
            subline.link_linegroup(self)
            for stroke in subline.list_of_strokes:
                list_of_objs.append(stroke.obj)
        self.obj = VisualObject.group(list_of_objs, self.linedir, imgname="line%06i.png" % (line_id))
        
    def obj_upto_subline(self, subline_id):
        list_of_objs = []
        for i in range(0, subline_id):
            grayobj = self.list_of_sublines[i].obj.copy()
            grayobj.img = util.fg2gray(grayobj.img, 175)
            list_of_objs.append(grayobj)
        list_of_objs.append(self.list_of_sublines[subline_id].obj)
        return list_of_objs
        
    
def link_char_strokes(list_of_chars, list_of_strokes):
    for char in list_of_chars:
        charname = os.path.basename(char.obj.imgpath)
        charname = os.path.splitext(charname)[0]
        for stroke in list_of_strokes:
            strokename = os.path.basename(stroke.obj.imgpath)
            strokename = os.path.splitext(strokename)[0]
            if strokename in charname:
                stroke.list_of_chars.append(char)
                char.stroke = stroke
                break
            
def get_strokes(video, objdir):
    list_of_strokeobjs = VisualObject.objs_from_file(video, objdir)
    list_of_strokes = []
    for obj in list_of_strokeobjs:
        list_of_strokes.append(Stroke(obj, video))
    return list_of_strokes

def get_chars(video, xcutdir):
    list_of_charobjs = VisualObject.objs_from_file(video, xcutdir)
    list_of_chars = []
    for charobj in list_of_charobjs:
        list_of_chars.append(Character(charobj))
    return list_of_chars

def get_sublines(list_of_strokes, linetxt, list_of_sentences, sublinedir, stcstrokesdir):
    line_ids = util.stringlist_from_txt(linetxt)
    line_ids = util.strings2ints(line_ids)
    n_lines = len(np.unique(np.array(line_ids)))
    line_ids.append(-1)
    
    list_of_sublines = []
    sub_ids = [0 for x in range(0, n_lines)]
    start_i = 0
    for i in range(0, len(list_of_strokes)):
        cur_lineid = line_ids[i]
        next_id = line_ids[i + 1]
        if (cur_lineid != next_id):
            sub_lineid = sub_ids[cur_lineid]
            subline = SubLine(list_of_strokes[start_i:i + 1], cur_lineid, sub_lineid, sublinedir)
            sub_ids[cur_lineid] += 1
            list_of_sublines.append(subline)
            start_i = i + 1
   
    link_stc_to_sublines(list_of_sentences, list_of_sublines)    
    for subline in list_of_sublines:
        subline.link_stcstrokes(stcstrokesdir)
                 
    return list_of_sublines

def link_stc_to_sublines(list_of_sentences, list_of_sublines):
    """sentence is associated with a subline, or none"""
    for subline in list_of_sublines:
        del subline.list_of_sentences[:]
    
    n_sublines = len(list_of_sublines)
    closest_subline_ids = []
    for stc in list_of_sentences:
        stc_length_fid = stc.video.ms2fid(stc.endt) - stc.video.ms2fid(stc.startt)
        closest_subline = None
        closest_id = -1
        min_dist = float("inf")
        for i in range(0, n_sublines):
            subline = list_of_sublines[i]
            dist = VisualObject.obj_stc_distance(subline.obj, stc.list_of_words, stc.video)
            if (dist < 0 and dist < min_dist):
                min_dist = dist
                closest_subline = list_of_sublines[i]
                closest_id = i
        closest_subline_ids.append(closest_id)
        stc.subline = closest_subline
        if (closest_subline is not None and abs(min_dist) >= 0.75*stc_length_fid):
            closest_subline.list_of_sentences.append(stc)    
    return closest_subline_ids

def get_linegroups(list_of_sublines, linetxt, linedir):
    line_ids = util.stringlist_from_txt(linetxt)
    line_ids = util.strings2ints(line_ids)
    numlines = len(np.unique(np.array(line_ids)))
    list_of_linegroups = []
    for i in range(0, numlines):
        sublines_i = []
        for subline in list_of_sublines:
            if subline.line_id == i:
                sublines_i.append(subline)
        line_i = LineGroup(sublines_i, i, linedir)
        list_of_linegroups.append(line_i)
    return list_of_linegroups

def draw(panorama, list_of_linegroups):
    panorama_copy = panorama.copy()
    for linegroup in list_of_linegroups:
        obj = linegroup.obj
        cv2.rectangle(panorama_copy, (obj.tlx, obj.tly), (obj.brx, obj.bry), (0, 0, 255), 1)
        for subline in linegroup.list_of_sublines:
            obj = subline.obj
            cv2.rectangle(panorama_copy, (obj.tlx, obj.tly), (obj.brx, obj.bry), (255, 0, 255), 1)
            for stcstroke in subline.list_of_stcstrokes:
                obj = stcstroke.obj
                cv2.rectangle(panorama_copy, (obj.tlx, obj.tly), (obj.brx, obj.bry), (255, 0, 0), 1)
                for stroke in stcstroke.list_of_strokes:
                    obj = stroke.obj
                    cv2.rectangle(panorama_copy, (obj.tlx, obj.tly), (obj.brx, obj.bry), (255, 255, 0), 1)
                    for char in stroke.list_of_chars:
                        obj = char.obj
                        cv2.rectangle(panorama_copy, (obj.tlx, obj.tly), (obj.brx, obj.bry), (0, 0, 0), 1)
    return panorama_copy


def getvisuals(videopath, panoramapath, objdir, scriptpath):
    video = Video(videopath)
    panorama = cv2.imread(panoramapath)
    """strokes"""
    list_of_strokes = get_strokes(video, objdir)
    
    """xcut characters"""
    xcutdir = objdir + "/xcut"
    list_of_chars = get_chars(video, xcutdir)
    link_char_strokes(list_of_chars, list_of_strokes)
    
    """sublines"""
    sublinedir = objdir + "/sublines_15_03_18"
    stcstrokesdir = objdir + "/stcstrokes_15_03_18"
    linetxt = objdir + "/linebreak_wo_area_compact_adjust_xgap_ids.txt"
    list_of_words = pjson.get_words(scriptpath)
    list_of_stcs = pjson.get_sentences(list_of_words)
    list_of_sentences = []
    stcid = 0
    for stc in list_of_stcs:
        list_of_sentences.append(Sentence(stc, video, stcid))
        stcid += 1
    
    list_of_sublines = get_sublines(list_of_strokes, linetxt, list_of_sentences, sublinedir, stcstrokesdir)
    
    """lines"""
    linedir = objdir + "/linegroups"
    list_of_linegroups = get_linegroups(list_of_sublines, linetxt, linedir)
    
    list_of_stcstrokes = []
    for subline in list_of_sublines:
        list_of_stcstrokes = list_of_stcstrokes + subline.list_of_stcstrokes
        
    """break sublines"""
    for subline in list_of_sublines:
        break_subline(subline, list_of_sentences)
   
    return [panorama, list_of_linegroups, list_of_sublines, list_of_stcstrokes, list_of_strokes, list_of_chars, list_of_sentences]
     
def panorama_lines(panorama, list_of_linegroups):
    panorama_copy = panorama.copy()
    for linegroup in list_of_linegroups:
        obj = linegroup.obj
        cv2.rectangle(panorama_copy, (obj.tlx, obj.tly), (obj.brx, obj.bry), (0, 0, 0), 2)
    return panorama_copy

def break_subline(subline, list_of_sentences):
    sb = SublineBreaker(subline, list_of_sentences)
    subline.list_of_subsublines = sb.breaklines()    
        
     
if __name__ == "__main__":
    videopath = sys.argv[1]
    panoramapath = sys.argv[2]
    objdir = sys.argv[3]
    scriptpath = sys.argv[4]
    
    video = Video(videopath)
    
    """strokes"""
    list_of_strokes = get_strokes(video, objdir)
    
    """xcut characters"""
    xcutdir = objdir + "/xcut"
    list_of_chars = get_chars(video, xcutdir)
    link_char_strokes(list_of_chars, list_of_strokes)
    
    """sublines"""
    linetxt = objdir + "/line_ids.txt"
    list_of_words = pjson.get_words(scriptpath)
    list_of_stcs = pjson.get_sentences(list_of_words)
    list_of_sentences = []
    stcid = 0
    for stc in list_of_stcs:
        list_of_sentences.append(Sentence(stc, video, stcid))
        stcid += 1
    
    sublinedir = objdir + "/sublines_15_03_18"
    stcstrokesdir = objdir + "/stcstrokes_15_03_18"
    if not os.path.exists(os.path.abspath(sublinedir)):
        os.makedirs(os.path.abspath(sublinedir))
    if not os.path.exists(os.path.abspath(stcstrokesdir)):
        os.makedirs(os.path.abspath(stcstrokesdir))

    list_of_sublines = get_sublines(list_of_strokes, linetxt, list_of_sentences, sublinedir, stcstrokesdir)
    VisualObject.write_to_file(sublinedir + "/obj_info.txt", [subline.obj for subline in list_of_sublines])

    list_of_stcstrokes = []
    for subline in list_of_sublines:
        list_of_stcstrokes = list_of_stcstrokes + subline.list_of_stcstrokes
    VisualObject.write_to_file(stcstrokesdir + "/obj_info.txt", [stcstroke.obj for stcstroke in list_of_stcstrokes])



    """lines and sublines_inline"""
    linedir = objdir + "/linegroups_15_03_18"
    if not os.path.exists(os.path.abspath(linedir)):
        os.makedirs(os.path.abspath(linedir))

    list_of_linegroups = get_linegroups(list_of_sublines, linetxt, linedir)
    
    """break sublines"""
    for subline in list_of_sublines:
        break_subline(subline, list_of_sentences)
    
    
    VisualObject.write_to_file(linedir + "/obj_info.txt", [line.obj for line in list_of_linegroups])
    VisualObject.write_to_file(sublinedir + "/inline_obj_info.txt", [subline.obj_in_line for subline in list_of_sublines])
    
    

            
                
    
        
            
        
        
        
        
