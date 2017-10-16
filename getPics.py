#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import sys
import base64
import random
import string
import imghdr
import hashlib
import requests
from io import BytesIO
from PIL import Image
from PIL.ExifTags import TAGS
from bs4 import BeautifulSoup
from optparse import OptionParser
try:
    import queue
    from urllib.parse import urlsplit, urljoin
except ImportError:
    import Queue as queue
    from urlparse import urlsplit, urljoin

once = False
needsize = None
donelink = set()
imgshash = set()
keywords = []
lnkqueue = queue.Queue()
b64regex = re.compile(r"data:image/([a-zA-Z]{2,5});base64,(.+)")
headers = {
    "User-Agent": "Mozilla/5.0"
}

def randomStr():
    return "".join(random.sample(string.ascii_letters+string.digits, 10))

def findPage(url):
    try:
        print("[+] Finding images on %s" % url)
        html = requests.get(url, headers=headers).content
        soup = BeautifulSoup(html, "html5lib")
        imgtags = soup.findAll("img")
        if not once:
            for linktag in  soup.findAll("a"):
                link = linktag.get("href")
                if not link:
                    continue
                if "://" not in link:
                    link = urljoin(url, link)
                if keywords and not [key for key in keywords if key in link]:
                    continue
                lnkqueue.put(link)
        donelink.add(url)
        return imgtags
    except Exception:
        return []

def downloadImage(url, path, imgtag):
    try:
        imgsrc = imgtag.get("src")
        if "://" not in imgsrc:
            imgsrc = urljoin(url, imgsrc)
        results = b64regex.match(imgsrc)
        if results:
            imgtype = results.group(1)
            imgdata = base64.b64decode(results.group(2).encode("utf-8"))
            filename = randomStr()
            filename += ".%s" % imgtype
        else:
            imgdata = requests.get(imgsrc, headers=headers).content
            filename = os.path.basename(urlsplit(imgsrc).path)
        filename, imgtype = testImage(imgdata, filename)
        if not filename:
            return
        savepath = os.path.join(path, filename)
        while os.path.exists(savepath):
            savepath = os.path.join(path, randomStr() + imgtype)
        print("[+] Saving image %s..." % savepath)
        with open(savepath, "wb") as f:
            f.write(imgdata)
        return savepath
    except Exception:
        return

def testImage(imgdata, filename):
    imgio = BytesIO(imgdata)
    imgtype = imghdr.what(imgio)
    imghash = hashlib.md5(imgdata).hexdigest()
    if imgtype and imghash not in imgshash:
        imgshash.add(imghash)
        imgtype = ".%s" % imgtype
        if not os.path.splitext(filename)[1]:
            filename += imgtype
        try:
            img = Image.open(imgio)
        except Exception:
            return
        if needsize:
            size = img.width if img.width > img.height else img.height
            if size < needsize:
                return
        info = img._getexif() or {}
        for k, v in info.items():
            if "GPS" in TAGS[k]:
                print("[!!!] %s contains GPS MetaData" % filename)
        return filename, imgtype
    return

def fuckit(path):
    while True:
        try:
            url = lnkqueue.get_nowait()
            if not url or url in donelink:
                continue
        except queue.Empty:
            break
        imgtags = findPage(url)
        for imgtag in imgtags:
            downloadImage(url, path, imgtag)

def main():
    global once, needsize
    parser = OptionParser(usage="Usage: %prog <url> [-p <path> -s <size> -k <link keywork>]")
    parser.add_option("-s", "--size", dest="size", type="int", help="specify the shortest height or width")
    parser.add_option("-k", "--keyword", dest="keyword", type="string", help="specify the link keywords")
    parser.add_option("-o", "--once", dest="once", action="store_true", default=False, help="just one link")
    parser.add_option("-p", "--path", dest="path", type="string", default="images", help="specify a path to store images(default: images)")
    opts, args = parser.parse_args()
    if not args:
        parser.print_help()
        sys.exit(1)
    url = urljoin(args[0], "/") if not urlsplit(args[0]).path else args[0]
    path = opts.path
    once = opts.once
    needsize = opts.size
    if opts.keyword:
        keywords.extend([x.strip() for x in opts.keyword.split(",")])
    if not os.path.exists(path):
        os.mkdir(path)
    lnkqueue.put(url)
    fuckit(path)

if __name__ == "__main__":
    main()


