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

def absolute_pos(framepos, cursorpos):
    absx = framepos[0] + cursorpos[0]
    absy = framepos[1] + cursorpos[1]
    return (absx, absy)

def get_word_pos(video, word, framepos, cursorpos):
    start_fid = video.ms2fid(word.startt)
    end_fid = video.ms2fid(word.endt)
    posx = 0.0
    posy = 0.0
    fcount = 0
    for i in range(start_fid, end_fid + 1):
        pos = absolute_pos(framepos[i], cursorpos[i])
        posx += pos[0]
        posy += pos[1]
        fcount += 1
    avg_posx = posx / fcount
    avg_posy = posy / fcount
    return (int(avg_posx), int(avg_posy))

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
    cv2.circle(pcopy, pos, 5, (0,0,255), thickness=3)
    util.showimages([pcopy])
    
def show_pos_obj(obj, pos):
    posx = int(pos[0] - obj.tlx)
    posy = int(pos[1] - obj.tly)
    print 'relpos', (posx, posy)
    imgcopy = obj.img.copy()
    cv2.circle(imgcopy, (posx, posy), 5, (0,0,255), thickness=3)
    return imgcopy
    
    
def get_strokes_bfr(list_of_strokes, fid):
    bfr_list_of_strokes = []
    for stroke in list_of_strokes:
        if (stroke.obj.end_fid <= fid):
            bfr_list_of_strokes.append(stroke)
    return bfr_list_of_strokes
    
    
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
    html = WriteHtml(objdir + "/locate_word.html", "Locate Word")
    stopwords = ['here', 'here,', 'Here', 'here.']
    for sentence in list_of_sentences:
        html.opendiv()
        html.paragraph_list_of_words(sentence.list_of_words, stopwords)
        word_id = 0
        for word in sentence.list_of_words:
            if (word.original_word in stopwords):
                pos = get_word_pos(video, word, framepos, cursorpos)
                print 'pos', pos
                list_of_bfr_strokes = get_strokes_bfr(list_of_strokes, video.ms2fid(word.endt))
                stroke = get_closest_stroke(list_of_bfr_strokes, pos)
                subline = stroke.stcgroup.subline
                upto_subline_objs = subline.linegroup.obj_upto_subline(subline.sub_line_id)
                obj = VisualObject.group(upto_subline_objs, figdir, "line%i_upto_sub%i.png"%(subline.linegroup.line_id, subline.sub_line_id))
                img = show_pos_obj(obj, pos)
                imgname = "stc%i_word%i.png"%(sentence.id, word_id)
                util.saveimage(img, figdir, imgname)
                html.image(figdir + "/" + imgname)
                word_id += 1
        html.closediv()
    html.closehtml()
    
    