# FraserHacks2026

- 🧠 Smart Waste Sorter
🚀 Overview
A real-time smart waste sorting system that uses a webcam and computer vision to classify objects as recycling or trash, then physically sorts them using an Arduino-controlled servo.

🎯 Features
📷 Live webcam input

🎨 Color-based detection (brown = recycling, blue = trash)

🤖 Optional ML integration (Teachable Machine .h5 model)

🔌 Serial communication (Python → Arduino)

⚙️ Physical sorting using a servo motor

🛠️ Tech Stack
Software:

Python

OpenCV (cv2)

NumPy

PySerial

(Optional) TensorFlow / Keras

Hardware:

Arduino (Uno / ESP32)

Servo Motor

USB connection (serial)

🧩 How It Works
Webcam captures live video

Frame is processed using OpenCV

System detects:

Brown → Recycling (R)

Blue → Trash (T)

Python sends command via serial

Arduino receives command and rotates servo

Trash is physically sorted

