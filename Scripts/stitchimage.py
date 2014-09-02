#!/usr/bin/env python
import cv2
import numpy as np
import math
import processframe as pf
import sys
import util
import os
from PIL import Image

def calculate_size(size_image1, size_image2, H):
  
  col1, row1 = size_image1
  col2, row2 = size_image2
  min_row = 1
  min_col = 1
  max_row = 0
  max_col = 0
  
  im2T = np.array([[1,1,1], [1, col2,1], [row2, 1, 1], [row2, col2, 1]])
  im2 = im2T.T
  result = H.dot(im2)
  min_row = math.floor(min(min_row, min(result[0])))
  max_row = math.ceil(max(max_row, max(result[0])))
  min_col = math.floor(min(min_col, min(result[1])))
  max_col = math.ceil(max(max_col, max(result[1])))
    
  im_rows = max(max_row, row1) - min(min_row, row1) + 1
  im_cols = max(max_col, col1) - min(min_col, col1) + 1
  
  size = (im_rows, im_cols)
  offset = (min_row, min_col)
  return (size, offset)

def stitch_images(previmage, curimage, M):  
  if (previmage == None):
    return curimage
  
  curimage = cv2.cvtColor(curimage, cv2.COLOR_BGR2BGRA)
  previmage = cv2.cvtColor(previmage, cv2.COLOR_BGR2BGRA)
  
  (curh, curw) = curimage.shape[:2]
  (prevh, prevw) = previmage.shape[:2]
  (warpsize, offset) = calculate_size((prevh, prevw), (curh, curw), M)
  
  curimage_warp = cv2.warpPerspective(curimage, M, (int(warpsize[0]), int(warpsize[1])), borderMode = cv2.BORDER_TRANSPARENT)
  
  xoff = int(offset[0])
  yoff = int(offset[1])
  M0 = np.array([[1.0, 0.0, -(xoff-1)], [0.0, 1.0, -(yoff-1)], [0.0, 0.0, 1.0]])      
  previmage_warp = cv2.warpPerspective(previmage, M0, (int(warpsize[0]), int(warpsize[1])), borderMode = cv2.BORDER_TRANSPARENT)        
  
  pil_curimage_warp = Image.fromarray(curimage_warp, "RGBA")
  pil_previmage_warp = Image.fromarray(previmage_warp, "RGBA")
  pil_previmage_warp.paste(pil_curimage_warp, (-(xoff-1),-(yoff-1)), pil_curimage_warp)
  merged = np.array(pil_previmage_warp)
  
  #util.showimages([previmage, curimage, merged])
  return merged
  
def panorama(list_of_frames):
  prevpix = lsit_of_frames[0]
  prevpix_gray = cv2.cvtColor(prevpix, cv2.COLOR_BGR2GRAY)
  
  for i in range(1, len(list_of_frames)):
    curpix = frame
    curpix_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    prevh, prevw = prevpix.shape[:2]
    M = pf.detectobject(prevpix_gray, curpix_gray)
    if not pf.isgoodmatch(M):
        tx = 0.0
        ty = prevh
        M = np.array([[1.0, 0.0, tx], [0.0, 1.0, ty], [0.0, 0.0, 1.0]])
        nomatch = True
    else:
        nomatch = False
    
    prevpix = stitch_images(prevpix, curpix, M)
    prevpix_gray = cv2.cvtColor(prevpix, cv2.COLOR_BGR2GRAY)
  
  return prevpix


if __name__ == "__main__":
    
    dir_path = sys.argv[1]
    filelist = os.listdir(dir_path)
    imagefiles = []
    for filename in filelist:
        if "capture" in filename:
            imagefiles.append(filename)
    
    prevpix = cv2.imread(dir_path + "\\" + imagefiles[0])
    prevpix_gray = cv2.cvtColor(prevpix, cv2.COLOR_BGR2GRAY)
    
    for i in range(1, len(imagefiles)):
        print "%i of %i" %(i, len(imagefiles)), imagefiles[i]       
        
        ##find transformation M of current image to match previous image        
        curpix = cv2.imread(dir_path + "\\" + imagefiles[i])
        curpix_gray = cv2.cvtColor(curpix, cv2.COLOR_BGR2GRAY)
        
        prevh, prevw = prevpix.shape[:2]
        M = pf.detectobject(prevpix_gray, curpix_gray)
        if not pf.isgoodmatch(M):
            tx = 0.0
            ty = prevh
            M = np.array([[1.0, 0.0, tx], [0.0, 1.0, ty], [0.0, 0.0, 1.0]])
            nomatch = True
        else:
            nomatch = False
        
        prevpix = stitch_images(prevpix, curpix, M)
        prevpix_gray = cv2.cvtColor(prevpix, cv2.COLOR_BGR2GRAY)
        
        
        
        
    previmage.save(dir_path + "//panorama.png")    
    
