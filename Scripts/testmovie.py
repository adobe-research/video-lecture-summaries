'''
Created on Jul 2, 2015

@author: hijungshin
'''
from moviepy.editor import *
import sys
import moviepy.video.fx.all as vfx
from video import Video
import numpy as np
import util
    
    
    
if __name__ == "__main__":
    input1 = sys.argv[1]
    input2 = sys.argv[2]
    output = sys.argv[3]
    
    myvideo1 = Video(input1)
    video1 = VideoFileClip(input1).subclip(0, 10)
    video2 = VideoFileClip(input2).subclip(0,10)
    
    bwvideo = vfx.blackwhite(video1)
    bwvideo_crop = vfx.crop(bwvideo, 0, 0, 300, 300)
     
#     bwvideo_crop.write_videofile(myvideo1.videoname + "_bw_crop.mp4", codec='libx264', audio_codec='aac', temp_audiofile='temp-audio.m4a', remove_temp=True) 
        
#     bwvideo_crop.set_position((300,300))
#     
#     print 'video pos', video2.pos
#     print 'bwvideo', bwvideo_crop.pos
    newvideo = CompositeVideoClip([video2, bwvideo_crop.set_position((300,300))])
    
    newvideo.write_videofile(output, codec='libx264', audio_codec='aac', temp_audiofile='temp-audio.m4a', remove_temp=True) # Many options...
