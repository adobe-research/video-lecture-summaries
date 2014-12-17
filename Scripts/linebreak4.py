'''
Created on Dec 12, 2014

@author: hijungshin
A greedy approach based on ygap_distance
'''
import sys
from visualobjects import VisualObject
import util
import cv2

class Line:
    def __init__(self):
        self.list_of_objs = []
        self.miny = float("inf")
        self.maxy = -1.0 * float("inf")
        self.minx = float("inf")
        self.maxx = -1.0 * float("inf")
        
    def insertobject(self, obj):
        self.list_of_objs.append(obj)
        self.miny = min(self.miny, obj.tly)
        self.maxy = max(self.maxy, obj.bry)      
        self.minx = min(self.minx, obj.tlx)
        self.maxx = max(self.maxx, obj.brx)

    def ygap_distance(self, obj):
        tlx, tly, brx, bry = VisualObject.bbox(self.list_of_objs)
        line_ctry = tly + (bry + 1 - tly) / 2.0
        obj_ctry = obj.tly + (obj.bry + 1 - obj.tly) / 2.0
        line_h = (bry + 1 - tly)
        obj_h = (obj.bry + 1 - obj.tly)
        y_dist = abs(obj_ctry - line_ctry) - (obj_h/2.0 + line_h/2.0)
        return y_dist/(obj_h)
        
    
    def xgap_distance(self, obj):
        tlx, tly, brx, bry = VisualObject.bbox(self.list_of_objs)
        line_ctrx = tlx + (brx + 1 - tlx) / 2.0
        obj_ctrx = obj.tlx + (obj.brx + 1 - obj.tlx) / 2.0
        line_w = (brx + 1 - tlx)
        obj_w = (obj.brx + 1 - obj.tlx)
        x_dist = abs(obj_ctrx - line_ctrx) - (obj_w/2.0 + line_w/2.0)
        return x_dist/(obj_w)
    
def continued_line(line, obj):
    # object is in-line:
    (left_right, xdist) = VisualObject.xgap_distance_list(line.list_of_objs, [obj])
    ydist = VisualObject.ygap_distance_list(line.list_of_objs, [obj])
    print 'xdist', xdist, 'ydist', ydist, 'abs(line.maxx - obj.brx)', abs(line.maxx-obj.brx)
    if (ydist <= 10 and xdist <= 100):
        return True
#     if (ydist <= 15 and 0 <= xdist and xdist <= 15):
#         return True
#     if (ydist <= 30 and xdist >= -100 and xdist <= 100):
#         return True
    return False

def continued_line2(line, obj):
        # object is in-line:
    (left_right, xdist) = VisualObject.xgap_distance_list(line.list_of_objs, [obj])
    ydist = VisualObject.ygap_distance_list(line.list_of_objs, [obj])
#     print 'xdist', xdist, 'ydist', ydist
    if (ydist <= 5 and xdist <= 200):
        return True
    return False
                
if __name__ == "__main__":
    objdirpath = sys.argv[3]
    list_of_objs = VisualObject.objs_from_file(None, objdirpath)
    panoramapath = sys.argv[4]
    panorama = cv2.imread(panoramapath)
    
    lines = []
    line = Line()
    line.insertobject(list_of_objs[0])
    lines.append(line)
    imprev = None
    for i in range(1, len(list_of_objs)):
        panorama_copy = panorama.copy()
        obj = list_of_objs[i]
        cv2.rectangle(panorama_copy, (obj.tlx, obj.tly), (obj.brx, obj.bry), (255, 0, 0), 3)
        minx, miny, maxx, maxy = VisualObject.bbox(line.list_of_objs)
        xdist = VisualObject.xgap_distance_list(line.list_of_objs, [obj])
        ydist = VisualObject.ygap_distance_list(line.list_of_objs, [obj])
        xwrapdist = maxx - obj.tlx
        lineh = maxy - miny
#         print 'xdist=', xdist, ' ydist=', ydist, 'xwrapdist', xwrapdist
        
        # default: continuing current line:
        if (continued_line(line, obj)):
            line.insertobject(obj)
            inserted = True
        else: 
            #if overlap with prevline, merge
            prevline_idx = 0
            inserted = False
            for prevline in lines:
                ydist = VisualObject.ygap_distance_list(prevline.list_of_objs, [obj])
                temp, xdist = VisualObject.xgap_distance_list(prevline.list_of_objs, [obj])
                prevlineh = prevline.maxy - prevline.miny
                if (ydist/prevlineh < 0 and xdist < 0):
#                     print 'xdist', xdist, 'ydist', ydist/prevlineh
#                     print 'overlap with previous line', prevline_idx
                    prevline.insertobject(obj)
                    line = prevline
                    inserted = True
                    break
#                 if (imprev is not None):
#                     cv2.rectangle(panorama_copy, (obj.tlx, obj.tly), (obj.brx, obj.bry), (0,0,255), 3)
#                     cv2.rectangle(panorama_copy, (imprev.minx, imprev.miny), (imprev.maxx, imprev.maxy), (255, 0, 0), 3)
#                     util.showimages([panorama_copy], "imprev")
        if not inserted:
#             print 'separte line'
            line = Line()
            line.insertobject(obj)
            lines.append(line)
        
        imprev = line
       
        for prevline in lines:
            tlx, tly, brx, bry = VisualObject.bbox(prevline.list_of_objs)
            cv2.rectangle(panorama_copy, (tlx, tly), (brx, bry), (0, 255, 0), 1)
        tlx, tly, brx, bry = VisualObject.bbox(line.list_of_objs)
        cv2.rectangle(panorama_copy, (tlx, tly), (brx, bry), (0, 0, 255), 1)
        for obj in line.list_of_objs:
            cv2.rectangle(panorama_copy, (obj.tlx, obj.tly), (obj.brx, obj.bry), (0, 0, 255), 1)
        util.showimages([panorama_copy])    

    # merge largely overlapping lines
    merged = True
    while(merged):
        merged = False
        for i in range(0, len(lines)):
            line1 = lines[i]
            for j in range(i+1, len(lines)):
                line2 = lines[j]
                overlap = VisualObject.overlap_list(line1.list_of_objs, line2.list_of_objs)
                if (overlap > 0.40):
                    for k in range(0, len(line2.list_of_objs)):
                        line1.insertobject(line2.list_of_objs[k])
                    lines.pop(j)
                    merged = True
                    break
            if (merged):
                break
            
#     
#     for i in range(0, len(lines)):
#             line1 = lines[i]
#             area = (line1.maxx - line1.minx) * (line1.maxy - line1.miny)
#             if (area > 15000):
#                 continue
#             for j in range(0, len(lines)):
#                 if (i == j):
#                     continue
#                 line2 = lines[j]
#                 y_dist = abs((line1.maxy +line1.miny)/2.0 - (line2.maxy + line2.miny) / 2.0)
# #                 y_dist = VisualObject.ygap_distance_list(line1.list_of_objs, line2.list_of_objs)
# #                 y_dist = y_dist/min((line1.maxy - line1.miny), (line2.maxy - line2.miny))
#                 temp, x_dist = VisualObject.xgap_distance_list(line1.list_of_objs, line2.list_of_objs)
#                 print 'ydist', y_dist, 'xdist', x_dist
#                 if (y_dist <20 and x_dist <= 50 ):
#                     print 'i = ', i, 'j=', j
#                     for k in range(0, len(line2.list_of_objs)):
#                         print 'here'
#                         line1.insertobject(line2.list_of_objs[k])
#                     lines.pop(j)
#                     print 'merged!!!'
#                     merged = True
#                     break
#             if (merged):
#                 break
    
    
    
    for i in range(0, len(lines)):
        line = lines[i]
        tlx, tly, brx, bry = VisualObject.bbox(line.list_of_objs)
        area = (line.maxx - line.minx) * (line.maxy - line.miny)
        if (area < 5000):
            cv2.rectangle(panorama, (tlx, tly), (brx, bry), (0, 0, 255), 1)
        else:
            cv2.rectangle(panorama, (tlx, tly), (brx, bry), (0, 255, 0), 1)

#     for i in range(0, len(lines)):
#         line = lines[i]
#         tlx, tly, brx, bry = VisualObject.bbox(line.list_of_objs)
#         area = (line.maxx - line.minx) * (line.maxy - line.miny)
#         if (area < 15000):
#             cv2.rectangle(panorama, (tlx, tly), (brx, bry), (0, 0, 255), 1)
#             for j in range(0, len(lines)):
#                 if i==j:
#                     continue
#                 otherline = lines[j]
#                 y_dist = VisualObject.ygap_distance_list(line.list_of_objs, otherline.list_of_objs)
#                 tlx, tly, brx, bry = VisualObject.bbox(otherline.list_of_objs)
#                     
#                 if (y_dist < -0.5):
# #                     tlx, tly, brx, bry = VisualObject.bbox(otherline.list_of_objs)
#                     cv2.rectangle(panorama, (tlx, tly), (brx, bry), (255, 0, 0), 1)
#                 else:
#                     cv2.rectangle(panorama, (tlx, tly), (brx, bry), (0, 255, 0), 1)
# 
#                     
        util.saveimage(panorama, objdirpath, "temp_lines.png")
                
        
                