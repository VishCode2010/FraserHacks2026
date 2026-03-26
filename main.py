import cv2
import numpy as np

# captures the video
cap = cv2.VideoCapture(0)

# runs the video
while True:

    ret, frame = cap.read()
    if not ret:
        print("Frame is not working. Please fix camera")
        break

    if not cap.isOpened:
        print("Video stream is not initialized")
        break

    image = imread()

    if cv2.waitKey(0) == ord('q'):
        break


