import sys
from video import Video
from visualobjects import VisualObject
import util
import os

if __name__ == "__main__":
    videopath = sys.argv[1]
    objdir = sys.argv[2]
    outdir = sys.argv[3]
    outfile = outdir + "/visualobj.json"
    if not os.path.exists(os.path.abspath(outdir)):
        os.makedirs(os.path.abspath(outdir))
    outfile = open(outfile, "w")
    
    video = Video(videopath)
    list_of_objs = VisualObject.objs_from_file(video, objdir)
    
    outfile.write("{\n \"data\":[\n")
    count = 0
    nobjs = len(list_of_objs)
    for obj in list_of_objs:
        count += 1
        util.saveimage(obj.img, outdir, obj.imgpath)
        h, w = obj.img.shape[0:2]
        startt = video.fid2sec(obj.start_fid)
        outfile.write("\
        {\n \
        \"filename\": \"%s\",\n \
        \"x\": %i,\n \
        \"y\": %i,\n \
        \"h\": %i,\n \
        \"w\": %i,\n \
        \"time\": %i\n \
        }" %(obj.imgpath, obj.tlx, obj.tly, h, w, startt))
        if count != nobjs:
            outfile.write(",\n")
    
    outfile.write("\n]\n}")
    outfile.close()
