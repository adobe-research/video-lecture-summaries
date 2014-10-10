'''
Created on Oct 8, 2014

@author: hijungshin
'''
class VisualObject:
    def __init__(self, start_fid, end_fid, tlx, tly, brx, bry, istext=False):
        self.start_fid = start_fid
        self.end_fid = end_fid
        self.tlx = tlx
        self.tly = tly
        self.brx = brx
        self.bry = bry
        self.width = brx - tlx
        self.height = bry - tly
        self.istext = istext
        
    def __init__(self, text, istext=True):
        return
        
    def size(self):
        return (self.width, self.height)
    
    def copy(self):
        return VisualObject(self.start_fid, self.end_fid, self.tlx, self.tly, self.brx, self.bry, self.istext)
    
    def shiftx(self, x):
        self.tlx += x
        self.brx += x
        
    def shifty(self, y):
        self.tly += y
        self.bry += y
        
    def setx(self, x):
        self.tlx = x
        self.brx = self.tlx + self.width
    
    def sety(self, y):
        self.tly = y
        self.bry = self.tly + self.height
        