#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import piexif

def check(path):
    try:
        exif = piexif.load(path)
    except Exception:
        return False
    if exif['GPS']:
        print(path, exif['GPS'])
        return True
    return False

def main():
    if not sys.argv[1:]:
        print("Usage: %s <path>" % sya.argv[0])
        sys.exit(1)
    path = sys.argv[1]
    if os.path.isfile(path):
        check(path)
        return
    for p,d,f in os.walk(path):
        for file in f:
            check(os.path.join(p, file))
    return

if __name__ == "__main__":
    main()
