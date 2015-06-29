'''
Created on Jun 26, 2015

@author: hijungshin
'''
import sys
import cv2
from video import Video
import util
import processframe as pf

def write_scroll_coord(video, panorama):
    outfile = video.videoname + "_scroll.txt"
    scrolltxt = open(outfile, "w")
    cap = cv2.VideoCapture(video.filepath)

    while(cap.isOpened()):
        ret, frame = cap.read()
        if (frame == None):
            break
        topleft = pf.find_object_exact_inside(panorama, frame, threshold=0)
        scrolltxt.write("%i\t%i\n"%(topleft[0], topleft[1]))
    
    scrolltxt.close()
    
def read_scroll_coord(txt):
    list_of_coords = util.list_of_vecs_from_txt(txt)
    coords = []
    for xy in list_of_coords:
        coords.append((int(xy[0]), int(xy[1])))
    return coords    

def scroll_ids(video, scroll_coords):
    outfile2 = video.videoname + "_scroll_ids.txt"
    scrollid_txt = open(outfile2, "w")
    
    prev = None
    fid = 0
    for coord in scroll_coords:
        if (prev is not None):
            dx = coord[0] - prev[0]
            dy = coord[1] - prev[1]
            if (dx != 0 or dy != 0):
                scrollid_txt.write("%i\n"%fid)
        fid += 1        
        prev = coord
        
    scrollid_txt.close()    
    

if __name__ == "__main__":
    video = Video(sys.argv[1])
    panorama = cv2.imread(sys.argv[2])
    write_scroll_coord(video, panorama)