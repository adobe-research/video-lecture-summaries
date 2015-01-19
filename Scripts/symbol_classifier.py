'''
Created on Jan 15, 2015

@author: hijungshin
'''

from PIL import Image
import numpy as np
import util
import sys
import processframe as pf
import os
import cv2
import glob
from sklearn.decomposition import RandomizedPCA
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import confusion_matrix

STANDARD_SIZE = (50,50)

def pre_process(indir, outdir):
    resize_dir(indir, outdir)
    rgb_2_binary(indir, outdir)

def get_image_data(filename):
#     img = Image.open(filename)
#     img = img.getdata()
#     img = np.array(img)
#     img = np.resize(img, STANDARD_SIZE)
#     print 'img', img
    img = cv2.imread(filename, 0)
    s = img.shape[0] * img.shape[1]
    img_wide = img.reshape(1, s)
    return img_wide[0]

def resize_dir(input_dir, output_dir):
    filelist = os.listdir(input_dir)
    infiles = []
    for filename in filelist:
        if ".png" in filename and "obj" in filename: 
            infiles.append(filename)
            
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    for i in range(0, len(infiles)):
        img = Image.open(input_dir + "/" + infiles[i])
        resized = util.resize_img(img, STANDARD_SIZE)
        resized.save(output_dir + "/" + infiles[i], "PNG")
            
def rgb_2_binary(input_dir, output_dir):
    infilenames, infiles = util.get_imgs(input_dir, "obj")
    kernel = np.ones((5,5),np.uint8)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    for i in range(0, len(infilenames)):
        img = cv2.imread(input_dir + "/" + infilenames[i])
        mask = pf.fgmask(img, 50, 255, True)
        closing = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        util.saveimage(closing, output_dir, infilenames[i])



if __name__ == "__main__":
    
    data = []
    labels = []
    
    img_dir_list = os.listdir(sys.argv[1])
    for folder in img_dir_list:
        if os.path.isdir(sys.argv[1] + "/" + folder):
            img_file_list = glob.glob(os.path.join(sys.argv[1] + "/" + folder,"*.png"))
            for image in img_file_list:
                dirname =  os.path.dirname(folder)
                symbol = os.path.basename(folder)
                count = 0
                if symbol == "=":
                    data.append(get_image_data(image))
                    labels.append(1)
                elif count < 10:
                    """maximum ten examples from other characters"""
                    data.append(get_image_data(image))
                    labels.append(0)
                    count += 1 
    
    print """read in data done"""
    pca = RandomizedPCA(n_components=10)
    std_scaler = StandardScaler()
    X_train = data
    y_train = labels
    X_train = pca.fit_transform(X_train)
    X_train = std_scaler.fit_transform(X_train)
        
    clf = KNeighborsClassifier(n_neighbors=13)
    clf.fit(X_train, y_train)
    print "classifier training done"
    
  

            
    
    
        
        
        
        
        


