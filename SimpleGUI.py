import os

import PySimpleGUI as sg
import cv2
import numpy as np

from VideoStream import VideoStream

#RESOLUTION = (1280, 720)
SCREEN_REZ = (2560, 1440)
RESOLUTION = (640, 480)
ZOOM_REZ = (1280, 720)
BUFFERSIZE = 100

VideoStreams = [
    VideoStream("Pjaca", "https://ch-fra-n12.livespotting.com/vpu/ggazg0ll/g98s254r_720.m3u8", 30, RESOLUTION),
    VideoStream("Burkovo", "https://ch-fra-n9.livespotting.com/vpu/ggazg0ll/taelb29k_1080.m3u8", 20, RESOLUTION),
    VideoStream("Vrtic1", "https://cdn-004.whatsupcams.com/hls/hr_jelsa01.m3u8", 15, RESOLUTION),
    VideoStream("Vrtic2", "https://cdn-002.whatsupcams.com/hls/hr_jelsa04.m3u8", 12, RESOLUTION),
    VideoStream("CentarOkretna", "https://cdn-004.whatsupcams.com/hls/hr_jelsa06.m3u8", 10, RESOLUTION),
    VideoStream("VelaGospa", "https://cdn-002.whatsupcams.com/hls/hr_jelsa07.m3u8", 10, RESOLUTION)
]

def arrangeDisplays():
    x,y = 0,480
    maxY = y
    for vs in VideoStreams:
        if vs.rez[1] > maxY:
            maxY = vs.rez[1]
        if x + vs.rez[0] > SCREEN_REZ[0]:
            x = 0
            y += maxY + 30
        cv2.moveWindow(vs.name, x,y)
        cv2.resizeWindow(vs.name, vs.rez[0], vs.rez[1])
        x += vs.rez[0]


if __name__ == '__main__':
    #create windows and place them appropriately
    x,y = 0,500
    for vs in VideoStreams:
        cv2.namedWindow(vs.name, cv2.WINDOW_AUTOSIZE)

    arrangeDisplays()


    sg.theme('Dark')    

    layout = []
    for vs in VideoStreams:
        layout.append([sg.Checkbox(vs.name, default=False, key=vs.name), 
                        sg.Button("Zoom", key="zoom"+vs.name), sg.Button("Track", key="track"+vs.name)])

    layout.append([sg.Button("Refresh", key="refresh"), sg.Button("Rearrange", key="arrange")])

    window = sg.Window('ControlPanel', layout)

    while True:
        event, values = window.read(timeout=10)

        if event == "refresh":
            for vs in VideoStreams:
                if values[vs.name] and not vs.running:
                    vs.start()
                elif not values[vs.name] and vs.running:
                    vs.stop()
                elif vs.running:
                    vs.stop()
                    vs.start()
        elif event == "arrange":
            arrangeDisplays()
        else:
            for vs in VideoStreams:
                if event == "zoom"+vs.name and vs.running:
                    if not vs.zoomed:
                        vs.zoom(ZOOM_REZ)
                        vs.zoomed = True
                    else:
                        vs.zoom(RESOLUTION)
                        vs.zoomed = False
                    arrangeDisplays()

                elif event == "track"+vs.name:
                    os.system('/usr/bin/python3 tensorflow-human-detectionV2.py ' + vs.url+ ' &')
                    #os.system(f'/usr/bin/python3 MotionDetection.py {vs.url} {vs.fps} &')
        

        for vs in VideoStreams:
            if vs.running:
                cv2.imshow(vs.name, vs.getImage())
                #_, _, w, h = cv2.getWindowImageRect(vs.name)
                #if w != vs.rez[0] or h != vs.rez[1]:
                #    arangeDisplays()

        cv2.waitKey(1)

        if event == sg.WIN_CLOSED:
            for vs in VideoStreams:
                if vs.running:
                    vs.stop()
            break

    
    window.close()
    cv2.destroyAllWindows()

    
