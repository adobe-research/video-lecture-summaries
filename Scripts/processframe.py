#!/usr/bin/env python
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import cv2
import logging
from PIL import Image
import sys
import scipy as sp
import cluster
from itertools import cycle
import util
import math
from nltk.tbl import template 

logging.basicConfig(stream=sys.stderr, level=logging.ERROR)

def importantregion(gray_img, path=None, index=0):
    sift = cv2.SIFT(1000, 3, 0.12, 12)
    kp, d = sift.detectAndCompute(gray_img, None)
    if (path != None):
        img_kp_img = cv2.drawKeypoints(gray_img, kp, None, (255, 0, 0), 0)
        cv2.imwrite(path + "\\object_features" + ("%06i" % index) + ".jpg", img_kp_img)            
        
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

def fit_mask_to_img(image, mask, tlx, tly):
    h, w = image.shape[:2]    
    fitmask = np.zeros((h,w), dtype=np.uint8)
    maskh, maskw = mask.shape
    fitmask[tly:tly+maskh, tlx:tlx+maskw] = mask
    return fitmask
    
        
def highlight(image, mask, (r, g, b, a)=(23, 175, 251, 100)):
   
    # Create a semi-transparent highlight layer the size of image    
    h, w, bgra = image.shape  
    layer = np.empty((h, w, 4), dtype=np.uint8)
    layer[:, :, 0] = r
    layer[:, :, 1] = g
    layer[:, :, 2] = b
    layer[:, :, 3] = a
    
    blurmask = expandmask(mask)
    layer = maskimage(layer, blurmask)
        
    fg_mask = fgmask(image)
    fgimg = alphaimage(image, fg_mask)
    img = Image.fromarray(fgimg, "RGBA")
    b, g, r, a = img.split()
    
        
    img = Image.merge("RGBA", (r, g, b, a))
    
    highlight = Image.fromarray(layer, "RGBA")
    result = Image.alpha_composite(img, highlight) 
    r, g, b, a = result.split()    
    data = np.empty((h, w, 4), dtype=np.uint8)
    data[:, :, 0] = b
    data[:, :, 1] = g
    data[:, :, 2] = r
    data[:, :, 3] = a
    
    return data
    
    
def removetemplate(gray_img, gray_obj, M):
    rows, cols = gray_img.shape[0:2]
    neg_warp_obj = cv2.warpPerspective(255 - gray_obj, M, (cols, rows))
    
    neg_img = 255 - gray_img
    negdiff = np.minimum(neg_img, cv2.absdiff(neg_img, neg_warp_obj))
    diff = 255 - negdiff
    
    # h1,w1 = neg_warp_obj.shape
    # h2,w2 = neg_img.shape
    # h3,w3 = diff.shape
    # view = sp.zeros((max(h1, h2, h3), w1+w2+w3), sp.uint8)
    # view[:h1, :w1] =neg_warp_obj
    # view[:h2, w1:w1+w2] = neg_img
    # view[:h3, w1+w2:w1+w2+w3] = negdiff
    # cv2.namedWindow("remove template", cv2.WINDOW_NORMAL)
    # cv2.imshow("remove template", view)
    # cv2.waitKey(0)
    
    return diff

def subtractlogo(frame, logo, color=None):
    gray_logo = util.grayimage(logo)
    wlogo, hlogo = gray_logo.shape[::-1]
    topleft = find_object_exact_inside(frame, logo, 0.90)
    frame_copy = frame.copy()
    if  topleft == None:
#         util.showimages([frame], "no logo")
        return frame_copy
    else:
#         print 'logo detected'
        tlx = topleft[0]
        tly = topleft[1]
    brx = tlx + wlogo
    bry = tly + hlogo
    if color is None:
        frame_copy[tly:bry, tlx:brx] = cv2.absdiff(frame[tly:bry, tlx:brx], logo)
    else:
        logomask = fgmask(logo, 25, 255, True)
#         logomask = cv2.bitwise_not(logomask)
        logomask = fit_mask_to_img(frame_copy, logomask, tlx, tly)
#         util.showimages([logomask], "logomask")
        frame_copy[logomask != 0] = color
#     util.showimages([frame, frame_copy], "processframe:subtractlogo")
    return frame_copy 

def fgmask(image, threshold=200, var_threshold=255, inv=False):
#     if (threshold is None): 
#         threshold = 225
#     if (var_threshold is None):
#         var_threshold = 255
#     if (inv is None):
#         inv = False
    var = np.var(image, 2, dtype=np.uint8)    
    ret, var_mask = cv2.threshold(var, var_threshold, 255, cv2.THRESH_BINARY)       
    # cv2.imshow("var_mask", var_mask)
    # cv2.waitKey(0)
    img2gray = util.grayimage(image)
    
    ret, lum_mask = cv2.threshold(img2gray, threshold, 255, cv2.THRESH_BINARY_INV)    
    mask = cv2.bitwise_or(var_mask, lum_mask)
    if (inv):
        mask = cv2.bitwise_not(mask)
    return mask



def fgbbox(mask):   
    cols, rows = np.where(mask != 0)
    if (len(cols) == 0 or len(rows) == 0 ):
        return (-1, -1, -1, -1)
    tlx = min(rows)
    brx = max(rows)
    tly = min(cols)
    bry = max(cols)
    return (tlx, tly, brx, bry)

def maskimage_white(image, mask):
    # mask is a single channel array; mask_region is whited
    maskimg = cv2.bitwise_and(image, image, mask=mask)
    inv_mask = cv2.bitwise_not(mask)
    maskimg = cv2.bitwise_not(maskimg, maskimg, mask=inv_mask)
    return maskimg

def maskimage(image, mask):
    # mask is a single channel array; mask_region is blacked
    maskimg = cv2.bitwise_and(image, image, mask=mask)
    return maskimg

def alphaimage(image, mask):    
    h, w = image.shape[:2]
    result = np.empty((h, w, 4), dtype=np.uint8)
    result[:, :, 0:3] = image[:,:,0:3]
    result[:, :, 3] = mask
    return result
    

def expandmask(mask, width=10):
    kernel = np.ones((width, width), np.float32) / (width * width)
    blurmask = cv2.filter2D(mask, -1, kernel)
    blurmask[blurmask != 0] = 255
    return blurmask

def subtractobject(image, objmask, M, emptycolor=0):    
    rows, cols = image.shape[0:2]    
    warpmask = cv2.warpPerspective(objmask, M, (cols, rows))
    warpmask = cv2.bitwise_not(warpmask)
    kernel = np.ones((10, 10), np.float32) / 100
    blurmask = cv2.filter2D(warpmask, -1, kernel)
    blurmask[blurmask != 255] = 0
    
    subimage = cv2.bitwise_and(image, image, mask=blurmask)   
    subimage[blurmask == 0] = emptycolor    
     
    return subimage



def find_template_ctr(frame, template):
    """Return center of template location in side frame"""
    grayframe = util.grayimage(frame)
    graytemp = util.grayimage(template)
    wtemp, htemp = graytemp.shape[::-1]
    top_left = find_object_exact_inside(frame, template)
    if (top_left == None):        
        return None
    else:
        center = (top_left[0] + wtemp / 2, top_left[1] + htemp / 2)
    return center    

def find_best_match_inside(img, obj):
    """obj must be inside img"""
    """This method does work, but is very slow"""
    objh, objw = obj.shape[:2]
    imgh, imgw = img.shape[:2]
    mindiff = float("inf")
    minloc = (-1, -1)
    for x in range(0, (imgw-objw)+1):
        for y in range(0, (imgh-objh)+1):
            diff = cv2.absdiff(obj, img[y:y+objh, x:x+objw])
            diff = cv2.min(diff, obj)
            score = np.sum(diff)
            if (score < mindiff):
                mindiff = score
                minloc = (x,y)
                
    cv2.rectangle(img, (minloc[0],minloc[1]), (minloc[0]+objw, minloc[1]+objh), (255,255,255), 2)
    util.showimages([obj, img], "pf.find_best_match_inside")
    return minloc

def find_object_appx(img, obj, thres=-1):
    sift = cv2.SURF(0)
    gray_img = util.grayimage(img)
    gray_obj = util.grayimage(obj)
    kp1, d1 = sift.detectAndCompute(gray_obj, None)
    kp2, d2 = sift.detectAndCompute(gray_img, None)
    
#     obj_kp_img = cv2.drawKeypoints(gray_obj, kp1, None, (255, 0, 0), 0)
#     img_kp_img = cv2.drawKeypoints(gray_img, kp2, None, (255, 0, 0), 0)

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
    
    match_img = drawMatches(gray_obj, gray_img, kp1, kp2, matches)
    util.showimages([match_img])
    src_pts = np.float32([kp1[m.queryIdx].pt for m in matches])
    dst_pts = np.float32([kp2[m.trainIdx].pt for m in matches])
    
    M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
    # num_in = mask.ravel().tolist().count(1)    
    # logging.info("# Inliers: %i", num_in)
    #
    # if (num_in < len(kp1)*0.5):
    #    print 'Warning: less than half of object features are inliers'        
    #
    # (h1, w1) = gray_obj.shape[:2]
    # (h2, w2) = gray_img.shape[:2]
    # image = np.zeros((max(h1, h2), w1 + w2), np.uint8)
    # image[:h1, :w1] = gray_obj
    # image[:h2, w1:w1+w2] = gray_img
    return M    
     
def find_object_appx_thres(img, obj, thres=None):
    """Find approximate match using feature-match and return transformation matrix"""
    gray_img = util.grayimage(img)
    gray_obj = util.grayimage(obj)
    
    """Return 3x3 transformation matrix which transforms gray_obj to match inside gray_img
    Return None if no good match"""    
    sift = cv2.SIFT()
    kp1, d1 = sift.detectAndCompute(gray_obj, None)
    kp2, d2 = sift.detectAndCompute(gray_img, None)
    
    bf = cv2.BFMatcher(cv2.NORM_L2, True)
    if d1 == None or d2 == None:
        print 'no matches'
        return None
    
    logging.info("gray_obj # features: %i", len(kp1))
    logging.info("gray_img # features: %i", len(kp2))
    
    matches = bf.match(d1, d2)
    dist = [m.distance for m in matches]
    if (len(dist) < 0):
        print "Not enough matches: ", len(dist)
        return None
    
    if (thres==None):
        thres_param = 0.5
    else:
        thres_param = thres
        thres_dist = (sum(dist) / len(dist)) * thres_param
        good_matches = [m for m in matches if m.distance < thres_dist]
    
        logging.info("good match threshold: sum(dist)/len(dist)* %f = %f", thres_param, thres_dist)
        logging.info("Number of matches: %i", len(matches))
        logging.info("Number of good matches: %i", len(good_matches))
        
        if (len(good_matches) <= 4):
            print 'not enough good match'
            return None
        
        good_matches = sorted(good_matches, key=lambda x:x.distance)
    #     match_img = drawMatches(gray_obj, gray_img, kp1, kp2, good_matches)
    #     util.showimages([match_img])
        
        src_pts = np.float32([kp1[m.queryIdx].pt for m in good_matches])
        dst_pts = np.float32([kp2[m.trainIdx].pt for m in good_matches])
        M, mask = cv2.findHomography(src_pts, dst_pts, cv2.LMEDS)
        if (mask.ravel().tolist().count(1) < len(good_matches) * 0.3):
            logging.info("mask count %i", mask.ravel().tolist().count(1))
            logging.info("no good transform")
            return None
        return M
    
    if (thres<0):
        src_pts = np.float32([kp1[m.queryIdx].pt for m in matches])
        dst_pts = np.float32([kp2[m.trainIdx].pt for m in matches])
        M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
        return M

def drawKeypointClusters(img, n_kp, labels):          
    unique_labels = set(labels)   
    n_clusters_ = len(unique_labels)    
    colors = cycle([(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255), (0, 255, 255)])
    for k, col in zip(unique_labels, colors):
        class_members = labels == k
        img = cv2.drawKeypoints(img, n_kp[class_members], None, col, 4)
    return img

def isgoodmatch(M):
    if M == None:
        return False

    unitsquare = np.array([[0, 0], [1, 0], [1, 1], [0, 1]], dtype='float32')
    unitsquare = np.array([unitsquare])
    tsquare = cv2.perspectiveTransform(unitsquare, M)    
    tarea = cv2.contourArea(tsquare)
    print 'tarea = ', tarea
    if tarea < 0.5 or tarea > 5:
        print "Not a good homography, scaling factor:", tarea
        return False
    return True

def find_object_exact_inside(img, template, threshold=0.90):
    """Return the top left corner of the rectangle that matches exact template INSIDE img"""  
    gray_img = util.grayimage(img)
    gray_template = util.grayimage(template)
    w, h = gray_template.shape[::-1]    
    # Apply template Matching
    res = cv2.matchTemplate(img, template, cv2.TM_CCORR_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    top_left = max_loc
    bottom_right = (top_left[0] + w, top_left[1] + h)
#     img_copy = img.copy()
#     cv2.rectangle(img_copy, top_left, bottom_right, 255, 2)
#     util.showimages([img_copy, template])
    """threshold khan = 0.75, tecmath = 0.25 """   
#     print max_val
    if (max_val < threshold):
# #         print max_val
# #         util.showimages([img])        
        logging.info("Exact match NOT found: %f", max_val)        
        return None
    else:
        logging.info("Exact match found: %f", max_val)        
    
    return top_left

def find_object_exact(fgimg, obj, threshold = 2.0):
    """Return translation matrix for exact template match, including partial overlap"""
    imgh, imgw = fgimg.shape[:2]
    objh, objw = obj.shape[:2]
    
    if (len(fgimg.shape) == 3):        
        img = np.ones((imgh + 2 * objh, imgw + 2 * objw, 3), dtype=np.uint8) * 0 
        img[objh:objh + imgh, objw:objw + imgw, :] = fgimg[:, :, :3]
    else:
        img = np.ones((imgh + 2 * objh, imgw + 2 * objw), dtype=np.uint8) * 0  # use 255?
        img[objh:objh + imgh, objw:objw + imgw] = fgimg[:, :]
    
    # util.showimages([img, obj])
    
    res = cv2.matchTemplate(img, obj, cv2.TM_SQDIFF)
    # plt.imshow(res,cmap = 'gray')
    # plt.show()
    # cv2.waitKey(0)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    min_val = math.sqrt(min_val) / (objh * objw)
    if (min_val > threshold):
        logging.info("Exact match NOT found: %f", min_val)
        return None
    else:
        logging.info("Exact match found: %f", min_val)        
    top_left = min_loc
    
    # print 'top left', top_left
    # print min_val
    # cv2.imshow("obj", obj)
    # cv2.imshow("img", img)   
    # cv2.imshow("res", res)
    # cv2.waitKey(0)
              
    M = np.identity(3, dtype=np.float32)
    M[0, 2] = top_left[0] - objw
    M[1, 2] = top_left[1] - objh
        
    # h,w = obj.shape[0:2]
    # bottom_right = (top_left[0] + w, top_left[1] + h)
    # cv2.imshow("object", obj_gray)
    # cv2.rectangle(fgimg_gray, top_left, bottom_right, 0, 2)
    # cv2.imshow("find_object_appx exact", fgimg_gray)
    # cv2.waitKey(0)
    return M

def get_newobj_and_mask(image_and_mask, objlist):
    """objlist-- obj, obj_mask"""
    # show image and mask       
    image = image_and_mask[0]
    fgmask = image_and_mask[1]
    fgimg = maskimage_white(image, fgmask)
    
    if objlist == None:
        return fgimg, fgmask
    for i in range(0, len(objlist)):
        obj = objlist[i][0]
        objmask = objlist[i][1]
        if (obj == None):
            continue

        fgimg_gray = cv2.cvtColor(fgimg, cv2.COLOR_BGR2GRAY)
        obj_gray = cv2.cvtColor(obj, cv2.COLOR_BGR2GRAY)
        M0 = find_object_exact(fgimg, obj)
        if M0 == None:
            # print 'using feature match'
            M = find_object_appx(fgimg_gray, obj_gray)
        else:
            # print 'using exact template match'
            M = M0
            
        if isgoodmatch(M):          
            fgimg = subtractobject(fgimg, objmask, M, 255)  # TODO: subtract object_white
            fgmask = subtractobject(fgmask, objmask, M, 0)  # TODO: subtract object_black              
    return fgimg, fgmask

def getnewobj(image, objlist):
    fg_mask = fgmask(image)
    fgimg = maskimage_white(image, fg_mask)
    
    if objlist == None or len(objlist) == 0:
        return fgimg
    for i in range(0, len(objlist)):
        obj = objlist[i]        
        if (obj == None):
            continue
        objmask = fgmask(obj)
        obj, objmask = croptofg(obj, objmask)
        if (obj == None):
            continue
        fgimg_gray = cv2.cvtColor(fgimg, cv2.COLOR_BGR2GRAY)        
        obj_gray = cv2.cvtColor(obj, cv2.COLOR_BGR2GRAY)
        M = find_object_exact(fgimg, obj)
        # M = None
        if M == None:            
            M = find_object_appx(fgimg_gray, obj_gray)
            
        if isgoodmatch(M):            
            fgimg = subtractobject(fgimg, objmask, M, 255) 
    return fgimg

def croptofg(fgimg, fgmask):
    if (fgimg == None or fgmask == None):
        return None, None
    tlx, tly, brx, bry = fgbbox(fgmask)
    if (tlx == -1 or brx - tlx == 0 or bry - tly == 0):  # nothing new in this image
        return None, None
    h, w = fgimg.shape[0:2]
#     tlx = int(max(0, tlx - 10))
#     tly = int(max(0, tly - 10))
#     brx = int(min(brx + 10, w))
#     bry = int(min(bry + 10, h))
    newobj = cropimage(fgimg, tlx, tly, brx, bry)
    newobjmask = cropimage(fgmask, tlx, tly, brx, bry)
    return newobj, newobjmask

def drawMatches(img1, img2, k1, k2, matches, maxline=100):
    
    h1, w1 = img1.shape[:2]
    h2, w2 = img2.shape[:2]
    view = sp.zeros((max(h1, h2), w1 + w2, 3), sp.uint8)
    view[:h1, :w1, 0] = img1
    view[:h2, w1:, 0] = img2
    view[:, :, 1] = view[:, :, 0]
    view[:, :, 2] = view[:, :, 0]
    numline = 0
    for m in matches:
        color = tuple([sp.random.randint(0, 255) for _ in xrange(3)])
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
    img2 = img[tly:bry+1, tlx:brx+1]
    return img2

def numfgpix_mit(gray_frame):
    return (gray_frame < 200).sum()

def numfgpix_khan(gray_frame):
    ret, thresimg = cv2.threshold(gray_frame, 50, 255, cv2.THRESH_BINARY)
#     util.showimages([thresimg], "numfgpix_khan")
    return np.count_nonzero(thresimg)

def removebg_mit(gray_frame):
    dest = gray_frame.copy()
    dest[gray_frame < 200] = 255
    dest[gray_frame >= 200] = 0
    return dest

def removebg_khan(gray_frame):
    dest = gray_frame.copy()
    dest[gray_frame < 100 ] = 255
    dest[gray_frame >= 100] = 0
    return dest

def numfgpix_thresh(gray, fgthres):
    #ret, threshimg = cv2.threshold(gray, fgthres, 255, cv2.THRESH_BINARY) #for black background
    ret, threshimg = cv2.threshold(gray, fgthres, 255, cv2.THRESH_BINARY_INV) #for white background
    numfg = np.count_nonzero(threshimg)
    logging.debug("#fg pix %i", numfg)
#     util.showimages([threshimg], "processframe::numfgpix_thres")
    return numfg

def numfgpix(img, bgcolor):
    """Return number of foreground pixels in img, where bg color denotes the background colors"""
    sub = np.empty(img.shape)
    print 'img.shape', img.shape
    sub.fill(1)
    for x in bgcolor:
        bg = np.empty(img.shape)
        bg.fill(x)
        sub = np.maximum(np.zeros(img.shape), np.abs(img - bg))
    count = np.count_nonzero(sub)
    return count

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


def calculate_size(size_image1, size_image2, H):
  
  col1, row1 = size_image1
  col2, row2 = size_image2
  min_row = 1
  min_col = 1
  max_row = 0
  max_col = 0
  
  im2T = np.array([[1, 1, 1], [1, col2, 1], [row2, 1, 1], [row2, col2, 1]])
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

def stitch_images(previmage, curimage):  
  if (previmage == None):
    return curimage
  
  curimage = cv2.cvtColor(curimage, cv2.COLOR_BGR2BGRA)
  curimage_gray = cv2.cvtColor(curimage, cv2.COLOR_BGR2GRAY)  
  previmage = cv2.cvtColor(previmage, cv2.COLOR_BGR2BGRA)
  previmage_gray = cv2.cvtColor(previmage, cv2.COLOR_BGR2GRAY)
  
  # util.showimages([curimage, previmage])
  
  (curh, curw) = curimage.shape[:2]
  (prevh, prevw) = previmage.shape[:2]
  
  M = find_object_appx_thres(previmage_gray, curimage_gray, 0.9)
  print M 
  if not isgoodmatch(M):
        print "M is not a good match"
        tx = 0.0
        ty = prevh
        M = np.array([[1.0, 0.0, tx], [0.0, 1.0, ty], [0.0, 0.0, 1.0]])
   
  (warpsize, offset) = calculate_size((prevh, prevw), (curh, curw), M)
  
  curimage_warp = cv2.warpPerspective(curimage, M, (int(warpsize[0]), int(warpsize[1])), borderValue=(0, 0, 0, 0), borderMode=cv2.BORDER_CONSTANT)
  
  xoff = int(offset[0])
  yoff = int(offset[1])
  M0 = np.array([[1.0, 0.0, -(xoff - 1)], [0.0, 1.0, -(yoff - 1)], [0.0, 0.0, 1.0]])      
  previmage_warp = cv2.warpPerspective(previmage, M0, (int(warpsize[0]), int(warpsize[1])), borderValue=(0, 0, 0, 0), borderMode=cv2.BORDER_CONSTANT)        
  
  # util.showimages([curimage_warp, previmage_warp])
  
  pil_curimage_warp = util.array_to_pil(curimage_warp, "RGBA")  # Image.fromarray(curimage_warp, "RGBA")
  pil_previmage_warp = util.array_to_pil(previmage_warp, "RGBA")  # Image.fromarray(previmage_warp, "RGBA")
  pil_previmage_warp.paste(pil_curimage_warp, (-(xoff - 1), -(yoff - 1)), pil_curimage_warp)
  merged = np.array(pil_previmage_warp)  
  merged = cv2.cvtColor(merged, cv2.COLOR_RGB2BGR)
  return merged
  
def panorama(list_of_frames):
  previmage = list_of_frames[0]
  for i in range(1, len(list_of_frames)):
    print "%i of %i" % (i, len(list_of_frames))
    curimage = list_of_frames[i]
    util.showimages([previmage], "pf::panorama, previmage")
    previmage = stitch_images(previmage, curimage)    
  return previmage

    
def writetext(img, text, bottomleft, fontscale=10.0, color=(0, 0, 0)):
    cv2.putText(img, text, bottomleft, cv2.FONT_HERSHEY_PLAIN, fontscale, color)
    return img

if __name__ == "__main__":
    src = cv2.imread("udacity1_capture.png", 0)  # 3 channel BGR image
    dest = src.copy()
    dest[src < 200] = 0
    dest[src >= 200] = 255
    cv2.imwrite("udactiy1_bg.png", dest)
    cv2.imshow("display", dest)
    cv2.waitKey(0)
    
