import cv2

import numpy as np

from threading import Thread
from multiprocessing import Process, Queue
import time

class VideoStream:
    def __init__(self, name, url, fps, rez) -> None:
        self.name = name
        self.url = url
        self.fps = fps
        self.rez = rez
        #self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 100)
        #self.lastImage = cv2.resize(self.cap.read()[1], rez)
        self.lastImage = np.zeros((rez[1], rez[0], 3), dtype='uint8')


        self.lastRead = time.perf_counter()

        self.running = False
        self.zoomed = False

    def threadQueue(self, q, rez):
        print(f"Thread {self.name} started")
        cap = cv2.VideoCapture(self.url)
        while True:
            time.sleep(0.5/self.fps)
            #print(f"{self.name} size: {q.qsize()}")
            if q.qsize() < 10:
                img = cap.read()[1]
                if img is not None:
                    img = cv2.resize(img, rez)
                    q.put(img)

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
        if not self.t.is_alive():
            self.t.join(timeout=1.0)

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

        if time.perf_counter() - self.lastRead >= 1.0/self.fps:
            self.lastRead = time.perf_counter()
            self.readImage()

        return self.lastImage