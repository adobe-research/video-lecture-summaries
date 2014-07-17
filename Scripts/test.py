#!/usr/bin/env python
import numpy as np
import cv2
import sys
import processframe as pf
from matplotlib import pyplot as plt
import os

if __name__ == "__main__":
    
    dir_path = sys.argv[1]
    filelist = os.listdir(sys.argv[1])
    imagefiles = []
    for filename in filelist:
        if ".png" in filename:
            imagefiles.append(filename)
            
    gray_objs = []
    
    processed_path = dir_path + "\\emph"
    if not os.path.exists(processed_path):
        os.makedirs(processed_path)


    for i in range(0, len(imagefiles) - 1):
        img_path1 = dir_path + "\\" + imagefiles[i]
        print imagefiles[i]
        #img_path2 = dir_path + "\\" + imagefiles[i+1]
        img1 = cv2.imread(img_path1)
        #img2 = cv2.imread(img_path2)
        gray_img1 = cv2.imread(img_path1, 0)
        #gray_img2 = cv2.imread(img_path2, 0)
        
        index = 0
        for gray_obj in gray_objs:
            M = pf.detectobject(gray_img1, gray_obj)
            if M == None:
                index += 1
                continue
            gray_img1 = pf.removetemplate(gray_img1, gray_obj, M)
            cv2.imwrite(dir_path+"\\objects\\temp"+str(i)+"_"+str(index)+".jpg", gray_img1)
            index += 1

        #find important object in img            
        tlx, tly, brx, bry = pf.importantregion(gray_img1)
        if tlx < 0: #no important region, save entire image
            cv2.imwrite(processed_path+"\\capture"+str(i)+".png", img1)
            
        else:
            gray_obj1 = pf.cropimage(gray_img1, tlx, tly, brx, bry)
            gray_objs.append(gray_obj1)
            obj1 = pf.cropimage(img1, tlx, tly, brx, bry)
            gray_img1[tly:bry, tlx:brx] = obj1   
    
            cv2.imwrite(processed_path+"\\capture"+str(i)+".png", gray_img1)
        
        
        
          
    #templates = []
    #for i in range(0,len(filelist),1):
    #    
    #    if ".png" in imagefile or ".jpg" in imagefile:
    #        
    #img1_path = sys.argv[1]
    #img2_path = sys.argv[2]
    #
    #img1 = cv2.imread(img1_path)
    #img2 = cv2.imread(img2_path)
    #
    #img1_gray = cv2.imread(img1_path, 0)
    #img2_gray = cv2.imread(img2_path, 0)
    #
    #threshval = 200
    #ret1,thresh1 = cv2.threshold(img1_gray,threshval,255,cv2.THRESH_BINARY)
    #ret2,thresh2 = cv2.threshold(img2_gray,threshval,255,cv2.THRESH_BINARY)
    #
    ## detect keypoints and descriptors in thresh1
    #surf = cv2.SURF(50)
    #surf.upright = True
    #kp1, d1 = surf.detectAndCompute(img1_gray, None)
    #
    ## get its bounding box and crop    
    #pointsx = []
    #pointsy = []
    #for kp in kp1:
    #    pointsx.append(int(kp.pt[0]))
    #    pointsy.append(int(kp.pt[1]))
    #minx = np.amin(pointsx)
    #miny = np.amin(pointsy)
    #maxx = np.amax(pointsx)
    #maxy = np.amax(pointsy)
    #
    #f_img1_gray = pf.cropimage(img1_gray, minx, miny, maxx, maxy)
    #cv2.imwrite("f1_crop.png", f_img1_gray)
    #f_img1 = pf.cropimage(img1, minx, miny, maxx, maxy)
    #M = pf.detectobject(img2_gray, f_img1_gray)
    #if M != None:
    #    diff = pf.removetemplate(img2, f_img1, M)
    #else:
    #    print 'here'
    #
    #cv2.imwrite('diff2.png', diff)
        
    #h,w = f_img1_gray.shape
    #pts = np.float32([ [0,0],[0,h-1],[w-1,h-1],[w-1,0] ]).reshape(-1,1,2)
    #dst = cv2.perspectiveTransform(pts,M)
    #minx2 = dst.min(0)[:,0]
    #miny2 = dst.min(0)[:,1]
    #maxx2 = dst.max(0)[:,0]
    #maxy2 = dst.max(0)[:,1]
    #
    #minx2, miny2, maxx2, maxy2 = pf.detectobject(img2_gray, f_img1_gray)
    #
    ##cv2.rectangle(img2_gray, (minx2, miny2), (maxx2, maxy2), 0, 3)
    ##cv2.imwrite("img2_f1.png", img2_gray)
    #
    #print img2_gray.shape
    #img_mask = np.zeros(img2_gray.shape, dtype=np.uint8)
    #print img_mask
    #print img_mask.shape
    #img_mask[miny2:maxy2, minx2:maxx2] = 255
    #img2_gray_wo_f1 = cv2.inpaint(img2_gray, img_mask, 3, 0)
    #
    #
    ##img2_gray_wo_f1 = pf.whiteout(img2_gray, minx2, miny2, maxx2, maxy2)
    #cv2.imwrite("img2_wo_f1.png", img2_gray_wo_f1)
    #
    #surf2= cv2.SURF(5000)
    #kp1, d1 = surf2.detectAndCompute(img2_gray_wo_f1, None)
    #
    ## get its bounding box and crop    
    #pointsx = []
    #pointsy = []
    #for kp in kp1:
    #    pointsx.append(int(kp.pt[0]))
    #    pointsy.append(int(kp.pt[1]))
    #minx = np.amin(pointsx)
    #miny = np.amin(pointsy)
    #maxx = np.amax(pointsx)
    #maxy = np.amax(pointsy)
    #
    #my_image = pf.cropimage(img2_gray_wo_f1, minx, miny, maxx, maxy)
    #cv2.imwrite("test.png", my_image)

    