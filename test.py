import cv2
from cvzone.HandTrackingModule import HandDetector
from cvzone.ClassificationModule import Classifier
import numpy as np
import math
import json
import os
import tensorflow
import paho.mqtt.client as mqtt
broker = "mqtt-dashboard.com"
topic = "node/data/group99"
sent_to = "group99/u2"
client = mqtt.Client("Python_Client_1")

def on_connect(client, userdata, flags, rc):
    print("✅ Connected to MQTT broker with code:", rc)

def on_message(client, userdata, msg):
    print(f"📩 Received message: {msg.payload.decode()} from topic: {msg.topic}")
    
client.on_connect = on_connect
client.on_message = on_message

client.connect(broker, 1883)
client.loop_start()

wCam,hCam = 720,560
cap = cv2.VideoCapture(0)
detector = HandDetector(maxHands= 1)
classifier = Classifier("Model/keras_model.h5","Model/labels.txt") 
laber = ["1","2"]

cap.set(3,wCam)
cap.set(4,hCam)
cnt = 0
folder = "Data/2"
os.makedirs(folder, exist_ok=True)
offset = 20
imgSize = 300
last_idx = -1

while True:
    _,img = cap.read()
    if not cap.isOpened():
        print("❌ Cannot open webcam.")
        exit()
    hands , img = detector.findHands(img)
    if hands :
        hand = hands[0]
        x,y,w,h = hand['bbox']
        
        imgWhite = np.ones((imgSize,imgSize,3),np.uint8)*255
        wi = len(imgWhite)
        wj = len(imgWhite[0])
        if x-offset <0 or x-offset>wCam or x+w+offset < 0 or x+w+offset > wCam or y-offset <0 or y-offset>hCam or y+h+offset < 0 or y+h+offset > hCam or wi < 0 or wi > hCam or wj < 0 or wj > wCam:
            continue 
        imgCrop = img[y-offset:y+h+offset , x-offset:x+w+offset]
        
        # if(imgCropShape[0]>300 or imgCropShape[1] > 300):
        #     continue
        # print("Crop shape:", imgCrop.shape)
    
        
        aspectRatio = h/w
        idx = -1
        if aspectRatio > 1:
            k = imgSize/h
            wCal = math.ceil(k*w)
            imgResize = cv2.resize(imgCrop,(wCal,imgSize))
            imgResizeShape = imgResize.shape
            wGap = math.ceil((imgSize-wCal)/2)
            # if(imgResizeShape[0]>imgSize or imgResizeShape[1]+wGap > imgSize):
            #     continue
            imgWhite[:,wGap:wGap+imgResizeShape[1]] = imgResize
            prediction , idx =  classifier.getPrediction(imgWhite)
            print(prediction,idx)
        else :
            k = imgSize/w
            hCal = math.ceil(k*h)
            imgResize = cv2.resize(imgCrop,(imgSize,hCal))
            imgResizeShape = imgResize.shape
            hGap = math.ceil((imgSize-hCal)/2)
            # if(imgResizeShape[0]>imgSize or imgResizeShape[1]+hGap > imgSize):
            #     continue
            imgWhite[hGap:hCal+hGap,:] = imgResize
            prediction , idx =  classifier.getPrediction(imgWhite)
            print(prediction,idx)
        if(idx != last_idx):
            client.publish(sent_to, str(int(idx)))
            last_idx = idx
        
        cv2.imshow("crop",imgCrop)  
        cv2.imshow("img White",imgWhite)
    else :
        if last_idx != 3:
            client.publish(sent_to, str(3))
            last_idx = 3
    
    cv2.imshow("img",img)
    key = cv2.waitKey(10)
    if key  == ord("q"):
        break

