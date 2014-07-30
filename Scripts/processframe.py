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
import util

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
    
def highlight(image, mask, (r,g,b,a) = (251, 175, 23, 100)):
   
    # Create a semi-transparent highlight layer the size of image    
    h,w,bgra =  image.shape  
    layer = np.empty((h,w,4), dtype=np.uint8)
    layer[:,:,0] = r
    layer[:,:,1] = g
    layer[:,:,2] = b
    layer[:,:,3] = a
    
    blurmask = expandmask(mask)
    layer = maskimage(layer, blurmask)
    
    fg_mask = fgmask(image)
    fgimg = alphaimage(image, fg_mask)
    img = Image.fromarray(fgimg, "RGBA")
    b, g, r,a = img.split()
    img = Image.merge("RGBA", (r, g, b, a))
    
    highlight = Image.fromarray(layer, "RGBA")
    result = Image.alpha_composite(img, highlight)
    r,g,b,a = result.split()    
    data = np.empty((h,w,4), dtype=np.uint8)
    data[:,:,0] = b
    data[:,:,1] = g
    data[:,:,2] = r
    data[:,:,3] = a
    return data
    
    
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

def fgmask(image, threshold=225):
    #b = image[:,:,0]
    #g = image[:,:,1]
    #r = image[:,:,2]
    #cv2.imshow("minimum", img2gray)
    img2gray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
    #cv2.imshow("im2gray", img2gray)
    #cv2.waitKey(0)
    ret, mask = cv2.threshold(img2gray, threshold, 255, cv2.THRESH_BINARY_INV)
    
    return mask

def fgbbox(mask):   
    cols, rows = np.where(mask != 0)
    if (len(cols) == 0 or len(rows) == 0):
        return (-1, -1, -1, -1)
    tlx = min(rows)
    brx = max(rows)
    tly = min(cols)
    bry = max(cols)
    return (tlx, tly, brx, bry)


def maskimage_white(image, mask):
    # mask is a single channel array; mask_region is whited
    maskimg = cv2.bitwise_and(image, image, mask = mask)
    inv_mask = cv2.bitwise_not(mask)
    maskimg = cv2.bitwise_not(maskimg, maskimg, mask = inv_mask)
    return maskimg

def maskimage(image, mask):
    # mask is a single channel array; mask_region is blacked
    maskimg = cv2.bitwise_and(image, image, mask = mask)
    return maskimg

def alphaimage(image, mask):    
    h,w,bgr =  image.shape
    result = np.empty((h,w,bgr+1), dtype=np.uint8)
    result[:,:,0:3] = image
    result[:,:,3] = mask
    return result
    

def expandmask(mask, width=10):
    kernel = np.ones((width,width),np.float32)/(width*width)
    blurmask = cv2.filter2D(mask,-1,kernel)
    blurmask[blurmask != 0] = 255
    return blurmask

def subtractobject(image, objmask, M, emptycolor=0):    
    rows, cols = image.shape[0:2]    
    warpmask = cv2.warpPerspective(objmask, M, (cols, rows))
    warpmask = cv2.bitwise_not(warpmask)
    kernel = np.ones((10,10),np.float32)/100
    blurmask = cv2.filter2D(warpmask,-1,kernel)
    blurmask[blurmask != 255] = 0
    
    subimage = cv2.bitwise_and(image, image, mask = blurmask)   
    subimage[blurmask==0] = emptycolor    
     
    return subimage

def findobject(gray_img, gray_obj):
    sift = cv2.SURF(0)
    kp1, d1 = sift.detectAndCompute(gray_obj, None)
    kp2, d2 = sift.detectAndCompute(gray_img, None)
    
    obj_kp_img = cv2.drawKeypoints(gray_obj, kp1, None, (255, 0, 0), 0)
    img_kp_img = cv2.drawKeypoints(gray_img, kp2, None, (255, 0, 0), 0)

    logging.info("Object # features: %i", len(kp1))
    logging.info("Image # features: %i", len(kp2))
    if d1 == None or d2 == None:
        print 'No matches: no feature'
        return None
    
    bf = cv2.BFMatcher(cv2.NORM_L2, True)
    matches = bf.match(d1, d2)
    dist = [m.distance for m in matches]
    logging.info("Number of correspondences: %i", len(matches))
    if (len(matches) < 4):
        print 'No matches: Not enough correspondence'
        return None
    
    #match_img = drawMatches(gray_obj, gray_img, kp1, kp2, matches)
    #cv2.imshow("match img", match_img)
    #cv2.waitKey(0)
    #
    src_pts = np.float32([kp1[m.queryIdx].pt for m in matches])
    dst_pts = np.float32([kp2[m.trainIdx].pt for m in matches])
    
    M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
    #num_in = mask.ravel().tolist().count(1)    
    #logging.info("# Inliers: %i", num_in)
    #
    #if (num_in < len(kp1)*0.5):
    #    print 'Warning: less than half of object features are inliers'        
    #
    #(h1, w1) = gray_obj.shape[:2]
    #(h2, w2) = gray_img.shape[:2]
    #image = np.zeros((max(h1, h2), w1 + w2), np.uint8)
    #image[:h1, :w1] = gray_obj
    #image[:h2, w1:w1+w2] = gray_img
    return M    
    

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
    img_kp_img = cv2.drawKeypoints(gray_img, kp2, None, (255, 0, 0), 0)
    
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
    
    if (len(good_matches) <= 3):
        #print 'not enough good match'
        return None
    
    
    good_matches = sorted(good_matches, key = lambda x:x.distance)
    match_img = drawMatches(gray_obj, gray_img, kp1, kp2, good_matches)
    #cv2.imshow("matching features", match_img)
    #cv2.waitKey(0)
    
    src_pts = np.float32([kp1[m.queryIdx].pt for m in good_matches])
    dst_pts = np.float32([kp2[m.trainIdx].pt for m in good_matches])
    M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
    if (mask.ravel().tolist().count(1) < len(good_matches)*0.3):
        logging.info("mask count %i", mask.ravel().tolist().count(1))
        logging.info("no good transform")
        return None

    #(h1, w1) = gray_obj.shape[:2]
    #(h2, w2) = gray_img.shape[:2]
    #image = np.zeros((max(h1, h2), w1 + w2), np.uint8)
    #image[:h1, :w1] = gray_obj
    #image[:h2, w1:w1+w2] = gray_img
    #
    ## Draw yellow lines connecting corresponding features.
    #print 'len(src_pts)', len(src_pts)
    #print 'len(dst_pts)', len(dst_pts)
    #for (x1, y1), (x2, y2) in zip(np.int32(src_pts), np.int32(dst_pts)):
         #cv2.line(image, (x1, y1), (x2+w1, y2), (0, 255, 255), lineType=cv2.CV_AA)
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

def isgoodmatch(M):
    if M == None:
        return False

    unitsquare = np.array([[0,0], [1,0], [1,1], [0,1]], dtype='float32')
    unitsquare = np.array([unitsquare])
    tsquare = cv2.perspectiveTransform(unitsquare, M)    
    tarea = cv2.contourArea(tsquare)
    if tarea < 0.1 or tarea > 10:
        print "Not a good homography, scaling factor:", tarea
        return False
    return True

def findobject_exact(fgimg_gray, obj_gray):
    res = cv2.matchTemplate(fgimg_gray, obj_gray, cv2.TM_SQDIFF_NORMED)
    #plt.imshow(res,cmap = 'gray')
    #plt.show()
    #cv2.waitKey(0)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    print min_val
    if (min_val > 0.08):
        print "Exact match not found:", min_val
        return None
    top_left = min_loc
    M = np.identity(3, dtype = np.float32)
    M[0,2] = top_left[0]
    M[1,2] = top_left[1]
    h,w = obj_gray.shape[0:2]
    bottom_right = (top_left[0] + w, top_left[1] + h)
    #cv2.imshow("object", obj_gray)
    #cv2.rectangle(fgimg_gray, top_left, bottom_right, 0, 2)
    #cv2.imshow("findobject exact", fgimg_gray)
    #cv2.waitKey(0)
    return M


def getnewobj(image_and_mask, objlist):
    image = image_and_mask[0]
    fgmask = image_and_mask[1]
    fgimg = maskimage_white(image, fgmask)
    
    if objlist == None:
        return fgimg, fgmask
    for i in range(0, len(objlist)):
        obj = objlist[i][0]
        objmask = objlist[i][1]

        fgimg_gray = cv2.cvtColor(fgimg, cv2.COLOR_BGR2GRAY)
        obj_gray = cv2.cvtColor(obj, cv2.COLOR_BGR2GRAY)
        M0 = findobject_exact(fgimg, obj)
        if M0 == None:
            print 'using feature match'
            M = findobject(fgimg_gray, obj_gray)
        else:
            print 'using exact template match'
            M = M0
            
        if isgoodmatch(M):
          
            fgimg = subtractobject(fgimg, objmask, M, 255) #TODO: subtract object_white
            fgmask = subtractobject(fgmask, objmask, M, 0) #TODO: subtract object_black
            #cv2.imshow("fgimg", fgimg)
            #cv2.imshow("fgmask", fgmask)
            #cv2.waitKey(0)
            #print 'Found object', i       
    return fgimg, fgmask

def croptofg(fgimg, fgmask):
    if (fgimg == None or fgmask == None):
        return None, None
    tlx, tly, brx, bry = fgbbox(fgmask)
    if (tlx == -1 or brx - tlx == 0 or bry - tly == 0): # nothing new in this image
        return None, None
    h,w = fgimg.shape[0:2]
    tlx = int(max(0, tlx-5))
    tly = int(max(0, tly-5))
    brx = int(min(brx+5, w))
    bry = int(min(bry+5, h))
    newobj = cropimage(fgimg, tlx, tly, brx, bry)
    newobjmask = cropimage(fgmask, tlx, tly, brx, bry)
    return newobj, newobjmask

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
    """Return number of foreground pixels in gimg, where bg color denotes the background colors"""
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
    