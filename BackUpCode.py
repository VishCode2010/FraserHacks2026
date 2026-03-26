import cv2
import numpy as np
import serial
import time

# -----------------------------
# Arduino Setup
# -----------------------------
arduino = serial.Serial('COM3', 9600, timeout=1)  # change COM port
time.sleep(3)  # wait for Arduino to be ready

# -----------------------------
# Camera Setup
# -----------------------------
cap = cv2.VideoCapture(0)

# -----------------------------
# Color Ranges in HSV
# -----------------------------
# Brown color (for recycling)
lower_brown = np.array([10, 100, 20])
upper_brown = np.array([20, 255, 200])

# Blue color (for trash)  ← CHANGED
lower_blue = np.array([100, 150, 50])
upper_blue = np.array([140, 255, 255])

# Command cooldown
last_sent_time = 0
COMMAND_COOLDOWN = 0.5  # seconds

# -----------------------------
# Main Loop
# -----------------------------
try:
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.resize(frame, (640, int(frame.shape[0]*640/frame.shape[1])))

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Mask for brown
        mask_brown = cv2.inRange(hsv, lower_brown, upper_brown)
        # Mask for blue (replaces red)
        mask_red = cv2.inRange(hsv, lower_blue, upper_blue)

        # Count pixels in each mask
        brown_pixels = cv2.countNonZero(mask_brown)
        red_pixels = cv2.countNonZero(mask_red)

        current_time = time.time()

        # Send command if enough color detected and cooldown passed
        if brown_pixels > 2000 and current_time - last_sent_time > COMMAND_COOLDOWN:
            arduino.write(b'R')
            print("Brown detected → Recycling command sent")
            last_sent_time = current_time

        elif red_pixels > 2000 and current_time - last_sent_time > COMMAND_COOLDOWN:
            arduino.write(b'T')
            print("Blue detected → Trash command sent")
            last_sent_time = current_time

        # Show masks for debugging
        cv2.imshow("Frame", frame)
        cv2.imshow("Brown Mask", mask_brown)
        cv2.imshow("Blue Mask", mask_red)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    cap.release()
    cv2.destroyAllWindows()
    arduino.close()