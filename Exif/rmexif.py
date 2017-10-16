#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import piexif
import imghdr
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
    etime = exif['Exif'].get(piexif.ExifIFD.DateTimeOriginal) or exif['Exif'].get(piexif.ExifIFD.DateTimeDigitized)
    if not etime:
        exif['Exif'][piexif.ExifIFD.DateTimeOriginal] = time
        exif['Exif'][piexif.ExifIFD.DateTimeDigitized] = time
    return exif

def fuckexif(name, time):
    if imghdr.what(name) != "jpeg":
        if time and os.path.splitext(name)[1].lower() in ('.jpg', '.jpeg'):
            try:
                img = Image.open(name)
                img.save(name, format="JPEG", exif=piexif.dump(addtime(time)))
                img.close()
                return True
            except Exception as e:
                lock.acquire()
                print("%s: %s" % (name, e))
                lock.release()
                return False
        else:
            lock.acquire()
            print("%s: not JPEG!!!" % name)
            lock.release()
            return True
    try:
        exif = piexif.load(name)
    except Exception:
        if not time:
            return True
        exif = piexif.load(piexif.dump({}))
    try:
        exif['GPS'] = {}
        if time:
            exif = addtime(time, exif)
        piexif.insert(piexif.dump(exif), name)
        return True
    except Exception as e:
        lock.acquire()
        print("%s: %s" % (name, e))
        lock.release()
        return False

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










