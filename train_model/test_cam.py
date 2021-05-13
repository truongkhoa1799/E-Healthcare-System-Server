import time
import sys
sys.path.append('/Users/khoatr1799/GitHub/E-Healthcare-System-Server/')
from parameters import *
from common_functions.identifying_user import IdentifyUser
from common_functions.face_recognition import FaceRecognition
import cv2

IMG_PATH = '/Users/khoatr1799/GitHub/E-Healthcare-System-Server/Manipulate_Data/Original_Face/train/1/IMG_3415.jpg'

para.face_recognition = FaceRecognition()

img = cv2.imread(IMG_PATH)
start_time = time.time()
ret, face_location = para.face_recognition.Get_Location_Face(img)
print("time to get face: {}".format(time.time() - start_time))
face = img[face_location[0]:face_location[1], face_location[2]:face_location[3]]

preprocessed_img = para.face_recognition.Preprocessing_Img(face)
known_location = (0, IMAGE_SIZE, IMAGE_SIZE, 0)

start_time = time.time()
raw_landmark = para.face_recognition.Get_Landmarks(preprocessed_img, [known_location])[0]
print("time to get landmarks: {}".format(time.time() - start_time))

start_time = time.time()
encoded_face = para.face_recognition.Encoding_Face(face)
print("time to encode: {}".format(time.time() - start_time))

for i in range(5):
    x = raw_landmark.part(i).x
    y = raw_landmark.part(i).y
    cv2.circle(preprocessed_img, (x, y), 1, (0, 0, 255), -1)

if ret == 0:
    # face = cv2.resize(face, (300,300))
    cv2.imshow('test', preprocessed_img)
    cv2.waitKey(3000)