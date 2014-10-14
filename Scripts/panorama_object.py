'''
Created on Oct 14, 2014

@author: hijungshin
'''
import processframe as pf
import util
import sys
import cv2
from visualobjects import VisualObject

def find_objects(panorama, list_of_objects):
    
    panorama_copy = panorama.copy()
    for obj in list_of_objects:
        tl = pf.find_object_exact_inside(panorama, obj.img)
        if tl is None:
#             util.showimages([obj.img])
            continue
        cv2.rectangle(panorama_copy, (tl[0], tl[1]), (tl[0]+obj.width, tl[1]+obj.height), (0, 255, 0), 1)
#         util.showimages([panorama_copy])
    return panorama_copy
        
if __name__ == "__main__":
    panoramapath = sys.argv[1]
    objdirpath = sys.argv[2]
    
    panorama = cv2.imread(panoramapath)
    img_objs = VisualObject.objs_from_file(None, objdirpath)
    panorama_copy = find_objects(panorama, img_objs)
    util.saveimage(panorama_copy, objdirpath, "panorama_objects.png")

    