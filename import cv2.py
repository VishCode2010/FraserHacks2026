import cv2
import numpy as np
import serial
import time

# Connect to Arduino (CHANGE COM PORT)
arduino = serial.Serial('COM9', 9600)
time.sleep(2)

cap = cv2.VideoCapture(0)

last_sent = None

def detect_shape(contour):
    peri = cv2.arcLength(contour, True)
    approx = cv2.approxPolyDP(contour, 0.04 * peri, True)

    sides = len(approx)

    if sides == 3:
        return "triangle"
    elif sides == 4:
        return "rectangle"
    else:
        # Check circularity for better circle detection
        area = cv2.contourArea(contour)
        if peri == 0:
            return "unknown"
        circularity = 4 * np.pi * (area / (peri * peri))

        if circularity > 0.7:
            return "circle"
        else:
            return "unknown"

while True:
    ret, frame = cap.read()

    if not ret:
        break

    # Convert to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Blur to reduce noise
    blur = cv2.GaussianBlur(gray, (5, 5), 0)

    # Edge detection
    edges = cv2.Canny(blur, 50, 150)

    # Find contours
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for cnt in contours:
        area = cv2.contourArea(cnt)

        # Ignore small objects
        if area > 1000:
            shape = detect_shape(cnt)

            x, y, w, h = cv2.boundingRect(cnt)

            # Draw rectangle
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            # Put shape text
            cv2.putText(frame, shape, (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

            # Send to Arduino
            if shape == "circle" and last_sent != "R":
                arduino.write(b'R')
                last_sent = "R"
                print("Recycling detected")

            elif shape != "circle" and last_sent != "T":
                arduino.write(b'T')
                last_sent = "T"
                print("Trash detected")

            time.sleep(1)

    cv2.imshow("Frame", frame)
    cv2.imshow("Edges", edges)

    # Press ESC to exit
    if cv2.waitKey(1) == 27:
        break

cap.release()
cv2.destroyAllWindows()