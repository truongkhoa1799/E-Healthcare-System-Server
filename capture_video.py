import os
import re
import cv2
from parameters import *
from common_functions.identifying_user import IdentifyUser
from common_functions.face_recognition import FaceRecognition

cap = cv2.VideoCapture(0)
para.identifying_user = IdentifyUser()
para.face_recognition = FaceRecognition()

while(True):
    ret, rgb = cap.read()

    fra = 300 / max(rgb.shape[0], rgb.shape[1]) 
    # resized_img = cv2.resize(rgb, (int(rgb.shape[1] * fra), int(rgb.shape[0] * fra)))
    # GRAY_resized_img = cv2.cvtColor(resized_img, cv2.COLOR_BGR2GRAY)

    ret, face_location = para.face_recognition.Get_Location_Face(rgb)
    # print(face_locations)
    # print(resized_img.shape)

    if ret == 0:
        top = face_location[0]
        bottom = face_location[2]
        left = face_location[3]
        right = face_location[1]

        mask_face = rgb[top:bottom, left:right]

        embedded_img = para.face_recognition.Encoding_Face(mask_face)
        
        cv2.rectangle(rgb, (left, top), (right, bottom) , (2, 255, 0), 2)

    cv2.imshow('frame', rgb)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()