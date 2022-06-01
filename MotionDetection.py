import cv2
import numpy as np

import sys
import time

sys.path.insert(1, '/home/hellvetica/Development/JelsaWebcam/rt-motion-detection-opencv-python')
from detector import MotionDetector
from packer import pack_images

ZOOM_REZ = (1280, 720)
frameCnt = 0
_FPS = 30
if __name__ == '__main__':
    if len(sys.argv) > 1:
        cap = cv2.VideoCapture(sys.argv[1])
        _FPS = int(sys.argv[2])
    else:
        cap = cv2.VideoCapture('https://ch-fra-n12.livespotting.com/vpu/ggazg0ll/g98s254r_720.m3u8')

    detector = MotionDetector(bg_history=200,
                              bg_subs_scale_percent=0.25,
                              group_boxes=False,
                              expansion_step=5,
                              brightness_discard_level=30,
                              movement_frames_history=5,
                              bg_skip_frames=2)

    b_height = 512
    b_width = 512

    res = []

    while True:
        frameCnt += 1
        _, frame = cap.read()
        if frame is None:
            break
        frame = cv2.resize(frame, ZOOM_REZ)

        begin = time.perf_counter()
        boxes, _, movement = detector.detect(frame)

        results = []
        if boxes:
            results, box_map = pack_images(frame=frame, boxes=boxes, width=b_width, height=b_height,
                                           box_filter=lambda b: ((b[2] - b[0]) * (b[3] - b[1])) > 1000)
            # box_map holds list of mapping between image placement in packed bins and original boxes

        ## end

        for b in boxes:
            cv2.rectangle(frame, (b[0], b[1]), (b[2], b[3]), (0, 0, 255), 1)

        end = time.perf_counter()
        res.append(1000 * (end - begin))
        print("StdDev: %.4f" % np.std(res), "Mean: %.4f" % np.mean(res), "Boxes found: ", len(boxes))

        idx = 0
        for r in results:
            idx += 1
            cv2.imshow('packed_frame_%d' % idx, r)

        cv2.imshow('last_frame', frame)
        cv2.imshow('movement', movement)

        end_time = time.perf_counter()
        wait_time = int(max(1.0/_FPS - (end_time-begin), 0) * 1000)
        wait_time = 1 if wait_time == 0 else wait_time

        char = cv2.waitKey(wait_time)
        if char == ord('q'):
            break