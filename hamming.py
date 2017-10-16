#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PIL import Image
from functools import reduce

def avhash(imgfile):
    img = Image.open(imgfile).resize((8, 8)).convert("L")
    avg = reduce(lambda x, y: x + y, img.getdata()) / 64
    ans = reduce(lambda x, y: x | (y[1] << y[0]), enumerate(map(lambda i: 0 if i < avg else 1, img.getdata())), 0)
    return ans

def hamming(imgsrc, imgdst):
    h1 = avhash(imgsrc)
    h2 = avhash(imgdst)
    h, d = 0, h1 ^ h2
    while d:
        h += 1
        d &= d - 1
    return h




