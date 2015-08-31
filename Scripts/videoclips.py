'''
Created on Aug 17, 2015

@author: hijungshin
'''

from moviepy.editor import *
import moviepy.video.fx.all as vfx
import util
import processframe as pf

def colormask(colorvideo, tlx, tly, brx, bry):
    """color box, and grayout rest of the area"""
    bwvideo = vfx.blackwhite(colorvideo)
    colorbox = vfx.crop(colorvideo, tlx, tly, brx, bry)
    newvideo = CompositeVideoClip([bwvideo, colorbox.set_position((tlx, tly))])
    return newvideo

def write_video(clipdir, figdir, filename, myvideo, start_sec, end_sec):
    subclip = VideoFileClip(myvideo.filepath).subclip(start_sec, end_sec)
    clipsrc = clipdir + "/" + filename + ".mp4"
    subclip.write_videofile(clipsrc, codec='libx264', audio_codec='aac', temp_audiofile='temp-audio.m4a', remove_temp=True) # Many options...

def write_crop_video(clipdir, figdir, filename, myvideo, start_sec, end_sec, tlx, tly, brx, bry):
    subclip = VideoFileClip(myvideo.filepath).subclip(start_sec, end_sec)
    subclip_crop = vfx.crop(subclip, tlx, tly, brx, bry)
    cropsrc = clipdir + "/" + filename +"_crop.mp4"
    subclip_crop.write_videofile(cropsrc, codec='libx264', audio_codec='aac', temp_audiofile='temp-audio.m4a', remove_temp=True) # Many options...

def write_subline_clips(clipdir, figdir, list_of_sublines, myvideo, scroll_coords):    
    prev_end_sec = 0
    for i in range(0, len(list_of_sublines)):
        subline = list_of_sublines[i]
        filename = "line%i_sub%i"%(subline.line_id, subline.sub_line_id)
        start_sec = prev_end_sec
        if (i < len(list_of_sublines) -1): 
            next_subline = list_of_sublines[i+1]
            end_sec = myvideo.fid2sec(next_subline.obj.start_fid)
        else:
            end_sec = myvideo.endt/1000.0
        subline.video_startt = start_sec
        subline.video_endt = end_sec
        write_video(clipdir, figdir, filename, myvideo, start_sec, end_sec)
        
        lineobj = subline.linegroup.obj
        scrollx = scroll_coords[lineobj.end_fid][0]
        scrolly = scroll_coords[lineobj.end_fid][1]
        
        tlx = lineobj.tlx - scrollx
        tly = lineobj.tly - scrolly
        brx = lineobj.brx - scrollx
        bry = lineobj.bry - scrolly
        write_crop_video(clipdir, figdir, filename, myvideo, start_sec, end_sec, tlx, tly, brx, bry)
        prev_end_sec = end_sec
        