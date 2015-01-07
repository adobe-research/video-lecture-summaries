'''
Created on Dec 18, 2014

@author: hijungshin
'''
from visualobjects import *

class LineBreaker:
    def __init__(self, list_of_objs, panorama, outvideo=None):
        self.list_of_lines = []
        self.list_of_objs = list_of_objs
        self.panorama = panorama
        self.nobjs = len(list_of_objs)
        # linecost[i][j]: cost of a line which has strokes [i to j] 
        self.linecost = [[0 for x in range(self.nobjs)] for x in range(self.nobjs)]
        # totalcost[i]: total cost of optimal arrangement of words from 0 to i
        self.totalcost = [float("inf") for x in range(self.nobjs)]
        self.cuts = [-1 for x in range(self.nobjs)]
        self.best_line_id = [[-1 for x in range(self.nobjs)] for x in range(self.nobjs)]
        self.outvideo = outvideo
        

    
    def compute_linecost(self):
        for i in range(0, self.nobjs):
            for j in range(i, self.nobjs):
                self.linecost[i][j] = LineBreaker.getlinecost(self.list_of_objs[i:j+1])
                print 'self.linecost[',i,'][',j,']=', self.linecost[i][j]
                panorama = self.panorama.copy()
                visualize_line(panorama, list_of_objs[i:j+1])
                util.showimages([panorama])
    
    def compute_totalcost(self):
#         cv2.imshow("current state", self.panorama)
#         cv2.waitKey(0)
        self.totalcost[0] = weighted_avg_linecost([self.list_of_objs[0:1]])
        self.cuts[0] = -1
        self.best_line_id[0][0] = 0
        myresult  = self.panorama.copy()
        self.visualize_current_state(myresult,0)
                
        for i in range(1, self.nobjs): #deciding best cut up to stroke i
            curline_idx = self.best_line_id[i-1][i-1]
            print '========================best cut up to object', i,'================================'
            self.totalcost[i] = float("inf")
            for j in range(-1, i):
                print 'j = ', j
                newline = self.list_of_objs[j+1:i+1]
                panorama_copy = self.panorama.copy()
                if j == -1:
                    """single segment"""
                    cost_from_cut_j = weighted_avg_linecost([newline]) 
                    if (cost_from_cut_j < self.totalcost[i]):
                        self.totalcost[i] = cost_from_cut_j
                        self.cuts[i] = j
                        for k in range(0, i+1):
                            self.best_line_id[i][k] = 0
                        print "All strokes in single segment cost: ", self.totalcost[i]
#                         self.visualize_current_state(panorama_copy, i)                    
                else:
                    """get best segmentation up to stroke j"""
                    prevlines = []
                    prevlines = self.getcutlines(j)
                    line_idx = self.best_line_id[j][0:j+1]
                    numprevlines = len(prevlines)
                    """cost to merge newline and prevline"""
                    merged = False
                    merged_to_line = -1
                    for prevline_idx in range(0, numprevlines):
                        new_line_idx = [prevline_idx for objid in range(0, len(newline))]
                        prevline = prevlines[prevline_idx]
                        mergedline = prevline + newline
                        templines = prevlines[:]
                        templines[prevline_idx] = mergedline
                       
                        bpenalty = break_penalty(list_of_objs[0:i+1], line_idx + new_line_idx)
                        cost_from_cut_j = weighted_avg_linecost(templines)
                        cost_from_cut_j += bpenalty

                        if (cost_from_cut_j < self.totalcost[i]):
                            merged = True
                            merged_to_line = prevline_idx
                            self.totalcost[i] = cost_from_cut_j
                            self.cuts[i] = j
                            self.best_line_id[i][0:j+1] = self.best_line_id[j][0:j+1]
                            for k in range(j+1, i+1):
                                self.best_line_id[i][k] = prevline_idx    
                                
                    if (merged):
                        print "merged to line", merged_to_line, 'cost', self.totalcost[i], 'result:', self.best_line_id[i]         
                            
                    """cost to separate newline"""
                    templines = self.getcutlines(j)
                    templines.append(newline)
                    new_line_idx = [len(prevlines) for objid in range(0, len(newline))]
                    bpenalty = break_penalty(list_of_objs[0:i+1], line_idx + new_line_idx)
                    cost_from_cut_j = weighted_avg_linecost(templines)
                    cost_from_cut_j += bpenalty
                    
                    print 'cost to separate newline', cost_from_cut_j
                    if (cost_from_cut_j < self.totalcost[i]):
                        self.totalcost[i] = cost_from_cut_j
                        self.cuts[i] = j
                        self.best_line_id[i][0:j+1] = self.best_line_id[j][0:j+1]
                        for k in range(j+1, i+1):
                            self.best_line_id[i][k] = len(prevlines) 
                        print 'separating line at j =', j, 'cost', cost_from_cut_j, 'result:', self.best_line_id[i]
            panorama_copy = self.panorama.copy()
            self.visualize_current_state(panorama_copy, i)
                           
    def getcutlines(self, index):
        line_ids = self.best_line_id[index][0:index+1]
        print 'best line_ids up to stroke', index, ":", line_ids
        nlines = len(np.unique(line_ids))
        mylines = [[] for x in range(0, nlines)]
        objid = 0
        for obj in self.list_of_objs[0:index+1]:
            mylines[line_ids[objid]].append(obj)
            objid += 1
        return mylines
 
        
    def breaklines(self):
#         self.compute_linecost()
        self.compute_totalcost()
        self.lines = []
        self.lines = self.getcutlines(self.nobjs-1)
        return self.lines
    
    def visualize_current_state(self, panorama, index, outvideo=None):
        lines = self.getcutlines(index)
        visualize_lines(panorama, lines)
        print 'current segmentation', self.best_line_id[index][0:index + 1]
        print 'total cost', self.totalcost[index]
        cv2.imshow("current state", panorama)        
        cv2.waitKey(1)
        if self.outvideo is not None:
            self.outvideo.write(panorama)            
        
    @staticmethod
    def getlinecost(list_of_objs):
        if (len(list_of_objs) == 0):
            return 0
        yprojcost = y_projection_score(list_of_objs)
        if (yprojcost <= 5.0):
            yprojcost = math.pow(yprojcost, 1.05)
        else:
            yprojcost = math.pow(5.0, 1.05) + math.pow(yprojcost - 5.0, 0.95)
        yprojcost = 0.1*yprojcost    
         
        yprojgapcost = y_projection_gap_score(list_of_objs)
        yprojgapcost = 0.025 * yprojgapcost
        yprojgapcost = math.pow(yprojgapcost, 2.0)
        
        strokecost = len(list_of_objs) 
        strokecost = math.pow(strokecost, 1.1)
        strokecost = 0.1 *strokecost
        
        xprojcost =  x_projection_score(list_of_objs) # maxgap
        xprojcost = xprojcost * 0.01
        xprojcost = math.pow(xprojcost, 2.0)
        xprojcost = 0.2 * xprojcost
        
        compactcost = bbox_fill_ratio(list_of_objs)
        compactcost = 0.5*math.pow(compactcost, 1.3)
        
        cost = -1.0 * (yprojcost + strokecost - yprojgapcost - xprojcost + compactcost)
#         print 'yprojcost', yprojcost, 'strokecost', strokecost, 'yprojgap', yprojgapcost, 'xprojcost', xprojcost, 'compactcost', compactcost, 'cost', cost
        return cost
               
def weighted_avg_linecost(list_of_lines):
    idx = 0
    sum_yprojcost = 0.0
    sum_yprojgapcost = 0.0
    sum_xprojcost = 0.0
    sum_compactcost = 0.0
    sum_numfgpixel = 0.0
    sum_strokecost = 0.0
    for line in list_of_lines:
        numfgpixel = VisualObject.fgpixel_count(line) #len(line)
        print 'numfgpixel', numfgpixel
    
        yprojcost = y_projection_score(line)
        yinline = yprojcost
        if (yprojcost <= 5.0):
            yprojcost = math.pow(yprojcost, 1.05)
        else:
            yprojcost = math.pow(5.0, 1.05) + math.pow(yprojcost - 5.0, 0.95)
        yprojcost = 0.1*yprojcost    
        sum_yprojcost += yprojcost
         
        yprojgapcost = y_projection_gap_score(line)
        ymaxgap = yprojgapcost
        yprojgapcost = 0.025 * yprojgapcost
        yprojgapcost = math.pow(yprojgapcost, 2.0)
        sum_yprojgapcost += yprojgapcost
        
        strokecost = numfgpixel
        strokecost = (numfgpixel - 1.0/numfgpixel)
        strokecost = 0.001 * strokecost
        sum_strokecost += strokecost
        
        xprojcost =  x_projection_score(line) 
        maxgap = xprojcost
        xprojcost = 0.01 * xprojcost
        xprojcost = math.pow(xprojcost, 2.0)
        xprojcost = 0.2 * xprojcost
        sum_xprojcost += xprojcost
        
        compactcost = bbox_fill_ratio(line)
        compact = compactcost
        compactcost = math.pow(compactcost, 0.5)
        sum_compactcost = sum_compactcost + (numfgpixel * compactcost)
        
        sum_numfgpixel += numfgpixel
        print 'yinline', yinline, 'yproj', yprojcost, 'ymaxgap', ymaxgap, 'strokecost', strokecost, 'xproj', xprojcost, 'compact', compact, 'compactcost', compactcost, 'maxgap', maxgap
        idx += 1
        
#     sum_num_strokes = 0.0
    overlap_penalty = 0.0
    for i in range(0, len(list_of_lines)):
        curline = list_of_lines[i]
        for j in range(i+1, len(list_of_lines)):
            nextline = list_of_lines[j]
            overlap = VisualObject.overlap_list(curline, nextline)
            overlap_penalty += overlap
        
    avg_compactcost = sum_compactcost/sum_numfgpixel
    print 'total yprojcost', sum_yprojcost, 'sumstrokecost', sum_strokecost, 'sum_yprojgap', sum_yprojgapcost, 'sum xprojcost', sum_xprojcost, 'avg compactcost', avg_compactcost, 'overlap_penalty', overlap_penalty
    sum_cost = -1.0 * (sum_yprojcost + sum_strokecost - sum_yprojgapcost - sum_xprojcost + avg_compactcost - overlap_penalty)
    return sum_cost

def break_penalty(list_of_objs, line_ids):
    break_penalty = 0.0
    for i in range(0, len(line_ids) -1):
        if line_ids[i] != line_ids[i+1]:
            obj1 = list_of_objs[i]
            obj2 = list_of_objs[i+1]
            xdist, ydist, tdist = VisualObject.break_penalty(obj1, obj2)
            break_penalty += 1.0/tdist
    return break_penalty
        
    
def visualize_line(panorama, list_of_objs, color=(0,255,0)):
    if len(list_of_objs) == 0:
        return
    tlx, tly, brx, bry = VisualObject.bbox(list_of_objs)
    cv2.rectangle(panorama, (tlx, tly), (brx, bry), color, 2)
    for obj in list_of_objs:
        cv2.rectangle(panorama, (obj.tlx, obj.tly), (obj.brx, obj.bry), (0,0,255), 1)
 
def visualize_lines(panorama, lines):
    for line in lines:
        visualize_line(panorama, line)
    return panorama

def visualize_obj(panorama, list_of_obj, color=(255,0,255), width=1):
    tlx, tly, brx, bry = VisualObject.bbox(list_of_obj)
    cv2.rectangle(panorama, (tlx, tly), (brx, bry), color, width)

def is_annotation(prev_objs, new_objs):
    overlap = VisualObject.overlap_list(prev_objs, new_objs)
    if (overlap > 0.5):
        return True
    return False

def bbox_fill_ratio(list_of_objs):
    if len(list_of_objs) == 0:
        return 0
    tlx, tly, brx, bry = VisualObject.bbox(list_of_objs)
    if len(list_of_objs) == 1:
        return 1.0
#         return min(0.5, (brx - tlx + 1.0) * (bry - tly + 1.0) / 25000.0)
    total_area = (bry - tly + 1.0) * (brx - tlx + 1.0)
    sum_area = 0.0
    for obj in list_of_objs:
        sum_area += (obj.bry - obj.tly + 1.0) * (obj.brx - obj.tlx + 1.0)
    return sum_area/total_area

def inline_score(list_of_objs):
    sumcost = 0.0
    if (len(list_of_objs) <= 1):
        return 0
    for i in range(1, len(list_of_objs)):
        curobj = list_of_objs[i]
        templine = list_of_objs[0:i]
        _is_inline = VisualObject.inline(templine, curobj)
        if (_is_inline >= 0):
            sumcost += 1.5 * _is_inline
        else:
            sumcost += 15.0 * _is_inline
    return sumcost

def y_projection_score(list_of_objs):
    if (len(list_of_objs) == 0):
        return 0
    """get maxy from projection function"""
    tlx, tly, brx, bry = VisualObject.bbox(list_of_objs)
#     print 'area = ', (brx - tlx + 1.0) * (bry - tly + 1.0)
    yproj = VisualObject.y_projection_function(list_of_objs)
    maxy = yproj.argmax() + tly
    in_maxy = 0
    not_in_maxy = 0
    in_maxy_objs = []
    not_in_maxy_objs = []
    for obj in list_of_objs:
        if obj.tly <= maxy + 20.0 and maxy - 20.0 <= obj.bry:
            in_maxy += 1.0
            in_maxy_objs.append(obj)
        else:
            not_in_maxy += 1.0
            not_in_maxy_objs.append(obj)
        
    not_in_maxy_but_close = 0.0    
    not_in_maxy_but_close_objs = []
    for not_in_obj in not_in_maxy_objs:
        for in_obj in in_maxy_objs:
            overlap = VisualObject.overlap(not_in_obj, in_obj)
            if overlap > 0:
                not_in_maxy_but_close += 1.0
                not_in_maxy_but_close_objs.append(not_in_obj)
                continue
    return in_maxy + not_in_maxy_but_close - 1.0


def x_projection_score(list_of_objs):
    if len(list_of_objs) == 0:
        return 0
    if len(list_of_objs) == 1:
        return 0
    xproj = VisualObject.x_projection_function(list_of_objs)
    not_zero = np.nonzero(xproj)[0]
    maxgap = -1
    for i in range(0, len(not_zero)-1):
        gap = not_zero[i+1] - not_zero[i]
        if (gap > maxgap):
            maxgap = gap
    return maxgap
    
    
def y_projection_gap_score(list_of_objs):
    if len(list_of_objs) == 0:
        return 0
    if len(list_of_objs) == 1:
        return 0
    yproj = VisualObject.y_projection_function(list_of_objs)
    not_zero = np.nonzero(yproj)[0]
    maxgap = 0.0
    for i in range(0, len(not_zero)-1):
        gap = not_zero[i+1] - not_zero[i] - 1.0
        if (gap > maxgap):
            maxgap = gap
    return maxgap 

def avg_min_distance(list_of_objs):
    if (len(list_of_objs) <= 1):
        return 0.0
    avg_dist = 0.0    
    for i in range(0, len(list_of_objs)):
        obj1 = list_of_objs[i]
        mindist = float('inf')
        for j in range(0, len(list_of_objs)):
            if i == j:
                continue
            obj2 = list_of_objs[j]
            dist = VisualObject.ctr_distance(obj1, obj2)
            if (dist < mindist):
                mindist = dist
        avg_dist += mindist
    avg_dist /= len(list_of_objs)
    return avg_dist

if __name__ == "__main__":
    panoramapath = sys.argv[1]
    panorama = cv2.imread(panoramapath)
    h, w = panorama.shape[0:2]
    objdirpath = sys.argv[2]
    list_of_objs = VisualObject.objs_from_file(None, objdirpath)
    print 'number of objects', len(list_of_objs)

    fourcc = cv2.cv.CV_FOURCC('D', 'I', 'V', 'X')
    outfilename = "01_07_test"
    outvideo = cv2.VideoWriter(objdirpath + "/" + outfilename + ".avi", int(fourcc), int(2), (w, h))
    mybreaker = LineBreaker(list_of_objs, panorama, outvideo)
    lines = mybreaker.breaklines()
    result = visualize_lines(panorama, lines)
#     util.showimages([result])
    util.saveimage(result, objdirpath, outfilename + ".png")
    outvideo.release()
    
    
