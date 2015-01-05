'''
Created on Dec 18, 2014

@author: hijungshin
'''

import sys
import util
import cv2
from dynamic_linebreak import *
import operator

def set_to_ordered_list(set_of_objs):
    list_of_objs = list(set_of_objs)
    list_of_objs = sorted(list_of_objs, key=operator.attrgetter('start_fid'))
    return list_of_objs

def show(panorama, list_of_lines, curline):
    for i in range(0, len(list_of_lines)):
        line = list_of_lines[i]
        if i == curline:
            visualize_line(panorama, line, (255,0,255))
        else:
            visualize_line(panorama, line)
    return panorama

if __name__ == "__main__":   
    panorama = cv2.imread(sys.argv[1])
    objdir = sys.argv[2]
    list_of_objs = VisualObject.objs_from_file(None, objdir)
#     util.showimages([panorama])
    cv2.imshow("", panorama)
    cv2.waitKey(100)
    
    curline = 0    
    list_of_lines = []
    list_of_line_ids = []
    
    cur_select_objs = set([])
    cur_select_ids = set([])
    
    list_of_lines.append(cur_select_objs)
    list_of_line_ids.append(cur_select_ids)
    
    while (True):
        cur_select_objs = list_of_lines[curline]
        cur_select_ids = list_of_line_ids[curline]
        
        userstring = raw_input('object number: ')
        if (userstring == 'please quit'):
            break
        elif (userstring=='add line'):
            cur_select_objs = set([])
            cur_select_ids = set([])
            list_of_lines.append(cur_select_objs)
            list_of_line_ids.append(cur_select_ids)
            curline = len(list_of_lines) - 1
        elif(userstring=="change line"):
            userstring = raw_input('line number:')
            changed = False
            while(not changed):
                if (userstring.isdigit() and int(userstring) < len(list_of_lines)):
                    curline = int(userstring)
                    changed = True
                else:
                    userstring = raw_input("Invalid line number. Please enter again:")    
        elif (userstring == 'eval'):
            curline_cost = weighted_avg_linecost([set_to_ordered_list(cur_select_objs)])
            print 'current line', cur_select_ids
            print 'current line_cost = ', curline_cost
        elif (userstring == 'eval all'):
            print 'all lines:', list_of_line_ids
            for i in range(0, len(list_of_lines)):
                curline_cost = weighted_avg_linecost([set_to_ordered_list(list_of_lines[i])])
                print 'line', i, 'cost =', curline_cost
            print 'total cost = ', weighted_avg_linecost(list_of_lines)
             
        elif (userstring=='clear'):
            list_of_lines[curline] = set([])
            list_of_line_ids[curline] = set([])
            
        elif (userstring=='clear all'):
            cur_select_objs = set([])
            cur_select_ids = set([])
            list_of_lines = [cur_select_objs]
            list_of_line_ids = [cur_select_ids]
            curline = 0
        else:
            try:
                objnum = int(userstring)
            except:
                print 'invalid string'
                continue
            if (objnum > 0):
                newobj = list_of_objs[objnum-1]
                newobj.numfgpixel()
                cur_select_objs.add(list_of_objs[objnum-1])
                cur_select_ids.add(objnum)
            else:
                objnum = abs(objnum)
                print 'objnum', objnum
                cur_select_objs.remove(list_of_objs[objnum-1])
                cur_select_ids.remove(objnum)
        panorama_copy = panorama.copy()
        panorama_copy = show(panorama_copy, list_of_lines, curline)
        cv2.imshow("", panorama_copy)
        cv2.waitKey(100)
