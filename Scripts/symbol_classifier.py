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
from sklearn.svm import SVC
from visualobjects import VisualObject

STANDARD_SIZE = (50,50)

def crop_and_resize(indir, outdir):
    crop_dir(indir, outdir)
    resize_dir(outdir, outdir)

def pre_process(indir, outdir):
    resize_dir(indir, outdir)
    rgb_2_binary(outdir, outdir)

def get_image_data(filename):
#     img = Image.open(filename)
#     img = img.getdata()
#     img = np.array(img)
#     img = np.resize(img, STANDARD_SIZE)
#     print 'img', img
    img = cv2.imread(filename, 0)
#     util.showimages([img], "image")
#     print 'image shape get imagedata', img.shape
    if img  is None:
        return None
    """convert to binary"""
    img /= 255 
    s = img.shape[0] * img.shape[1]
    img_wide = img.reshape(1, s)
    return img_wide[0]

def crop_dir(indir, outdir):
    filelist = os.listdir(indir)
    infiles = []
    for filename in filelist:
        if ".png" in filename: 
            infiles.append(filename)
    
    if not os.path.exists(outdir):
        os.makedirs(outdir)
    
    for i in range(0, len(infiles)):
        img = cv2.imread(indir + "/" + infiles[i])
        fgmask = pf.fgmask(img, 50, 255, True)
        img, mask = pf.croptofg(img, fgmask)
#         util.showimages([img])
        util.saveimage(img, outdir, infiles[i])
    

def resize_dir(input_dir, output_dir):
    filelist = os.listdir(input_dir)
    infiles = []
    for filename in filelist:
        if "obj" in filename and ".png" in filename: 
            infiles.append(filename)
    
    print output_dir
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    txtfile = open(output_dir + "/shape.txt", 'w')
    
    for i in range(0, len(infiles)):
        img = Image.open(input_dir + "/" + infiles[i])
        w, h = img.size
        txtfile.write("%i %i\n" % (int(h), int(w)) )
        
        resized = util.resize_img(img, STANDARD_SIZE)
        resized.save(output_dir + "/" + infiles[i], "PNG")
        
    txtfile.close()
            
def rgb_2_binary(input_dir, output_dir):
    infilenames, infiles = util.get_imgs(input_dir, "obj")
    kernel = np.ones((5,5),np.uint8)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    for i in range(0, len(infilenames)):
        img = cv2.imread(input_dir + "/" + infilenames[i])
        mask = pf.fgmask(img, 225, 255, False)
        closing = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        util.saveimage(closing, output_dir, infilenames[i])



if __name__ == "__main__":

    data = []
    labels = []
    traindir = sys.argv[1]
    objdir = sys.argv[2]
    testdir = objdir + "/symbols_fill"
#     pre_process(objdir, testdir)
    objdir = sys.argv[3]
    panorama = cv2.imread(sys.argv[4])
      
    img_dir_list = os.listdir(sys.argv[1])
    shape_data = []
    for folder in img_dir_list:
        if os.path.isdir(sys.argv[1] + "/" + folder):
            img_file_list = glob.glob(os.path.join(sys.argv[1] + "/" + folder,"*.png"))
            txtfile = sys.argv[1] + "/" + folder + "/shape.txt"
            shape_list = util.list_of_vecs_from_txt(txtfile)
            for image in img_file_list:
                dirname =  os.path.dirname(folder)
                symbol = os.path.basename(folder)
                shape = shape_list.pop(0)
                h = float(shape[0])
                w = float(shape[1])
                h_to_w = h/w
                shape_data.append(h_to_w)
                
                if symbol == "=":
                    data.append(get_image_data(image))
                    labels.append(1)
                else:
                    data.append(get_image_data(image))
                    labels.append(0)
      
    print "read in data done:", len(data), "samples"
    X_train_imdata = data
    y_train = labels
      
    pca = RandomizedPCA(n_components=50)
    X_train_imdata = pca.fit_transform(X_train_imdata)
    X_train = X_train_imdata
    
#     print "add shape feature"
#     X_train = []
#     for i in range(0, len(X_train_imdata)):
#         X_train.append(np.append(X_train_imdata[i], shape_data[i])) 
    
    std_scaler = StandardScaler()
    X_train = std_scaler.fit_transform(X_train)
   
    print "fitting clf"
    clf = SVC(class_weight='auto')
    clf.fit(X_train, y_train)
    print "clf training score", clf.score(X_train, y_train)
      
    test_shape_list = util.list_of_vecs_from_txt(testdir + "/shape.txt")
    test_img_list, test_images = util.get_imgs(testdir, name = "obj") 
    test_shape_data = []
    test_data = []
    test_label = []
    for image in test_img_list:
        if "obj" not in image:
            continue
        imdata = get_image_data(testdir + "/" + image)
        if imdata is not None:
            test_data.append(imdata)
            shape = test_shape_list.pop(0)
            h = float(shape[0])
            w = float(shape[1])
            h_to_w = h/w
            test_shape_data.append(h_to_w)
        else:
            print "symbol_classifier Error: should not enter here"
          
    X_test_imdata = test_data
    X_test_imdata = pca.transform(X_test_imdata)
    X_test = X_test_imdata
#     print "add shape feature"
#     X_test = []
#     for i in range(0, len(X_test_imdata)):
#         X_test.append(np.append(X_test_imdata[i], test_shape_data[i])) 
#     
#     print 'len(X_test[0])', len(X_test[0])
    
    X_test = std_scaler.transform(X_test)
    test_label = clf.predict(X_test)
    match_idx = np.where(test_label == 1)[0]
    print match_idx
      
    list_of_objs = VisualObject.objs_from_file(None, objdir)
    for idx in match_idx:
        img_filename = test_img_list[idx]
        print 'matching file', img_filename
        for obj in list_of_objs:
            if obj.imgpath == img_filename:
#                 print 'obj.imgpath', obj.imgpath, 'img_filename', img_filename
                cv2.rectangle(panorama, (obj.tlx, obj.tly), (obj.brx, obj.bry), (0,0,255), 2)
                h, w = obj.img.shape[:2]
                print 'obj aspect ratio h/w', float(h)/float(w)
                util.showimages([panorama], "detected object")
                continue
#     util.saveimage(panorama, testdir, "equal_02_04_pca50.png")
#     
#     
#         
#         
#         
#         
#         


