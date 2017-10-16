#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import piexif
import threading
from PIL import Image
from optparse import OptionParser

try:
    import Queue as queue
except ImportError:
    import queue

q = queue.Queue()
lock = threading.Lock()

def addtime(time, exif=None):
    if not exif:
         exif = piexif.load(piexif.dump({}))
    exif['Exif'][piexif.ExifIFD.DateTimeOriginal] = time
    exif['Exif'][piexif.ExifIFD.DateTimeDigitized] = time
    return exif

def fuckexif(name, time):
    try:
        img = Image.open(name)
        info = img._getexif()
    except Exception as e:
        if time and '_getexif' in str(e) and os.path.splitext(name)[1].lower() in ('.jpg', '.jpeg'):
            info = addtime(time)
            img.save(name, format="JPEG", exif=piexif.dump(info))
            img.close()
            return True
        lock.acquire()
        print("%s: %s" % (name, e))
        lock.release()
        return False
    if info:
        exif = piexif.load(img.info['exif'])
        exif['GPS'] = {}
        etime = exif['Exif'].get(piexif.ExifIFD.DateTimeOriginal) or exif['Exif'].get(piexif.ExifIFD.DateTimeDigitized)
        if not etime and time:
            exif = addtime(time, exif)
    elif time:
        exif = addtime(time)
    else:
        img.close()
        return True
    exif = piexif.dump(exif)
    img.save(name, exif=exif)
    img.close()
    return True

def fuck(time):
    while True:
        try:
            path = q.get_nowait()
        except queue.Empty:
            break
        lock.acquire()
        print("Fucking %s..." % path)
        lock.release()
        fuckexif(path, time)
    return

def main():
    parser = OptionParser(usage="Usage: %prog -p <path> [-t <1999:00:00 00:00:00>]")
    parser.add_option("-p", "--path", dest="path", type="string", help="specify picture a path or a directory to remove Exif info")
    parser.add_option("-t", "--time", dest="time", type="string", help="specify time to the file without Exif info") 
    opts, args = parser.parse_args()
    path = opts.path
    time = opts.time
    if not path:
        parser.print_help()
        os.sys.exit(1)
    if os.path.isfile(path):
        print("Fucking %s..." % path)
        fuckexif(path, time)
        return
    for path,dirs,files in os.walk(path):
        for file in files:
            q.put(os.path.join(path, file))
    size = q.qsize()
    for i in range(1 if size < 50 else 25):
        threading.Thread(target=fuck, args=(time,)).start()

if __name__ == "__main__":
    main()










