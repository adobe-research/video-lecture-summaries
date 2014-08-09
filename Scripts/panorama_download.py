#!/usr/bin/env python
import cv2
import numpy as np
import math
import sys

def extract_features(gray_image, surfThreshold=1000):

  ## Detect SIFT features and compute descriptors.
  sift = cv2.SIFT()
  keypoints, descriptors = sift.detectAndCompute(gray_obj, None)
    
  #descriptors = np.array([[1,1], [7,5], [5,2], [3,4]], np.float32)
  #keypoints = [cv2.KeyPoint(100 * x, 100 * y, 1) for (x,y) in descriptors]

  return (keypoints, descriptors)


## 2. Find corresponding features between the images. [2] ----------------
def find_correspondences(keypoints1, descriptors1, keypoints2, descriptors2):
  
  ## Find corresponding features.
  bf = cv2.BFMatcher(cv2.NORM_L2, TRUE)
  match = bf.match(descriptors1, descriptors2)

  ## TODO: Look up corresponding keypoints.
  points1 = np.array([keypoints1[m.queryIdx].pt for m in matches], np.float32)
  points2 = np.array([keypoints2[m.queryIdx].pt for m in matches], np.float32)
  
  #points1 = np.array([k.pt for k in keypoints1], np.float32)
  #points2 = np.array([k.pt for k in keypoints1], np.float32)

  return (points1, points2)


## 3. Calculate the size and offset of the stitched panorama. [5] --------
def calculate_size(row1, col1, row2, col2, H):
  
  min_row = 1
  min_col = 1
  max_row = 0
  max_col = 0
  
  im2T = np.array([[1,1,1], [1, col2,1], [row2, 1, 1], [row2, col2, 1]])
  im2 = corners.T
  result = H*im2
  min_row = math.floor(min(min_row, result[1]))
  max_row = math.ceil(max(max_row, result[1]))
  min_col = math.floor(min(min_col, result[2]))
  max_col = math.ceil(max(max_col, result[2]))
    
  im_rows = max(max_row, row1) - min(min_row, row1) + 1
  im_cols = max(max_col, col1) - min(min_col, col1) + 1
  
  row_offset = 1 - min_row
  col_offset = 1 - min_col
  
  
  size = (im_rows, im_cols)
  offset = (row_offset, col_offset)
  return (size, offset)


## 4. Combine images into a panorama. [4] --------------------------------
def merge_images(image1, image2, homography, size, offset, keypoints):

  ## TODO: Combine the two images into one.
  (h1, w1) = image1.shape[:2]
  (h2, w2) = image2.shape[:2]
  panorama = np.zeros((size[1], size[0], 3), np.uint8)
  panorama[:h1, :w1] = image1
  panorama[offset[2]:h2, offset[1]:offset[1]+w2] = image2

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
  ## Load images.
  image1 = cv2.imread(sys.argv[1])
  image2 = cv2.imread(sys.argv[2])

  ## Detect features and compute descriptors.
  (keypoints1, descriptors1) = extract_features(image1)
  (keypoints2, descriptors2) = extract_features(image2)
  print len(keypoints1), "features detected in image1"
  print len(keypoints2), "features detected in image2"
  
  ## Find corresponding features.
  (points1, points2) = find_correspondences(keypoints1, descriptors1, keypoints2, descriptors2)
  print len(points1), "features matched"

  ## Visualise corresponding features.
  #correspondences = draw_correspondences(image1, image2, points1, points2)
  #cv2.imwrite("correspondences.jpg", correspondences)
  #cv2.imshow('correspondences', correspondences)
  
  ## Find homography between the views.
  (homography, _) = cv2.findHomography(points2, points1)
  
  ## Calculate size and offset of merged panorama.
  (size, offset) = calculate_size(image1.shape, image2.shape, homography)
  print "output size: %ix%i" % size
  
  ## Finally combine images into a panorama.
  panorama = merge_images(image1, image2, homography, size, offset, (points1, points2))
  cv2.imwrite("panorama.jpg", panorama)
  cv2.imshow('panorama', panorama)
  cv2.waitKey()
  

