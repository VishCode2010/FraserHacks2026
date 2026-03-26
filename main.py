import cv2
import numpy as np

# captures the video
cap = cv2.VideoCapture(0)

# runs the video
while True:

    ret, frame = cap.read()

if cv2.waitKey(0) == ord('q'):
    break
