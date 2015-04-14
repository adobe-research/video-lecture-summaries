'''
Created on Apr 7, 2015

@author: hijungshin
'''

'''
Created on Mar 24, 2015

@author: hijungshin
'''
import cv2
import sys
from video import Video
import process_aligned_json as pjson
import util
import lecturevisual
from writehtml import WriteHtml
from visualobjects import VisualObject

def get_ref_words(sentence):
        
    ref_phrase = ['here']
    ref_words = []
    if sentence.subline is not None:
        return ref_words
    for p in ref_phrase:
        for w in sentence.list_of_words:
            if w.raw_word == p:
                ref_words.append(w)
    return ref_words

def get_label_pos(list_of_sublines, sentence, word, framepos, cursorpos):
    avgpos = get_word_avgpos(sentence.video, sentence, framepos, cursorpos)
    cand_sublines = get_vis_bfr(list_of_sublines, sentence.start_fid)
    subline = get_closest_subline(cand_sublines, avgpos)
    return subline, avgpos

def absolute_pos(framepos, cursorpos):
    absx = framepos[0] + cursorpos[0]
    absy = framepos[1] + cursorpos[1]
    return (absx, absy)

def get_word_avgpos(video, word, framepos, cursorpos):
    start_fid = video.ms2fid(word.startt)
    end_fid = video.ms2fid(word.endt)
    posx = 0.0
    posy = 0.0
    fcount = 0
    for i in range(start_fid, end_fid + 1):
        if framepos[i][0] < 0 or framepos[i][1] < 0 or cursorpos[i][0] < 0 or cursorpos[i][1] < 0:
            continue
        pos = absolute_pos(framepos[i], cursorpos[i])
        posx += pos[0]
        posy += pos[1]
        fcount += 1
    avg_posx = posx / fcount
    avg_posy = posy / fcount
    return (int(avg_posx), int(avg_posy))

def get_word_pos(video, word, framepos, cursorpos):
    start_fid = video.ms2fid(word.startt)
    end_fid = video.ms2fid(word.endt)
    fcount = 0
    pos = []
    for i in range(start_fid, end_fid + 1):
        if framepos[i][0] < 0 or framepos[i][1] < 0 or cursorpos[i][0] < 0 or cursorpos[i][1] < 0:
            continue
        abspos = absolute_pos(framepos[i], cursorpos[i])
        pos.append(abspos)
        fcount += 1
    ratio = float(fcount)/float(end_fid - start_fid + 1)
    return pos, ratio

def get_closest_subline(list_of_sublines, pos):
    mindist = float("inf")
    close_subline = None
    for subline in list_of_sublines:
        dist = util.min_dist_bbox(pos[0], pos[1], subline.obj.tlx, subline.obj.tly, subline.obj.brx, subline.obj.bry)
        if dist < mindist:
            mindist = dist
            close_subline = subline
    return close_subline

def get_closest_stroke(list_of_strokes, pos):
    mindist = float("inf")
    close_stroke = None
    for stroke in list_of_strokes:
        strokex = (stroke.obj.tlx + stroke.obj.brx)/2
        strokey = (stroke.obj.tly + stroke.obj.bry)/2
        dist = (strokex - pos[0]) * (strokex - pos[0]) + (strokey - pos[1]) * (strokey-pos[1])
        if (dist < mindist):
            close_stroke = stroke
            mindist = dist
            
    return close_stroke

    
def show_pos_panorama(panorama, pos):
    pcopy = panorama.copy()
    for p in pos:
        cv2.circle(pcopy, p, 5, (0,0,255), thickness=3)
#     util.showimages([pcopy])
    return pcopy

def show_wordpos_in_stc_panorama(panorama, video, sentence, word, framepos, cursorpos):
    start_fid = video.ms2fid(sentence.startt)
    end_fid = video.ms2fid(sentence.endt)
    imgcopy = panorama.copy()
    for i in range(start_fid, end_fid + 1):
        if framepos[i][0] < 0 or framepos[i][1] < 0 or cursorpos[i][0] < 0 or cursorpos[i][1] < 0:
            continue
        abspos = absolute_pos(framepos[i], cursorpos[i])
        cv2.circle(imgcopy, abspos, 5, (255,0,0), thickness = 2)
    w_start_fid = video.ms2fid(word.startt)
    w_end_fid = video.ms2fid(word.endt)
    for i in range(w_start_fid, w_end_fid+1):
        if framepos[i][0] < 0 or framepos[i][1] < 0 or cursorpos[i][0] < 0 or cursorpos[i][1] < 0:
            continue
        abspos = absolute_pos(framepos[i], cursorpos[i])
        cv2.circle(imgcopy, abspos, 5, (0,0,255), thickness = 2)
    return imgcopy
    
    
def show_pos_obj(obj, pos):
    posx = int(pos[0] - obj.tlx)
    posy = int(pos[1] - obj.tly)
    print 'relpos', (posx, posy)
    imgcopy = obj.img.copy()
    cv2.circle(imgcopy, (posx, posy), 5, (0,0,255), thickness=3)
    return imgcopy

    
def get_vis_bfr(list_of_vis, fid):
    bfr_list_of_vis = []
    for vis in list_of_vis:
        if (vis.obj.end_fid <= fid):
            bfr_list_of_vis.append(vis)
    return bfr_list_of_vis
    
    
if __name__ == "__main__":
    videopath = sys.argv[1]
    panoramapath = sys.argv[2]
    scriptpath = sys.argv[3]
    cursortxt = sys.argv[4]
    frametxt = sys.argv[5]
    objdir = sys.argv[6]
    
    [panorama, list_of_linegroups, list_of_sublines, list_of_stcstrokes, 
     list_of_strokes, list_of_chars, list_of_sentences] = lecturevisual.getvisuals(videopath, panoramapath, 
                                                                objdir, scriptpath)
    
    video = Video(videopath)
    list_of_words = pjson.get_words(scriptpath)
    
    fp = util.list_of_vecs_from_txt(frametxt)
    framepos = []
    for p in fp:
        framepos.append((int(p[0]), int(p[1])))
        
    cp = util.list_of_vecs_from_txt(cursortxt)
    cursorpos = []
    for p in cp:
        cursorpos.append((int(p[0]), int(p[1])))
    
    figdir = objdir + "/locate_word"
    html = WriteHtml(objdir + "/locate_word.html", "Locate Word", stylesheet ="../Mainpage/locate_word.css")
    stopwords = ['here']
    for sentence in list_of_sentences:
        ref_words = get_ref_words(sentence)
        if (len(ref_words) == 0):
            continue    
        html.opendiv()
        html.paragraph_list_of_words(sentence.list_of_words, stopwords)
        word_id = 0
        for word in sentence.list_of_words:
            if (word.raw_word in stopwords):
#                 pos, ratio = get_word_pos(video, word, framepos, cursorpos)
                img = show_wordpos_in_stc_panorama(panorama, video, sentence, word, framepos, cursorpos)
                
#                 list_of_bfr_strokes = get_vis_bfr(list_of_strokes, video.ms2fid(word.endt))
#                 stroke = get_closest_stroke(list_of_bfr_strokes, pos)
#                 subline = stroke.stcgroup.subline
#                 upto_subline_objs = subline.linegroup.obj_upto_subline(subline.sub_line_id)
#                 obj = VisualObject.group(upto_subline_objs, figdir, "line%i_upto_sub%i.png"%(subline.linegroup.line_id, subline.sub_line_id))
#                 img = show_pos_obj(obj, pos)
                imgname = "stc%i_word%i.png"%(sentence.id, word_id)
                util.saveimage(img, figdir, imgname)
                html.opendiv()
#                 html.writestring("%f"%ratio)
                html.image(figdir + "/" + imgname)
                html.closediv()
                word_id += 1
        html.closediv()
    html.closehtml()
    
    