#!/usr/bin/env python
from PIL import Image
import glob, os

size = 128, 128

for infile in glob.glob("*.png"):
    file, ext = os.path.splitext(infile)
    im = Image.open(infile)
    im.thumbnail(size, Image.ANTIALIAS)
    im.save(file + ".thumbnail", "PNG")