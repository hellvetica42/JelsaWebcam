import time
import cv2

SCREEN_REZ = (2560, 1440)
if __name__ == '__main__':
    url = "https://ch-fra-n9.livespotting.com/vpu/ggazg0ll/taelb29k_1080.m3u8"
    cap = cv2.VideoCapture(url)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 100)

    lastImage = cap.read()[1]
    lastRead = time.perf_counter()

    while True:

        if time.perf_counter() - lastRead >= 1.0/20:
            lastRead = time.perf_counter()
            lastImage = cap.read()[1]
            #lastImage = cv2.resize(lastImage, SCREEN_REZ)

        cv2.imshow("Pjaca", lastImage)

        char = cv2.waitKey(1)
        if char == ord('q'):
            break