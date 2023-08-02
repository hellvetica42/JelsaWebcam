import time
import datetime

from ffpyplayer.player import MediaPlayer
import numpy as np
import torch
import pandas as pd

video_urls = {
    "Pjaca": "https://ch-fra-n12.livespotting.com/vpu/ggazg0ll/g98s254r_720.m3u8",
    "Burkovo": "https://ch-fra-n9.livespotting.com/vpu/ggazg0ll/taelb29k_1080.m3u8",
    "Vrtic1": "https://cdn-004.whatsupcams.com/hls/hr_jelsa01.m3u8",
    "Vrtic2": "https://cdn-002.whatsupcams.com/hls/hr_jelsa04.m3u8",
    "CentarOkretna": "https://cdn-004.whatsupcams.com/hls/hr_jelsa06.m3u8", 
    "VelaGospa": "https://cdn-002.whatsupcams.com/hls/hr_jelsa07.m3u8", 
}

def get_data(model):
    print("Getting detections..")
    images = [] 
    for name in video_urls:
        print(f"Getting image from {name}")
        player = None

        while player is None:
            try:
                player = MediaPlayer(video_urls[name])
            except Exception as e:
                print("Failed to create player")
                print(e)
                time.sleep(1)

        time.sleep(1)

        img = None
        while img is None:
            try:
                img, val = player.get_frame()
            except Exception as e:
                print(e)
                time.sleep(1)

        img, t = img
        w,h = img.get_size()
        img = np.asarray(img.to_bytearray()[0]).reshape(h,w,3)
        images.append(img)

    results = model(images, size=640)
    print("Got detections")
    return results.pandas().xyxy
    

if __name__ == "__main__":
    print(f"Setup complete. Using torch {torch.__version__} ({torch.cuda.get_device_properties(0).name if torch.cuda.is_available() else 'CPU'})")
    print("Loading model..")
    model = torch.hub.load('ultralytics/yolov5', 'yolov5m')
    print("Model loaded.")

    detections = get_data(model)
    #Name, Class, Detections, Timestamp
    data = {
        "Name":[],
        "Class":[],
        "Detections":[],
        "Timestamp":[]
    }
    for name, d in zip(video_urls.keys(), detections):
        values = d.name.value_counts()
        for cls, count in values.iteritems():
            data["Name"].append(name)
            data["Class"].append(cls)
            data["Detections"].append(count)
            data["Timestamp"].append(datetime.datetime.now())
    new_df = pd.DataFrame(data)

    df = pd.read_csv('logged_data.csv')
    df = pd.concat([df, new_df])
    df.to_csv('logged_data.csv', index=False)
    

