import time
from queue import Queue 
from threading import Thread

import cv2

from VideoStream import VideoStream

#RESOLUTION = (1280, 720)
SCREEN_REZ = (2560, 1440)
RESOLUTION = (640, 480)
BUFFERSIZE = 100

VideoStreams = [
    VideoStream("Pjaca", "https://ch-fra-n12.livespotting.com/vpu/ggazg0ll/g98s254r_720.m3u8", 25, RESOLUTION),
    VideoStream("Burkovo", "https://ch-fra-n9.livespotting.com/vpu/ggazg0ll/taelb29k_1080.m3u8", 20, RESOLUTION),
    VideoStream("Vrtic1", "https://cdn-004.whatsupcams.com/hls/hr_jelsa01.m3u8", 15, RESOLUTION),
    VideoStream("Vrtic2", "https://cdn-002.whatsupcams.com/hls/hr_jelsa04.m3u8", 12, RESOLUTION),
    VideoStream("CentarOkretna", "https://cdn-004.whatsupcams.com/hls/hr_jelsa06.m3u8", 10, RESOLUTION),
    VideoStream("VelaGospa", "https://cdn-002.whatsupcams.com/hls/hr_jelsa07.m3u8", 10, RESOLUTION)
]

if __name__ == '__main__':

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

    threads = []
    index = 0
    VideoStreams[index].start()

    #for vs in VideoStreams:
    #    vs.start()

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

    #for vs in VideoStreams:
    #    vs.stop()

    VideoStreams[index].stop()
    cv2.destroyAllWindows()





