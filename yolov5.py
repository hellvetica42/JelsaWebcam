import cv2
import torch
print(f"Setup complete. Using torch {torch.__version__} ({torch.cuda.get_device_properties(0).name if torch.cuda.is_available() else 'CPU'})")
model = torch.hub.load('ultralytics/yolov5', 'yolov5s')

img = cv2.imread('people.jpg')
results = model([img], size=640)
results.print()
results.render()
cv2.imshow("res", results.imgs[0])
cv2.waitKey(0)