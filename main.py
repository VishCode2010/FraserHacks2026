import cv2
import numpy as np
import serial
import time
from tensorflow.keras.models import load_model

model = load_model("keras_model.h5", compile=False)

with open("labels.txt", "r") as f:
    class_names = [line.strip() for line in f.readlines()]

def preprocessing(frame):
    img = cv2.resize(frame, (224, 224))
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = img.astype(np.float32)
    img = (img / 127.5) - 1.0
    img = np.expand_dims(img, axis=0)
    return img

arduino = serial.Serial("COM9", 9600, timeout=1)
time.sleep(2)

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    raise RuntimeError("Could not open webcam")

# ROI coordinates
x1, y1, x2, y2 = 150, 100, 450, 400

ret, frame = cap.read()
if not ret:
    cap.release()
    arduino.close()
    raise RuntimeError("Could not read initial frame from webcam")

background_roi = frame[y1:y2, x1:x2].copy()

last_command = None

while True:
    ret, frame = cap.read()
    if not ret:
        break

    roi = frame[y1:y2, x1:x2]

    # Compare current ROI to empty background ROI
    diff = cv2.absdiff(roi, background_roi)
    gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 25, 255, cv2.THRESH_BINARY)
    changed_pixels = cv2.countNonZero(thresh)

    # Default values
    command = "U"
    label = "unknown"
    confidence = 0.0

    if changed_pixels >= 5000:
        input_img = preprocessing(roi)
        prediction = model.predict(input_img, verbose=0)

        class_index = np.argmax(prediction[0])
        confidence = float(prediction[0][class_index])
        label = class_names[class_index]

        # Clean label text if labels look like "0 recycling"
        label = label.split(" ", 1)[-1].strip().lower()

        if label == "recycling":
            command = "R"
        elif label == "trash":
            command = "T"
        else:
            command = "U"

    # Send only when command changes
    if command != last_command:
        arduino.write(command.encode())
        print(f"Sent: {command} | Label: {label} | Confidence: {confidence:.2f} | Pixels: {changed_pixels}")
        last_command = command

    # Draw ROI box
    box_color = (0, 255, 0) if changed_pixels >= 5000 else (0, 0, 255)
    cv2.rectangle(frame, (x1, y1), (x2, y2), box_color, 2)

    # Show status text
    text = f"{label} | {confidence:.2f} | cmd={command}"
    cv2.putText(frame, text, (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

    cv2.putText(frame, f"changed_pixels={changed_pixels}", (20, 75),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

    cv2.imshow("Webcam", frame)
    cv2.imshow("Threshold", thresh)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key == ord('b'):
        # Re-capture background ROI when box is empty
        background_roi = frame[y1:y2, x1:x2].copy()
        print("Background reset")

cap.release()
arduino.close()
cv2.destroyAllWindows()
   
# import cv2
# import numpy as np
# import serial
# import time
# from tensorflow.keras.models import load_model

# model = load_model("keras_model.h5", compile=False)

# arduino = serial.Serial('COM9', 9600, timeout=1)
# time.sleep(2)  # give Arduino time to reset

# cap = cv2.VideoCapture(0)

# last_command = None  # prevents sending same command over and over

# while True:
#     ret, frame = cap.read()
#     if not ret:
#         break

#     input_img = preprocessing(frame)

#     prediction = model.predict(input_img)

#     class_index = np.argmax(prediction[0])
#     confidence = prediction[0][class_index]
#     label = class_names[class_index]

#     label = label.split(" ", 1)[-1].strip().lower()

#     command = None

#     if label == "recycling":
#         command = "R"
#     elif label == "trash":
#         command = "T"
#     else:
#         command = "U"

#     # send only if command changed
#     if command != last_command:
#         arduino.write((command + "\n").encode())
#         print("Sent:", command)
#         last_command = command

#     # optional: show webcam
#     cv2.imshow("Camera", frame)

#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break

# cap.release()
# arduino.close()
# cv2.destroyAllWindows()