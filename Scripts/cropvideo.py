'''
Created on Jul 1, 2015

@author: hijungshin
'''

from video import Video
import sys
import lecturevisual as lv
import os
from visualobjects import VisualObject
from moviepy.editor import *
import moviepy.video.fx.all as vfx

if __name__ == "__main__":    
    videopath = sys.argv[1]
    panoramapath = sys.argv[2]
    objdir = sys.argv[3]
    scriptpath = sys.argv[4]
    
    [panorama, list_of_linegroups, list_of_sublines, list_of_stcstrokes, 
     list_of_strokes, list_of_chars, list_of_sentences] = lv.getvisuals(videopath, panoramapath, 
                                                                objdir, scriptpath)
    myvideo = Video(videopath)
    
    clipdir = objdir + "/clips"
    if not os.path.exists(os.path.abspath(clipdir)):
        os.makedirs(os.path.abspath(clipdir))
    for subline in list_of_sublines:
        subobj = subline.obj
        lineobj = subline.linegroup.obj
        filename, ext = os.path.splitext(os.path.basename(subline.obj.imgpath))
        outpath1 = clipdir + "/" + filename + "_crop.mp4"
        outpath2 = clipdir + "/" + filename + ".mp4"

        start_t = myvideo.fid2sec(subobj.start_fid)
        end_t = myvideo.fid2sec(subobj.end_fid)
        print 'start', start_t, 'end', end_t
        subclip = VideoFileClip(videopath).subclip(start_t, end_t)
        subclip.volumex(1.5)
        
        subclip_crop = vfx.crop(subclip, lineobj.tlx, lineobj.tly, lineobj.brx, lineobj.bry)
        subclip_crop.write_videofile(outpath1, codec='libx264', audio_codec='aac', temp_audiofile='temp-audio.m4a', remove_temp=True) # Many options...
        
        subclip.write_videofile(outpath2, codec='libx264', audio_codec='aac', temp_audiofile='temp-audio.m4a', remove_temp=True) # Many options...
        