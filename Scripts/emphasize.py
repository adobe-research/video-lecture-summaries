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
    temp_path = dir_path+"\\objects"
    if not os.path.exists(temp_path):
        os.makedirs(temp_path)


    for i in range(0, len(imagefiles)):
        print "image " , i
        img_path1 = dir_path + "\\" + imagefiles[i]
        img1 = cv2.imread(img_path1)
        
        gray_img1 = cv2.imread(img_path1, 0)
        gray_img1_pc = gray_img1.copy()
        
        h,w = gray_img1.shape
        index = 0
        for gray_obj in gray_objs:
            print "object ", index
            M = pf.detectobject(gray_img1_pc, gray_obj)
            if M == None:
                index += 1
                continue
            gray_img1_pc = pf.removetemplate(gray_img1_pc, gray_obj, M)
            cv2.imwrite(temp_path + "\\temp"+("%06i" % i)+"_"+("%06i" % index)+".jpg", gray_img1_pc)
            index += 1

        #find important object in img            
        tlx, tly, brx, bry = pf.importantregion(gray_img1_pc, temp_path, len(gray_objs))
        if tlx < 0: #no important region, save entire image        
            cv2.imwrite(processed_path+"\\capture"+("%06i" % i)+".jpg", img1)
        else:
            tlx = int(max(0, tlx-25))
            tly = int(max(0, tly-25))
            brx = int(min(brx+25, w))
            bry = int(min(bry+25, h))
            #print tlx, tly, brx, bry
            gray_obj1 = pf.cropimage(gray_img1_pc, tlx, tly, brx, bry)
            gray_objs.append(gray_obj1)
            cv2.imwrite(temp_path+"\\object" + ("%06i" % len(gray_objs))+".jpg", gray_obj1)            
            obj1 = pf.cropimage(img1, tlx, tly, brx, bry)
            img = img1.copy()
            img[:,:,0] = gray_img1
            img[:,:,1] = gray_img1
            img[:,:,2] = gray_img1
            img[tly:bry, tlx:brx] = obj1
            cv2.rectangle(img, (tlx,tly), (brx,bry), (0,0,255), 3)
                
            cv2.imwrite(processed_path+"\\capture"+("%06i" % i)+".jpg", img)
        
        

    