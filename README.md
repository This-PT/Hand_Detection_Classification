***Hand Gesture Alarm Clock***

Set an alarm clock with hand gestures. A webcam recognizes a hand sign, and an ESP32 clock adds time to the alarm based on which sign it sees.


*How it works*
Webcam ─> hand detection (cvzone / MediaPipe)
       ─> crop + resize hand to 300×300 on a white square
       ─> Keras classifier (2 gestures)
       ─> publish gesture id over MQTT
       ─> ESP32 receives it ─> updates alarm time ─> buzzer / LED on pin 17

*Python side (test.py)*

Detects one hand, crops it with a 20 px margin, and pastes it onto a 300×300 white square while keeping the aspect ratio, so the classifier always gets the same input size.
Classifies the gesture as 0 or 1, and sends 3 when no hand is visible.
Only publishes when the prediction changes, so the clock is not flooded with messages.

*ESP32 side (clock/clock.ino)*

Subscribes to the MQTT topic and stores the latest gesture id.
Shows elapsed minutes on a 7-segment display.
When the button (pin 12) is pressed: gesture 0 adds 10 minutes to the alarm and gesture 1 adds 15 minutes.
Turns pin 17 on when the alarm time is reached.
Collecting training data

data_colection.py uses the same crop-and-pad step. Press s to save a 300×300 image into Data , and q to quit. The model in `Model/` was trained on images. 

Run it
```bash
pip install -r requirements.txt cvzone paho-mqtt`
python test.py`        # needs a webcam
```
Then flash clock/clock.ino to an ESP32 (set your WiFi name and password first).

Limitations
The clock counts from when the board powers on (millis()), not real time.
Only 2 gestures, trained on a small self-collected dataset.
Uses a public MQTT broker with no authentication, so it's fine for a demo but not for real use.
