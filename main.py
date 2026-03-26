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

arduino = serial.Serial('COM9', 9600, timeout=1)
time.sleep(2)

cap = cv2.VideoCapture(0)

last_command = None

while True:
    ret, frame = cap.read()
    if not ret:
        break

    input_img = preprocessing(frame)

    prediction = model.predict(input_img, verbose=0)

    class_index = np.argmax(prediction[0])
    confidence = prediction[0][class_index]
    label = class_names[class_index]

    label = label.split(" ", 1)[-1].strip().lower()

    command = None

    if label == "recycling":
        command = "R"
    elif label == "trash":
        command = "T"
    else:
        command = "U"

    if command != last_command:
        arduino.write(command.encode())
        print("Sent:", command, "| Label:", label, "| Confidence:", confidence)
        last_command = command

    cv2.imshow("Webcam", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

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