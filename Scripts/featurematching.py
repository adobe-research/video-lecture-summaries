#!/usr/bin/env python
import numpy as np
import cv2
from matplotlib import pyplot as plt
import sys
import scipy as sp
    
if __name__ == "__main__":    
# matching features of two images

    
    if len(sys.argv) < 3:
        print 'usage: %s img1 img2' % sys.argv[0]
        sys.exit(1)
    
    img1_path = sys.argv[1]
    
    img1 = cv2.imread(img1_path, cv2.CV_LOAD_IMAGE_GRAYSCALE)
        
    surf = cv2.SURF(500)
    
    # detect keypoints and descriptors
    kp1, d1 = surf.detectAndCompute(img1, None)
    
    img2 = cv2.drawKeypoints(img1, kp1, None, (255, 0, 0), 2)
    plt.imshow(img2)
    plt.show()
    
    #kp2, d2 = surf.detectAndCompute(img2, None)
    
    #print d1[1]
    #print d2[1]
    ## descriptors
    #k1, d1 = descriptor.compute(img1, kp1)
    #k2, d2 = descriptor.compute(img2, kp2)
    #
    #print '#descriptors in image1: %d, image2: %d' % (len(d1), len(d2))
    #
    ## match the descriptors
    #matches = matcher.match(d1, d2)
    #
    ## visualize the matches
    ##print '#matches:', len(matches)
    #dist = [m.distance for m in matches]
    #
    #print 'distance: min: %.3f' % min(dist)
    #print 'distance: mean: %.3f' % (sum(dist) / len(dist))
    #print 'distance: max: %.3f' % max(dist)
    #
    ## threshold: half the mean
    #thres_dist = (sum(dist) / len(dist)) * 0.5
    #
    ## keep only the reasonable matches
    #sel_matches = [m for m in matches if m.distance < thres_dist]
    #
    #print '#selected matches:', len(sel_matches)
    #
    ## #####################################
    ## visualization
    #h1, w1 = img1.shape[:2]
    #h2, w2 = img2.shape[:2]
    #view = sp.zeros((max(h1, h2), w1 + w2, 3), sp.uint8)
    #view[:h1, :w1, 0] = img1
    #view[:h2, w1:, 0] = img2
    #view[:, :, 1] = view[:, :, 0]
    #view[:, :, 2] = view[:, :, 0]
    #
    #for m in sel_matches:
    #    # draw the keypoints
    #    # print m.queryIdx, m.trainIdx, m.distance
    #    color = tuple([sp.random.randint(0, 255) for _ in xrange(3)])
    #    cv2.line(view, (int(k1[m.queryIdx].pt[0]), int(k1[m.queryIdx].pt[1])) , (int(k2[m.trainIdx].pt[0] + w1), int(k2[m.trainIdx].pt[1])), color)
    #
    #
    #cv2.imshow("view", view)
    #cv2.waitKey()