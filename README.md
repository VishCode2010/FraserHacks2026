# FraserHacks2026

This project is a simple system that can recognize whether something is trash or recycling and then physically sort it.

We use a webcam to look at an object, process it with computer vision (and optionally a trained model), and then send a signal to an Arduino. The Arduino moves a servo to direct the item into the correct bin.

Why we made it
Sorting waste properly is a real problem, and people often get it wrong. We wanted to build something interactive that shows how automation + AI can help with sustainability in a practical way.


How it works (high level)
- Webcam captures live video
- Python processes the frame
- Detects whether it is trash or recycling
- Signal is sent to arduino
- A panel turns and object is sorted

Python/software:
- OpenCV
- NumPy
- PySerial
- (Optional) TensorFlow / Keras model

Hardware:
- Arduino
- Servo motor
- USB connection
