#!/usr/bin/env python
import cv2
import numpy as np
import math
import processframe as pf
import sys
import os
from PIL import Image

## 1. Extract SURF keypoints and descriptors from an image. [4] ----------
def extract_features(gray_image, surfThreshold=1000):

  ## Detect SIFT features and compute descriptors.
  sift = cv2.SIFT()
  keypoints, descriptors = sift.detectAndCompute(gray_image, None)
    
  #descriptors = np.array([[1,1], [7,5], [5,2], [3,4]], np.float32)
  #keypoints = [cv2.KeyPoint(100 * x, 100 * y, 1) for (x,y) in descriptors]

  return (keypoints, descriptors)


## 2. Find corresponding features between the images. [2] ----------------
def find_correspondences(keypoints1, descriptors1, keypoints2, descriptors2):
  
  ## Find corresponding features.
  bf = cv2.BFMatcher(cv2.NORM_L2, True)
  match = bf.match(descriptors1, descriptors2)
  dist = [m.distance for m in match]
  thres_param = 0.5
  thres_dist = (sum(dist) / len(dist)) * thres_param
  good_matches = [m for m in match if m.distance < thres_dist]
    
  if (len(good_matches) < 10):
    #print 'not enough good match'
    return None
    
  good_matches = sorted(good_matches, key = lambda x:x.distance)
    
  src_pts = np.float32([keypoints1[m.queryIdx].pt for m in good_matches])
  dst_pts = np.float32([keypoints2[m.trainIdx].pt for m in good_matches])
  M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)


  ## TODO: Look up corresponding keypoints.
  points1 = np.array([keypoints1[m.queryIdx].pt for m in match], np.float32)
  points2 = np.array([keypoints2[m.trainIdx].pt for m in match], np.float32)
  
  #points1 = np.array([k.pt for k in keypoints1], np.float32)
  #points2 = np.array([k.pt for k in keypoints1], np.float32)

  return (src_pts, dst_pts)


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


## 4. Combine images into a panorama. [4] --------------------------------
def merge_images(image1, image2, homography, size, offset, keypoints):

  ## TODO: Combine the two images into one.
  (h1, w1) = image1.shape[:2]
  (h2, w2) = image2.shape[:2]
  panorama = np.zeros((size[1], size[0]), np.uint8)
  panorama[:h1, :w1] = image1
  panorama[offset[1]:offset[1]+h2, offset[0]:offset[0]+w2] = image2

  return panorama


##---- No need to change anything below this point. ----------------------


def match_flann(desc1, desc2, r_threshold = 0.06):
  'Finds strong corresponding features in the two given vectors.'
  ## Adapted from <http://stackoverflow.com/a/8311498/72470>.

  ## Build a kd-tree from the second feature vector.
  FLANN_INDEX_KDTREE = 1  # bug: flann enums are missing
  flann = cv2.flann_Index(desc2, {'algorithm': FLANN_INDEX_KDTREE, 'trees': 4})

  ## For each feature in desc1, find the two closest ones in desc2.
  (idx2, dist) = flann.knnSearch(desc1, 2, params={}) # bug: need empty {}

  ## Create a mask that indicates if the first-found item is sufficiently
  ## closer than the second-found, to check if the match is robust.
  mask = dist[:,0] / dist[:,1] < r_threshold
  
  ## Only return robust feature pairs.
  idx1  = np.arange(len(desc1))
  pairs = np.int32(zip(idx1, idx2[:,0]))
  return pairs[mask]


def draw_correspondences(image1, image2, points1, points2):
  'Connects corresponding features in the two images using yellow lines.'

  ## Put images side-by-side into 'image'.
  (h1, w1) = image1.shape[:2]
  (h2, w2) = image2.shape[:2]
  image = np.zeros((max(h1, h2), w1 + w2, 3), np.uint8)
  image[:h1, :w1] = image1
  image[:h2, w1:w1+w2] = image2
  
  ## Draw yellow lines connecting corresponding features.
  for (x1, y1), (x2, y2) in zip(np.int32(points1), np.int32(points2)):
    cv2.line(image, (x1, y1), (x2+w1, y2), (0, 255, 255), lineType=cv2.CV_AA)

  return image


if __name__ == "__main__":
    
    dir_path = sys.argv[1]
    filelist = os.listdir(dir_path)
    imagefiles = []
    for filename in filelist:
        if "capture" in filename:
            imagefiles.append(filename)
    
    #previmage = cv2.imread(dir_path + "\\" + imagefiles[0], -1)
    prevpix_gray = cv2.imread(dir_path + "\\" + imagefiles[0], 0)   
    previmage = Image.open(dir_path + "\\" + imagefiles[0])
    previmage = previmage.convert("RGBA")
    prevpix = np.array(previmage)
    
    for i in range(1, len(imagefiles)):
        print "%i of %i" %(i, len(imagefiles)), imagefiles[i]       
        ##find transformation M of current image to match previous image        
        curpix_gray = cv2.imread(dir_path + "\\"+imagefiles[i], 0)
        curimage = Image.open(dir_path + "\\" + imagefiles[i])
        curimage = curimage.convert("RGBA")
        
        (curh, curw) = curpix_gray.shape
        (prevh, prevw) = prevpix_gray.shape
        
        M = pf.detectobject(prevpix_gray, curpix_gray)
        if M == None:
            tx = 0.0
            ty = prevh
            M = np.array([[1.0, 0.0, tx], [0.0, 1.0, ty], [0.0, 0.0, 1.0]])
            nomatch = True
        else:
            nomatch = False
        ##warp current image with transparent border
        (warpsize, offset) = calculate_size(prevpix_gray.shape, curpix_gray.shape, M)
        #if nomatch:
        #    offset = (-tx, -ty)
        curpix = np.array(curimage)
        curpix_warp = cv2.warpPerspective(curpix, M, (int(warpsize[0]), int(warpsize[1])), borderMode = cv2.BORDER_TRANSPARENT)
        curimage_warp = Image.fromarray(curpix_warp, "RGBA")
        print 'warpsize', warpsize
        print 'nomatch', nomatch
                
        #cv2.namedWindow("foreground warp", cv2.WINDOW_NORMAL)
        #cv2.imshow("foreground warp", curpix_warp)
        ##overlay current image on top of previous image
        xoff = int(offset[0])
        yoff = int(offset[1])
        M0 = np.array([[1.0, 0.0, -(xoff-1)], [0.0, 1.0, -(yoff-1)], [0.0, 0.0, 1.0]])
      
        #cv2.imshow("prevpix", prevpix)
        prevpix_warp = cv2.warpPerspective(prevpix, M0, (int(warpsize[0]), int(warpsize[1])), borderMode = cv2.BORDER_TRANSPARENT)
        #cv2.imshow("prevpix_warp", prevpix_warp)
        previmage_warp = Image.fromarray(prevpix_warp, "RGBA")
        #cv2.namedWindow("background warp", cv2.WINDOW_NORMAL)
        #cv2.imshow("background warp", prevpix_warp)
        previmage_warp.paste(curimage_warp, (-(xoff-1),-(yoff-1)), curimage_warp)        
        previmage = previmage_warp
        prevpix = np.array(previmage_warp)
        #cv2.namedWindow("result", cv2.WINDOW_NORMAL )
        #cv2.imshow("result", prevpix)
        #cv2.waitKey(0)
        previmage_gray = previmage_warp.convert("L")
        prevpix_gray = np.array(previmage_gray)
        
    previmage.save(dir_path + "//panorama.png")    
    
