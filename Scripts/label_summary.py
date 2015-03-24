'''
Created on Jan 14, 2015

@author: hijungshin
'''

import sys
import lecturevisual
import util
from writehtml import WriteHtml
import os
import process_aligned_json as pjson
from video import Video
from visualobjects import VisualObject
import labelfigure

def get_labeled_img(list_of_prevobjs, list_of_curobjs, list_of_labels): 
    list_of_imgobjs = []
    for obj in list_of_prevobjs:
        grayobj = obj.copy()
        grayobj.img = util.fg2gray(obj.img, 175)
        list_of_imgobjs.append(grayobj)
    for obj in list_of_curobjs:
        list_of_imgobjs.append(obj)
    for label in list_of_labels:
        list_of_imgobjs.append(label)
    img = util.groupimages(list_of_imgobjs)
    return img

def get_subline_img(subline):
    list_of_prevobjs = []
    linegroup = subline.linegroup
    for i in range(0, subline.sub_line_id):
        prevsubline = linegroup.list_of_sublines[i]
        list_of_prevobjs.append(prevsubline.obj)
    
    list_of_curobjs = []
    for stcstroke in subline.list_of_stcstrokes:
        list_of_curobjs.append(stcstroke.obj)
    
    if len(list_of_curobjs) > 1:
        list_of_labels = labelfigure.getlabels(0, len(list_of_curobjs))
        labelfigure.sim_anneal(list_of_curobjs, list_of_labels)
    else:
        list_of_labels = []
    img = get_labeled_img(list_of_prevobjs, list_of_curobjs, list_of_labels)
    return img
    
    
if __name__ == "__main__":
    videopath = sys.argv[1]
    panoramapath = sys.argv[2]
    objdir = sys.argv[3]
    scriptpath = sys.argv[4]
    title = sys.argv[5]
    figdir = objdir + "/label_summary"
    
    [panorama, list_of_linegroups, list_of_sublines, list_of_stcstrokes, 
     list_of_strokes, list_of_chars, list_of_sentences] = lecturevisual.getvisuals(videopath, panoramapath, 
                                                                objdir, scriptpath)
    video = Video(videopath)
    list_of_words = pjson.get_words(scriptpath)
    list_of_stcs = pjson.get_sentences(list_of_words)
    
     
    html = WriteHtml(objdir + "/label_summary.html", "Label Summary Test", stylesheet ="../Mainpage/label_summary.css")
    html.writestring("<h1>%s</h1><br>"%title)
    
    cur_stc_id = 0 
    for subline in list_of_sublines:
        if (len(subline.list_of_sentences) > 0):
            start_stc_id = subline.list_of_sentences[0].id
            if (start_stc_id > cur_stc_id):
                html.opendiv(idstring="c0_wrapper")
                html.opendiv(idstring="c0")
                for i in range(cur_stc_id, start_stc_id):
                    stc = list_of_sentences[i]
                    html.write_list_of_words(stc.list_of_words)
                cur_stc_id = start_stc_id
                html.closediv()
                html.closediv()
        else: #subline.list_of_sentences == 0
            stc = list_of_sentences[cur_stc_id]
            if(stc.end_fid < subline.obj.start_fid):
                html.opendiv(idstring="c0_wrapper")
                html.opendiv(idstring="c0")
                while(stc.end_fid < subline.obj.start_fid):
                    html.write_list_of_words(stc.list_of_words)
                    cur_stc_id += 1
                    stc = list_of_sentences[cur_stc_id]
                html.closediv()
                html.closediv()
        
        html.opendiv(idstring="c1c2_wrapper")
        
        html.opendiv(idstring="c1")
        sublineimg = get_subline_img(subline)
        imgpath = "line%i_sub%i.png"%(subline.line_id, subline.sub_line_id)
        util.saveimage(sublineimg, figdir, imgpath)
        html.image(figdir + "/" + imgpath)
#         subline_startt = video.fid2ms(subline.obj.start_fid)
#         subline_endt  = video.fid2ms(subline.obj.end_fid)
#         html.writestring("<p>%.3f - %.3f</p>"%(subline_startt, subline_endt))
        html.closediv() #c1
        
        html.opendiv(idstring="c2")
        label_id = 0
        for sentence in subline.list_of_sentences:
            html.writestring("<p>")
            if len(subline.list_of_stcstrokes) > 1 and sentence.stcstroke is not None:
                label = '(' + chr(ord('a') + label_id) + ')'
                html.writestring("<b>" + label + "</b> ")
                label_id += 1
            html.write_list_of_words(sentence.list_of_words)
            html.writestring("</p>")
            cur_stc_id = sentence.id+1
        html.closediv() #c2
        html.closediv() #c1c2wrapper
        
    
    if (cur_stc_id < len(list_of_stcs) -1):
        html.opendiv(idstring="c0wrapper")
        html.opendiv(idstring="c0")
        for i in range(cur_stc_id, len(list_of_stcs)):
            html.write_list_of_words(list_of_stcs[i])
#             html.writestring("%.3f - %.3f"%(list_of_stcs[i][0].startt, list_of_stcs[i][-1].endt))
        html.closediv()
        html.closediv()
    
    html.closehtml()