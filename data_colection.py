import cv2
from cvzone.HandTrackingModule import HandDetector
import numpy as np
import math
import time
import os


wCam,hCam = 720,560
cap = cv2.VideoCapture(0)
detector = HandDetector(maxHands= 1)
cap.set(3,wCam)
cap.set(4,hCam)
cnt = 0
folder = "Data/2"
os.makedirs(folder, exist_ok=True)
offset = 20
imgSize = 300


while True:
    _,img = cap.read()
    
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
        
        if aspectRatio > 1:
            k = imgSize/h
            wCal = math.ceil(k*w)
            imgResize = cv2.resize(imgCrop,(wCal,imgSize))
            imgResizeShape = imgResize.shape
            wGap = math.ceil((imgSize-wCal)/2)
            # if(imgResizeShape[0]>imgSize or imgResizeShape[1]+wGap > imgSize):
            #     continue
            imgWhite[:,wGap:wGap+imgResizeShape[1]] = imgResize
        else :
            k = imgSize/w
            hCal = math.ceil(k*h)
            imgResize = cv2.resize(imgCrop,(imgSize,hCal))
            imgResizeShape = imgResize.shape
            hGap = math.ceil((imgSize-hCal)/2)
            # if(imgResizeShape[0]>imgSize or imgResizeShape[1]+hGap > imgSize):
            #     continue
            imgWhite[hGap:hCal+hGap,:] = imgResize
            
            
        cv2.imshow("crop",imgCrop)  
        cv2.imshow("img White",imgWhite)
    
    
    cv2.imshow("img",img)
    key = cv2.waitKey(10)
    if key  == ord("q"):
        break
    elif key == ord("s"):
        cv2.imwrite(f"{folder}/Image_{time.time()}.jpg",imgWhite)
        cnt+=1
        print(f"cap : {cnt}")
        

