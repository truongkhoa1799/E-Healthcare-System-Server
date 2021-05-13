import os
import re
import cv2
from parameters import *
from common_functions.identifying_user import IdentifyUser
from common_functions.face_recognition import FaceRecognition

def __image_files_in_folder(folder):
    return [os.path.join(folder, f) for f in os.listdir(folder) if re.match(r'.*\.(jpg|jpeg|png)', f, flags=re.I)]

image_path = '/Users/khoatr1799/GitHub/E-Healthcare-System-Server/data_mask'
cut_face_path = '/Users/khoatr1799/GitHub/E-Healthcare-System-Server/cute_face'

para.identifying_user = IdentifyUser()
para.face_recognition = FaceRecognition()
# list_embeddeds = []

# for img in __image_files_in_folder(image_path):
#     image = cv2.imread(img)
#     face_location = para.face_recognition.Get_Location_Face(image)[1]
#     mask_face = image[face_location[0]:face_location[1], face_location[2]:face_location[3]]
#     embedded_img = para.face_recognition.Encoding_Face(mask_face)
#     list_embeddeds.append(embedded_img)

# para.identifying_user.Add_New_Patient(-2, list_embeddeds)

