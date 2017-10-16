#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import cv2
import shutil
import multiprocessing as process

Cascade = cv2.CascadeClassifier("/usr/share/opencv/haarcascades/haarcascade_frontalcatface.xml")
img_q = process.Queue()
lock = process.Lock()

def findcat(impath):
    try:
        img = cv2.imread(impath)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = Cascade.detectMultiScale(
            gray,
            scaleFactor = 1.02,
            minNeighbors = 3,
            minSize = (500, 500),
            flags = cv2.CASCADE_SCALE_IMAGE
        )
    except Exception as e:
        lock.acquire()
        print("识别出错: %s" % e)
        lock.release()
        return False
    if len(faces):
        return True
    return False

def handle(savepath):
    while True:
        try:
            impath = img_q.get_nowait()
            if not impath:
                continue
        except Exception:
            break
        if findcat(impath):
            if savepath:
                shutil.copyfile(impath, os.path.join(savepath, os.path.basename(impath)))
            lock.acquire()
            print("找到小喵咪: %s" % impath)
            lock.release()

def main():
    if len(os.sys.argv) < 2:
        print("Usage: %s <path or file> [<save path>]" % os.sys.argv[0])
        os.sys.exit(1)
    path = os.sys.argv[1]
    savepath = os.sys.argv[2] if len(os.sys.argv) >= 3 else False
    if not os.path.exists(savepath):
        os.mkdir(savepath)
    if not os.path.isdir(path):
        if findcat(path):
            if savepath:
                shutil.copyfile(path, os.path.join(savepath, os.path.basename(path)))
            print("找到小喵咪: %s" % path)
        else:
            print("没有找到小喵咪...")
        return
    for p,d,f in os.walk(path):
        for imname in f:
            img_q.put(os.path.join(p, imname))
    pool = process.Pool(4)
    for i in range(4):
        pool.apply_async(handle, args=(savepath,))
    pool.close()
    pool.join()
    print("完成任务咯...")

if __name__ == "__main__":
    main()





