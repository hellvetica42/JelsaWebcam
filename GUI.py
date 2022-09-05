import sys
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QPushButton, QApplication, QCheckBox, QWidget, QVBoxLayout
from PyQt5.QtCore import QSize, QThread

from VideoStream import VideoStream

import cv2

SCREEN_REZ = (2560, 1440)
RESOLUTION = (640, 480)

VideoStreams = [
    VideoStream("Pjaca", "https://ch-fra-n12.livespotting.com/vpu/ggazg0ll/g98s254r_720.m3u8", 25, RESOLUTION),
    VideoStream("Burkovo", "https://ch-fra-n9.livespotting.com/vpu/ggazg0ll/taelb29k_1080.m3u8", 20, RESOLUTION),
    VideoStream("Vrtic1", "https://cdn-004.whatsupcams.com/hls/hr_jelsa01.m3u8", 15, RESOLUTION),
    VideoStream("Vrtic2", "https://cdn-002.whatsupcams.com/hls/hr_jelsa04.m3u8", 12, RESOLUTION),
    VideoStream("CentarOkretna", "https://cdn-004.whatsupcams.com/hls/hr_jelsa06.m3u8", 10, RESOLUTION),
    VideoStream("VelaGospa", "https://cdn-002.whatsupcams.com/hls/hr_jelsa07.m3u8", 10, RESOLUTION)
]

class StreamThread(QtCore.QThread):
    def __init__(self) -> None:
        QtCore.QThread.__init__(self)
        #create windows and place them appropriately
        x,y = 0,500
        for vs in VideoStreams:
            cv2.namedWindow(vs.name)
            cv2.moveWindow(vs.name, x,y)
            cv2.resizeWindow(vs.name, RESOLUTION[0], RESOLUTION[1])
            x += RESOLUTION[0]
            if x + RESOLUTION[0] > SCREEN_REZ[0]:
                x = 0
                y += RESOLUTION[1]

        index = 0
        VideoStreams[index].start()
        
    def run(self):
        while True:

            #for vs in VideoStreams:
            #    cv2.imshow(vs.name, vs.getImage())
            cv2.imshow(VideoStreams[index].name, VideoStreams[index].getImage())

            char = cv2.waitKey(1)
            if char == ord('q'):
                break
            elif char == ord('n'):
                VideoStreams[index].stop()
                index = (index + 1) % len(VideoStreams)
                VideoStreams[index].start()


        VideoStreams[index].stop()
        cv2.destroyAllWindows()


class Window(QWidget):
    def __init__(self):
        super().__init__()

        self.setMinimumSize(QSize(140, 300))    
        self.setWindowTitle("Webcams") 

        layout = QVBoxLayout()

        self.cbs = {}

        for vs in VideoStreams:
            cb = QCheckBox(vs.name, self)
            #cb.stateChanged.connect(self.clickBox)
            self.cbs[vs] = cb
            layout.addWidget(cb)

        refrestBtn = QPushButton(self)
        refrestBtn.setText("Refresh")
        layout.addWidget(refrestBtn)
        refrestBtn.clicked.connect(self.refresh)

        self.setLayout(layout)


    def refresh(self):
        print("Refreshing")
        videoStream = StreamThread()
        videoStream.start()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWin = Window()
    mainWin.show()
    sys.exit( app.exec_() )