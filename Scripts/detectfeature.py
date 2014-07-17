#!/usr/bin/env python
import numpy as np
import cv2
from matplotlib import pyplot as plt
import sys
import scipy as sp


if __name__ == "__main__":    
# matching features of two images
    surfthres = 50
    
    img1_path = sys.argv[1]
    img1 = cv2.imread(img1_path, 0)
        
    surf = cv2.SURF(surfthres)
    surf.upright=True
    
    # detect keypoints and descriptors in img1
    kp1, d1 = surf.detectAndCompute(img1, None)
    
    #img 2
    img2_path = sys.argv[2]
    img2 = cv2.imread(img2_path, 0)
    
    kp2, d2 = surf.detectAndCompute(img2, None)
    
    bf = cv2.BFMatcher(cv2.NORM_L2, True)
    #bf.crossCheck = True
    matches = bf.match(d1, d2)
    
    #visualize
    
    print '#matches:', len(matches)
    dist = [m.distance for m in matches]

    print 'distance: min: %.3f' % min(dist)
    print 'distance: mean: %.3f' % (sum(dist) / len(dist))
    print 'distance: max: %.3f' % max(dist)

    # threshold: half the mean
    thres_dist = (sum(dist) / len(dist)) * 0.8

    # keep only the reasonable matches
    sel_matches = [m for m in matches if m.distance < thres_dist]
    print len(matches)
    print len(sel_matches)
    if len(sel_matches) > 0.3*len(matches):
        src_pts = np.float32([kp1[m.queryIdx].pt for m in sel_matches])
        dst_pts = np.float32([kp2[m.trainIdx].pt for m in sel_matches])

        M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
        matchesMask = mask.ravel().tolist()
        
        h,w = img1.shape
        pts = np.float32([ [0,0],[0,h-1],[w-1,h-1],[w-1,0] ]).reshape(-1,1,2)
        dst = cv2.perspectiveTransform(pts,M)
    
        cv2.polylines(img2,[np.int32(dst)],True,0,3)
        
        print img2

        plt.imshow(img2, 'gray'),plt.show()

   

    