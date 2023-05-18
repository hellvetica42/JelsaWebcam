import cv2

import numpy as np

from threading import Thread
from ffpyplayer.player import MediaPlayer
from multiprocessing import Process, Queue
import time

class VideoStream:
    def __init__(self, name, url, rez) -> None:
        self.name = name
        self.url = url
        self.rez = rez
        self.lastImage = np.zeros((rez[1], rez[0], 3), dtype='uint8')

        self.tracked = False
        self.running = False
        self.zoomed = False

    def threadQueue(self, q : Queue, rez):
        player = MediaPlayer(self.url)
        while True:
            if q.qsize() < 100:
                img, val = player.get_frame()
                if val != 'eof' and img is not None:

                    img, t = img 
                    w,h = img.get_size()
                    img = np.asarray(img.to_bytearray()[0]).reshape(h,w,3)
                    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)  # Convert the image to BGR format

                    img = cv2.resize(img, rez)
                    q.put(img)

                    time.sleep(val)

    def start(self, zoom=None):
        self.q = Queue()
        self.running = True

        rez = self.rez
        if zoom is not None:
            rez = zoom

        self.t = Process(target=self.threadQueue, args=(self.q, rez))
        self.t.daemon = True
        self.t.start()

    def stop(self):
        self.running = False

        while not self.q.empty():
            self.q.get()

        self.t.terminate()
        time.sleep(0.1)
        self.t.kill()

        self.q.close()

        print(f"Thread {self.name} exited")

    def zoom(self, rez):
        self.rez = rez
        self.stop()
        self.start(zoom=rez)

    def readImage(self):
        if not self.q.empty():
            self.lastImage = self.q.get()

    def getImage(self):
        self.readImage()
        return self.lastImage