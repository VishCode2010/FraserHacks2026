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


# from keras.models import load_model  # TensorFlow is required for Keras to work
# import cv2  # Install opencv-python
# import numpy as np

# # Disable scientific notation for clarity
# np.set_printoptions(suppress=True)

# # Load the model
# model = load_model("keras_Model.h5", compile=False)

# # Load the labels
# class_names = open("labels.txt", "r").readlines()

# # CAMERA can be 0 or 1 based on default camera of your computer
# camera = cv2.VideoCapture(0)

# while True:
#     # Grab the webcamera's image.
#     ret, image = camera.read()

#     # Resize the raw image into (224-height,224-width) pixels
#     image = cv2.resize(image, (224, 224), interpolation=cv2.INTER_AREA)

#     # Show the image in a window
#     cv2.imshow("Webcam Image", image)

#     # Make the image a numpy array and reshape it to the models input shape.
#     image = np.asarray(image, dtype=np.float32).reshape(1, 224, 224, 3)

#     # Normalize the image array
#     image = (image / 127.5) - 1

#     # Predicts the model
#     prediction = model.predict(image)
#     index = np.argmax(prediction)
#     class_name = class_names[index]
#     confidence_score = prediction[0][index]

#     # Print prediction and confidence score
#     print("Class:", class_name[2:], end="")
#     print("Confidence Score:", str(np.round(confidence_score * 100))[:-2], "%")

#     # Listen to the keyboard for presses.
#     keyboard_input = cv2.waitKey(1)

#     # 27 is the ASCII for the esc key on your keyboard.
#     if keyboard_input == 27:
#         break

# camera.release()
# cv2.destroyAllWindows()
