'''
Created on Jan 9, 2015

@author: hijungshin
'''

import numpy as np
from visualobjects import VisualObject
import util
import os



class Figure:
    def __init__(self, main_id, sub_id, list_of_subfigures, figuredir):
        self.main_id = main_id
        self.sub_id = sub_id
        self.list_of_newobjs = list_of_subfigures[-1]
        self.start_fid = self.list_of_newobjs[0].start_fid
        self.end_fid = self.list_of_newobjs[-1].end_fid
        self.figuredir = figuredir
        self.list_of_subfigures = list_of_subfigures        
        self.list_of_objs = []
        for subfigure in list_of_subfigures:
            self.list_of_objs = self.list_of_objs + subfigure
        self.newobjpath = self.highlight_new_objs().imgpath
        
        
    def all_objs(self):
        return VisualObject.group(self.list_of_objs, self.figuredir)
    
    def highlight_new_objs(self):
        list_of_objs = []
        """past objects in gray"""
        for i in range(0, len(self.list_of_subfigures)-1):
            subfigure_i = self.list_of_subfigures[i]
            for obj in subfigure_i:
                grayobj = obj.copy()
                grayobj.img = util.fg2gray(obj.img, 200)
#                 util.showimages([grayobj.img], "gray object")
                list_of_objs.append(grayobj)
        """new objects in color"""
        list_of_objs = list_of_objs + self.list_of_subfigures[-1]
        return VisualObject.group(list_of_objs, self.figuredir)
            
    @staticmethod
    def get_subfigures_in_line(list_of_objs, line_ids, n):
        list_of_subfigures = []
        subfigure = []
        for i in range(0, len(list_of_objs)):
            if line_ids[i] == n:
                subfigure.append(list_of_objs[i])
            elif len(subfigure) > 0:
                list_of_subfigures.append(subfigure)
                subfigure = []
        list_of_subfigures.append(subfigure)
        return list_of_subfigures

    def highlight_time(self, start_fid, end_fid):
        list_of_objs = []
        for obj in self.list_of_objs:
            if start_fid <= obj.start_fid and obj.end_fid <= end_fid:
                list_of_objs.append(obj)
            else:
                grayobj = obj.copy()
                grayobj.img = util.fg2gray(obj.img, 200)
                list_of_objs.append(grayobj)
        objname = os.path.basename(obj.imgpath) 
        basename = objname.split('.')[0]
        return VisualObject.group(list_of_objs, self.figuredir + "/highlight", imgname=basename + "_%06i_%06i.png"%(start_fid, end_fid))
    
    def highlight_objs(self, objs):
        list_of_objs = []
        for obj in self.list_of_objs:
            if obj in objs:
                list_of_objs.append(obj)
            else:
                grayobj = obj.copy()
                grayobj.img = util.fg2gray(obj.img, 200)
                list_of_objs.append(grayobj)
        objname = os.path.basename(obj.imgpath) 
        basename = objname.split('.')[0]
        if len(objs) == 0:
            return None
        else:
            start_fid = objs[0].start_fid
            end_fid = objs[-1].end_fid
            return VisualObject.group(list_of_objs, self.figuredir + "/highlight", imgname=basename + "_%06i_%06i.png"%(start_fid, end_fid))
                
    
            

    @staticmethod
    def getfigures(list_of_objs, line_ids, figuredir):
        
        list_of_figures = []
        num_figures = len(np.unique(np.array(line_ids)))
        subfigure_count = np.zeros(num_figures, dtype=np.uint8)
        num_objs = len(list_of_objs)
        
        line_ids.append(-1)        
        for i in range(0, num_objs):
            cur_id = line_ids[i]
            next_id = line_ids[i+1]
            if (cur_id != next_id):
                main_id = cur_id
                sub_id = subfigure_count[cur_id]
                list_of_subfigures = Figure.get_subfigures_in_line(list_of_objs[0:i+1], line_ids, cur_id)
#                 util.showimages([VisualObject.group(list_of_objs[0:i+1]).img])
                figure = Figure(main_id, sub_id, list_of_subfigures, figuredir)     
                list_of_figures.append(figure)
                subfigure_count[cur_id] += 1
                
        return list_of_figures