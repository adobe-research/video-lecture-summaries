'''
Created on Jul 2, 2015

@author: hijungshin
'''
from moviepy.editor import *
import sys
import moviepy.video.fx.all as vfx
    
if __name__ == "__main__":
    videopath = sys.argv[1]
    audiopath = sys.argv[2]
    outpath = sys.argv[3]
    video = VideoFileClip(videopath).subclip(30,60)
    audio = VideoFileClip(audiopath).subclip(30,60)
    auido = audio.audio.to_audiofile("test-short.ogg", write_logfile=True)
    video.set_audio("test-short.ogg")
    # Make the text. Many more options are available.
#     txt_clip = ( TextClip("My Holidays 2013",fontsize=70,color='white')
#                  .set_position('center')
#                  .set_duration(10) )
    
#     video.set_audio(audio)
    video.volumex(1.5)
#     video.write_videofile(outpath)
    video.write_videofile(outpath, codec='libtheora', audio_codec='aac', temp_audiofile='temp-audio.m4a', remove_temp=True) # Many options...