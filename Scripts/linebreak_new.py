'''
Created on Dec 17, 2014

@author: hijungshin
'''
from visualobjects import VisualObject
import sys
import util
import cv2

ydist_thres = 10
xdist_thres = 100

class Line:
    def __init__(self):
        self.list_of_objs = []
        self.miny = float("inf")
        self.maxy = -1.0 * float("inf")
        self.minx = float("inf")
        self.maxx = -1.0 * float("inf")
        self.numobjs = 0
            
    def insertobject(self, obj):
        self.list_of_objs.append(obj)
        self.miny = min(self.miny, obj.tly)
        self.maxy = max(self.maxy, obj.bry)      
        self.minx = min(self.minx, obj.tlx)
        self.maxx = max(self.maxx, obj.brx)
        self.numobjs += 1
        
class LineBreaker:
    def __init__(self):
        self.list_of_lines = []
        
    def insertline(self, line):
        self.list_of_lines.append(line)
        
    def merge_overlap(self):
        merged = True
        while(merged):
            merged = False
            for i in range(0, len(self.list_of_lines)):
                line1 = self.list_of_lines[i]
                for j in range(i+1, len(self.list_of_lines)):
                    line2 = self.list_of_lines[j]
                    overlap = VisualObject.overlap_list(line1.list_of_objs, line2.list_of_objs)
                    if (overlap > 0.50):
                        for k in range(0, len(line2.list_of_objs)):
                            line1.insertobject(line2.list_of_objs[k])
                        self.list_of_lines.pop(j)
                        merged = True
                        break
                if (merged):
                    break
        
        
    def breakline(self, list_of_objs, panorama):
        if (len(list_of_objs) == 0): 
            return
        """insert first object"""
        curline = Line()
        curline.insertobject(list_of_objs[0])
        
        for i in range(1, len(list_of_objs)):
            obj = list_of_objs[i]
            inserted = False
            ydist = VisualObject.ygap_distance_list(curline.list_of_objs, [obj])
            (temp, xdist) = VisualObject.xgap_distance_list(curline.list_of_objs, [obj])
            print 'ydist, xdist', ydist, xdist
            """continue on current line"""
            if (continue_line(curline, obj)):
                print 'continue current line'
                curline.insertobject(obj)
                inserted = True
                    
            """annotate previous line"""          
            if not inserted:
                for j in range(1, len(self.list_of_lines)+1):
                    """search from most recent line"""
                    prev_idx = len(self.list_of_lines) - j
                    prevline = self.list_of_lines[prev_idx]
                    if annotate_line(prevline, obj):
                        self.insertline(curline)
                        curline = self.list_of_lines.pop(prev_idx)
                        curline.insertobject(obj)
                        inserted = True
                        print 'annotated previous line'
                        break
                    
            """check immediately previous line"""
            if (not inserted and len(self.list_of_lines) > 0):
                imprev = self.list_of_lines[-1]
                
                """debugging"""
                panorama_copy = panorama.copy()
                tlx, tly, brx, bry = VisualObject.bbox(imprev.list_of_objs)
                cv2.rectangle(panorama_copy, (tlx, tly), (brx, bry), (255, 0, 0), 1)
                cv2.rectangle(panorama_copy, (obj.tlx, obj.tly), (obj.brx, obj.bry), (0, 0, 255), 1)
#                 util.showimages([panorama_copy], "check immediately previous line")
                
                if (continue_line(imprev, obj)):
                    print 'continue immediately previous line'
                    self.insertline(curline)
                    curline = self.list_of_lines.pop(-2)
                    curline.insertobject(obj) 
                    inserted = True
                    
            """start separate line"""
            if not inserted:   
                print 'started separte line'
                self.insertline(curline)
                curline = Line()
                curline.insertobject(obj)
                
            """debugging"""
            panorama_copy = panorama.copy()
            for line in self.list_of_lines:
                tlx, tly, brx, bry = VisualObject.bbox(line.list_of_objs)
                cv2.rectangle(panorama_copy, (tlx, tly), (brx, bry), (0, 255, 0), 1)
            tlx, tly, brx, bry = VisualObject.bbox(curline.list_of_objs)
            cv2.rectangle(panorama_copy, (tlx, tly), (brx, bry), (0,0,255),1)
            for obj in curline.list_of_objs:
                cv2.rectangle(panorama_copy, (obj.tlx, obj.tly), (obj.brx, obj.bry), (0, 0, 255), 1)
            cv2.rectangle(panorama_copy, (obj.tlx, obj.tly), (obj.brx, obj.bry), (255, 0, 255), 2)
#             util.showimages([panorama_copy], "current state")
            
        self.insertline(curline)
                

        
def continue_line(line, obj):
    ydist = VisualObject.ygap_distance_list(line.list_of_objs, [obj])
    (temp, xdist) = VisualObject.xgap_distance_list(line.list_of_objs, [obj])
    if (ydist <= ydist_thres and xdist <= xdist_thres):
        return True
    return False

def annotate_line(line, obj):
    ydist = VisualObject.ygap_distance_list(line.list_of_objs, [obj])
    (temp, xdist) = VisualObject.xgap_distance_list(line.list_of_objs, [obj])
    if (ydist <= 0 and xdist <= -obj.width/2.0):
        return True, 
    return False

if __name__ == "__main__":
    objdir = sys.argv[3]
    list_of_objs = VisualObject.objs_from_file(None, objdir)
    panoramapath = sys.argv[4]
    panorama = cv2.imread(panoramapath)
    
    breaker = LineBreaker()
    breaker.breakline(list_of_objs, panorama)
    breaker.merge_overlap()
    
    for i in range(0, len(breaker.list_of_lines)):
        line = breaker.list_of_lines[i]
        tlx, tly, brx, bry = VisualObject.bbox(line.list_of_objs)
        area = (line.maxx - line.minx) * (line.maxy - line.miny)
        if (area < 5000):
            cv2.rectangle(panorama, (tlx, tly), (brx, bry), (0, 0, 255), 1)
        else:
            cv2.rectangle(panorama, (tlx, tly), (brx, bry), (0, 255, 0), 1)
    

    util.saveimage(panorama, objdir, "linebreak_new.png")


    
    
        
        