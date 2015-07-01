'''
Created on Jun 30, 2015

@author: Valentina
'''
import fgpixel_objfids as fg
import sys

if __name__ == "__main__":    
    tempdir = sys.argv[1]
    obj_fids = fg.read_obj_fids(sys.argv[2])
    scroll_coords = fg.scroll.read_scroll_coord(sys.argv[3])
    objdir = sys.argv[4]
    fg.get_objects(tempdir, obj_fids, scroll_coords, objdir)