'''
Created on Mar 22, 2015

@author: hijungshin
'''
class Label:
    def __init__(self, img, pos):
        self.img = img
        self.pos = pos
        h, w = img.shape[0:2]
        self.tlx = pos[0] - w/2
        self.tly = pos[1] - h/2
        self.brx = self.tlx + w
        self.bry = self.tly + h       
        
    def changepos(self, pos):
        self.pos = pos
        h, w = self.img.shape[0:2]
        self.tlx = pos[0] - w/2
        self.tly = pos[1] - h/2
        self.brx = self.tlx + w
        self.bry = self.tly + h    