'''
Created on Oct 8, 2014

@author: hijungshin
'''
class VisualObject:
    def __init__(self, start_fid, end_fid, tlx, tly, brx, bry):
        self.start_fid = start_fid
        self.end_fid = end_fid
        self.tlx = tlx
        self.tly = tly
        self.brx = brx
        self.bry = bry
        self.width = brx - tlx
        self.height = bry - tly
        
    def size(self):
        return (self.width, self.height)