'''
Created on Jul 2, 2015

@author: hijungshin
'''
from moviepy.editor import *
import sys
    
if __name__ == "__main__":
    videopath = sys.argv[1]
    outpath = sys.argv[2]
    video = VideoFileClip(videopath).subclip(50,60)
    
    # Make the text. Many more options are available.
    txt_clip = ( TextClip("My Holidays 2013",fontsize=70,color='white')
                 .set_position('center')
                 .set_duration(10) )
    
    result = CompositeVideoClip([video, txt_clip]) # Overlay text on video
    result.write_videofile(outpath,fps=25) # Many options...