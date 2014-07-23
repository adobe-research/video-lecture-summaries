#!/usr/bin/env python
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import cv2
import logging
from PIL import Image
import sys
import scipy as sp
from objectcandidate import ObjectCandidate
import cluster
from itertools import cycle

logging.basicConfig(stream=sys.stderr, level=logging.ERROR)

def importantregion(gray_img, path=None, index=0):
    sift = cv2.SIFT(1000, 3, 0.12, 12)
    kp, d = sift.detectAndCompute(gray_img, None)
    if (path != None):
        img_kp_img = cv2.drawKeypoints(gray_img, kp, None, (255, 0, 0), 0)
        cv2.imwrite(path+"\\object_features" + ("%06i" % index)+".jpg", img_kp_img)            
        
    pointsx = []
    pointsy = []
    if len(kp) > 0:
        for point in kp:
            pointsx.append(point.pt[0])
            pointsy.append(point.pt[1])
        
        minx = np.floor(np.amin(pointsx))
        miny = np.floor(np.amin(pointsy))
        maxx = np.ceil(np.amax(pointsx))
        maxy = np.ceil(np.amax(pointsy))
    else:
        minx = -1
        miny = -1
        maxx = -1
        maxy = -1
    
    return minx, miny, maxx, maxy

def candidateobjects(image, siftthres=3000):
    sift = cv2.SIFT(siftthres)
    kp, d = sift.detectAndCompute(image, None)   
    
    points = []
    for point in kp:
        points.append(point.pt)
    
    n_points = np.array(points)
    indices, labels = cluster.dbscan(n_points)
    n_kp = np.array(kp)    
    
    return
    

def removetemplate(gray_img, gray_obj, M):
    rows, cols = gray_img.shape[0:2]
    neg_warp_obj = cv2.warpPerspective(255-gray_obj, M, (cols,rows))
    
    neg_img = 255 -gray_img
    negdiff = np.minimum(neg_img, cv2.absdiff(neg_img, neg_warp_obj))
    diff = 255-negdiff
    
    #h1,w1 = neg_warp_obj.shape
    #h2,w2 = neg_img.shape
    #h3,w3 = diff.shape
    #view = sp.zeros((max(h1, h2, h3), w1+w2+w3), sp.uint8)
    #view[:h1, :w1] =neg_warp_obj
    #view[:h2, w1:w1+w2] = neg_img
    #view[:h3, w1+w2:w1+w2+w3] = negdiff
    #cv2.namedWindow("remove template", cv2.WINDOW_NORMAL)
    #cv2.imshow("remove template", view)
    #cv2.waitKey(0)
    
    return diff

def subtractobject(image, obj, M):
    shape = image.shape
    warp_obj = cv2.warpPerspective(obj_mask, M, shape)
    
    #diff = cv2.absdiff(fg_mask, warp_obj)
    #
    #h1,w1 = warp_obj.shape
    #h2,w2 = fg_mask.shape
    #h3,w3 = diff.shape
    #view = sp.zeros((max(h1, h2, h3), w1+w2+w3), sp.uint8)
    #view[:h1, :w1] =warp_obj
    #view[:h2, w1:w1+w2] = fg_mask
    #view[:h3, w1+w2:w1+w2+w3] = diff
    #cv2.namedWindow("mask obj", cv2.WINDOW_NORMAL)
    #cv2.imshow("mask obj", view)
    #cv2.waitKey(0)
    #return diff

def commonregion(gray_img1, gray_img2, M):
    rows, cols = gray_img1.shape[0:2]
    warp_img2 = cv2.warpPerspective(gray_img2, M, (cols,rows))
    diff = cv2.absdiff(gray_img1, warp_img2)
    diff = 255 - diff    
    return diff




def detectobject(gray_img, gray_obj):
    """Return 3x3 transformation matrix which transforms gray_obj to match inside gray_img
    Return None if no good match"""
    
    #surf = cv2.SURF(500)
    #surf.upright = True
    #kp1, d1 = surf.detectAndCompute(gray_obj, None)
    #kp2, d2 = surf.detectAndCompute(gray_img, None)
    sift = cv2.SIFT()
    kp1, d1 = sift.detectAndCompute(gray_obj, None)
    kp2, d2 = sift.detectAndCompute(gray_img, None)
    
    obj_kp_img = cv2.drawKeypoints(gray_obj, kp1, None, (255, 0, 0), 0)
    #cv2.imshow("object features", obj_kp_img)
    #cv2.waitKey(0)
    img_kp_img = cv2.drawKeypoints(gray_img, kp2, None, (255, 0, 0), 0)
    #cv2.imshow("image features", img_kp_img)
    #cv2.waitKey(0)
    
    bf = cv2.BFMatcher(cv2.NORM_L2, True)
    if d1 == None or d2 == None:
        #print 'no matches'
        return None
    
    logging.info("gray_obj # features: %i", len(kp1))
    logging.info("gray_img # features: %i", len(kp2))
    
    matches = bf.match(d1, d2)
    dist = [m.distance for m in matches]
    if (len(dist) == 0):
        #print 'no matches'
        return None
    
    thres_param = 0.5
    thres_dist = (sum(dist) / len(dist)) * thres_param
    good_matches = [m for m in matches if m.distance < thres_dist]
    
    logging.info("good match threshold: sum(dist)/len(dist)* %f = %f", thres_param, thres_dist)
    logging.info("Number of matches: %i", len(matches))
    logging.info("Number of good matches: %i", len(good_matches))
    
    if (len(good_matches) <= 10):
        #print 'not enough good match'
        return None
    
    
    good_matches = sorted(good_matches, key = lambda x:x.distance)
    match_img = drawMatches(gray_obj, gray_img, kp1, kp2, good_matches)
    #cv2.imshow("matching features", match_img)
    #cv2.waitKey(0)
    
    src_pts = np.float32([kp1[m.queryIdx].pt for m in good_matches])
    dst_pts = np.float32([kp2[m.trainIdx].pt for m in good_matches])
    M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
    if (mask.ravel().tolist().count(1) < len(good_matches)*0.3 or mask.ravel().tolist().count(1) < 10):
        logging.info("no good transform")
        return None

    (h1, w1) = gray_obj.shape[:2]
    (h2, w2) = gray_img.shape[:2]
    image = np.zeros((max(h1, h2), w1 + w2), np.uint8)
    image[:h1, :w1] = gray_obj
    image[:h2, w1:w1+w2] = gray_img
  
    ## Draw yellow lines connecting corresponding features.
    #print 'len(src_pts)', len(src_pts)
    #print 'len(dst_pts)', len(dst_pts)
    for (x1, y1), (x2, y2) in zip(np.int32(src_pts), np.int32(dst_pts)):
         cv2.line(image, (x1, y1), (x2+w1, y2), (0, 255, 255), lineType=cv2.CV_AA)
    #cv2.namedWindow("correspondence", cv2.WINDOW_NORMAL)
    #cv2.imshow("correspondence", image)

    return M

def drawKeypointClusters(img, n_kp, labels):          
    unique_labels = set(labels)   
    n_clusters_ = len(unique_labels)    
    colors = cycle([(255,0,0), (0,255,0), (0,0,255), (255,255,0), (255,0,255), (0, 255,255)])
    for k, col in zip(unique_labels, colors):
        class_members = labels == k
        img = cv2.drawKeypoints(img, n_kp[class_members], None, col, 4)
    return img


def drawMatches(img1, img2, k1, k2, matches, maxline=100):
    
    h1,w1 = img1.shape[:2]
    h2,w2 = img2.shape[:2]
    view = sp.zeros((max(h1, h2), w1+w2, 3), sp.uint8)
    view[:h1, :w1, 0] = img1
    view[:h2, w1:, 0] = img2
    view[:,:,1] = view[:,:,0]
    view[:,:,2] = view[:,:,0]
    numline = 0
    for m in matches:
        color = tuple([sp.random.randint(0,255) for _ in xrange(3)])
        cv2.line(view, (int(k1[m.queryIdx].pt[0]), int(k1[m.queryIdx].pt[1])) , (int(k2[m.trainIdx].pt[0] + w1), int(k2[m.trainIdx].pt[1])), color)
        numline += 1
        if (numline >= maxline):
            break
    return view

def whiteout(threshimg, tlx, tly, brx, bry):
    """Whiteout rectangular region"""
    threshimg2 = threshimg.copy()
    threshimg2[tly:bry, tlx:brx] = 255
    return threshimg2

def bgfill(img, tlx, tly, brx, bry):
    """Inpaint rectangular region"""
    img_mask = np.zeros(img.shape[:2], dtype=np.uint8)
    img_mask[tly:bry, tlx:brx] = 255
    fill_img = cv2.inpaint(img, img_mask, 3, 0)
    return fill_img

def cropimage(img, tlx, tly, brx, bry):
    img2 = img[tly:bry, tlx:brx]
    return img2

def numfgpix_mit(gray_frame):
    return (gray_frame < 200).sum()

def numfgpix_khan(gray_frame):
    return (gray_frame >=100).sum()

def removebg_mit(gray_frame):
    dest = gray_frame.copy()
    dest[gray_frame < 200] = 255
    dest[gray_frame >=200] = 0
    return dest

def removebg_khan(gray_frame):
    dest = gray_frame.copy()
    dest[gray_frame < 100 ] = 255
    dest[gray_frame >= 100] = 0
    return dest

def numfgpix(img, bgcolor):
    """Return number of foreground pixels in img, where bg color denotes the background colors"""
    sub = np.empty(img.shape)
    print 'img.shape', img.shape
    sub.fill(1)
    for x in bgcolor:
        bg = np.empty(img.shape)
        bg.fill(x)
        sub =  np.maximum(np.zeros(img.shape), np.abs(img - bg))
    count = np.count_nonzero(sub)
    return count

def numfgpix(sub_img):
    return (sub_img == 255).sum()    

def matchtemplate(gray_img, gray_template):
    """Return the top left corner of the rectangle that matches template inside img"""
    method = 4 
    w, h = gray_template.shape[::-1]
    
    # Apply template Matching
    res = cv2.matchTemplate(gray_img,gray_template,method, 2)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    top_left = max_loc
    bottom_right = (top_left[0] + w, top_left[1] + h)
    return top_left;

def removebackground(gray_img, gray_bgsample, thres=50):
    """Remove background from img"""
    bgh, bgw = gray_bgsample.shape[:2]
    bgpix = []
    for i in range(0, bgw):
        for j in range(0, bgh):
            bgpix.append(gray_bgsample[j, i])
    
    orig = np.full(gray_img.shape, 255, dtype=np.uint8)
    for pix in bgpix:
        bg = np.full(gray_img.shape, pix, dtype=np.uint8)
        diff = cv2.absdiff(gray_img, bg)
        sub = np.minimum(orig, diff)
    sub[sub < thres] = 0
    sub[sub >= thres] = 255
    return sub

if __name__ == "__main__":
    src = cv2.imread("udacity1_capture.png", 0) #3 channel BGR image
    dest = src.copy()
    dest[src < 200] = 0
    dest[src >=200] = 255
    cv2.imwrite("udactiy1_bg.png", dest)
    cv2.imshow("display", dest)
    cv2.waitKey(0)
    