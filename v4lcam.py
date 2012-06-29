#!/usr/bin/python
# 
# This file is a wrapper for v4l2capture package written by Fredrik Portstrom.
# <fredrik at jemla se>, http://fredrik.jemla.eu/v4l2capture.
#
# It hides all cumbersome tasks including starting devices, creating buffers 
# and so on, to allow user to focus on more important things, 
# such as manipulating the image fetched from camera.
# 
# written by Yoonseop Kang <e0engoon at gmail com>

import select
import v4l2capture
import time
from PIL import Image

class Cam:
    def __init__(self, w, h, deviceName = '/dev/video0'):
        self.start(w, h, deviceName)

    def start(self, w, h, deviceName):
        self.video = v4l2capture.Video_device(deviceName)

        self.size = self.video.set_format(w, h)

        self.video.create_buffers(1)
        self.video.queue_all_buffers()
        self.video.start()
        select.select((self.video, ), (), ())

        self.image_data = None
        while True:
            try:
                self.image_data = self.video.read_and_queue()
                break
            except:
                continue

    def __del__(self):
        self.close()

    def close(self):
        self.video.close()

    def read(self, as_string=False):
        try:
            self.image_data = self.video.read_and_queue()
        except:
            ''
        if as_string:
            return self.image_data
        else:
            return Image.fromstring("RGB", self.size, self.image_data)

if __name__ == '__main__':
    c = Cam(480, 640)

    for i in range(0, 10):
        im = c.read()
        im.save('%d.jpg' % i)
        print i

