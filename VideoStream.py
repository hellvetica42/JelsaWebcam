import cv2

import numpy as np

from threading import Thread
from multiprocessing import Process, Queue
import plotext as plt
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
        self.tracked = False


        self.lastRead = time.perf_counter()
        self.tracked = False

        self.running = False
        self.zoomed = False

    def threadQueue(self, q : Queue, rez):
        print(f"Thread {self.name} started")
        cap = cv2.VideoCapture(self.url)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 2)
        qsizes = []
        last_time = time.perf_counter()
        last_plot = time.perf_counter()
        plt_interval = 0.1
        while True:

            if time.perf_counter() - last_plot > plt_interval:
                last_plot = time.perf_counter()
                x = np.arange(len(qsizes))
                #print(qsizes)
                plt.clear_terminal()
                plt.clear_figure()
                plt.plot_size(width=128, height=80)
                plt.plot(x, qsizes)
                plt.show()

            if time.perf_counter() - last_time <= 1.0/self.fps:
                continue
            last_time = time.perf_counter()
            qsizes.append(q.qsize())
            if len(qsizes) > 100:
                qsizes.pop(0)
            #print(f"{self.name} size: {q.qsize()}")


            if q.qsize() < 100:
                ret, img = cap.read()
                if ret:
                    img = cv2.resize(img, rez)
                    q.put(img)
            else:
                while not q.empty():
                    q.get()

    def start(self, zoom=None):
        self.q = Queue()
        self.fpsQ = Queue()
        self.running = True

        rez = self.rez
        if zoom is not None:
            rez = zoom

        self.t = Process(target=self.threadQueue, args=(self.q, rez, self.fpsQ))
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
        #self.stop()
        #self.start(zoom=rez)

    def readImage(self):
        if not self.q.empty():
            self.lastImage = self.q.get()
            self.lastImage = cv2.resize(self.lastImage, self.rez)

    def getImage(self):

        if time.perf_counter() - self.lastRead >= 1.0/self.fps or True:
            self.lastRead = time.perf_counter()
            self.readImage()

        return self.lastImage