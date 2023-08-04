import PySimpleGUI as sg
import cv2
import numpy as np
import time

#from VideoStream import VideoStream
cv2.namedWindow("TMP", cv2.WINDOW_AUTOSIZE)
cv2.destroyAllWindows()
from FFVideoStream import VideoStream
model = None

#RESOLUTION = (1280, 720)
SCREEN_REZ = (2560, 1440)
RESOLUTION = (640, 480)
#ZOOM_REZ = (1280, 720)
ZOOM_REZ = (1920, 1080)
BUFFERSIZE = 100

VideoStreams = [
    VideoStream("Pjaca", "https://ch-fra-n12.livespotting.com/vpu/ggazg0ll/g98s254r_720.m3u8", RESOLUTION),
    VideoStream("Burkovo", "https://ch-fra-n9.livespotting.com/vpu/ggazg0ll/taelb29k_1080.m3u8", RESOLUTION),
    VideoStream("Vrtic1", "https://cdn-004.whatsupcams.com/hls/hr_jelsa01.m3u8", RESOLUTION),
    VideoStream("Vrtic2", "https://cdn-002.whatsupcams.com/hls/hr_jelsa04.m3u8", RESOLUTION),
    VideoStream("CentarOkretna", "https://cdn-004.whatsupcams.com/hls/hr_jelsa06.m3u8", RESOLUTION),
    VideoStream("VelaGospa", "https://cdn-002.whatsupcams.com/hls/hr_jelsa07.m3u8", RESOLUTION)
]

def arrangeDisplays():
    VideoStreams.sort(key=lambda vs: vs.rez[0]*vs.rez[1], reverse=True)
    for vs in VideoStreams:
        vs.pos = None
    x,y = 0,480 # my vertical display adds extra desktop on my machine
    for i in range(len(VideoStreams)):


        for j in range(len(VideoStreams)):
            if i == j or VideoStreams[j].pos is None:
                continue
            if VideoStreams[j].pos[0] < x+2 <= VideoStreams[j].pos[0] + VideoStreams[j].rez[0]:
                y = VideoStreams[j].pos[1] + VideoStreams[j].rez[1] + 30


        cv2.resizeWindow(VideoStreams[i].name, VideoStreams[i].rez[0], VideoStreams[i].rez[1])
        cv2.moveWindow(VideoStreams[i].name, x, y)
        VideoStreams[i].pos = [x,y]

        x += VideoStreams[i].rez[0]
        if x >= SCREEN_REZ[0]:
            x = 0

        
    #maxY = y
    #for vs in VideoStreams:
    #    if vs.rez[1] > maxY:
    #        maxY = vs.rez[1]
    #    if x + vs.rez[0] > SCREEN_REZ[0]:
    #        x = 0
    #        y += maxY + 30
    #    cv2.moveWindow(vs.name, x,y)
    #    cv2.resizeWindow(vs.name, vs.rez[0], vs.rez[1])
    #    x += vs.rez[0]

def loadModel():
    global model
    import torch
    print(f"Setup complete. Using torch {torch.__version__} ({torch.cuda.get_device_properties(0).name if torch.cuda.is_available() else 'CPU'})")
    model = torch.hub.load('ultralytics/yolov5', 'yolov5m')
    #model.classes = [0, 2, 8]

def inferImage(image):
    im = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = model([im], size=640)
    results.render()
    return cv2.cvtColor(results.imgs[0], cv2.COLOR_RGB2BGR)


if __name__ == '__main__':
    #create windows and place them appropriately
    x,y = 0,500
    for vs in VideoStreams:
        cv2.namedWindow(vs.name, cv2.WINDOW_GUI_NORMAL)
        cv2.imshow(vs.name, np.zeros((RESOLUTION[1], RESOLUTION[0], 3)))

    arrangeDisplays()


    sg.theme('Dark')    

    layout = []
    for vs in VideoStreams:
        layout.append([sg.Checkbox(vs.name, default=True, key=vs.name, size=15), 
                        sg.Button("Zoom", key="zoom"+vs.name, button_color=("black", "gray"), ), 
                        sg.Button("Track", key="track"+vs.name, button_color=("black", "gray"))])

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
            arrangeDisplays()
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
                    window["zoom"+vs.name].update(button_color=("black", "green") if vs.zoomed else ("black", "gray"))

                elif event == "track"+vs.name:
                    if model is None:
                        loadModel()
                    vs.tracked = not vs.tracked
                    window["track"+vs.name].update(button_color=("black", "green") if vs.tracked else ("black", "gray"))
                    #os.system('/usr/bin/python3 tensorflow-human-detectionV2.py ' + vs.url+ ' &')
                    #os.system(f'/usr/bin/python3 MotionDetection.py {vs.url} {vs.fps} &')
        

        for vs in VideoStreams:
            if vs.running:
                resImg = vs.getImage()
                if vs.tracked:
                    resImg = inferImage(resImg)
                cv2.imshow(vs.name, resImg)
                #_, _, w, h = cv2.getWindowImageRect(vs.name)
                #if w != vs.rez[0] or h != vs.rez[1]:
                #    arangeDisplays()

        cv2.waitKey(10)

        if event == sg.WIN_CLOSED:
            for vs in VideoStreams:
                if vs.running:
                    vs.stop()
            break

    
    window.close()
    cv2.destroyAllWindows()