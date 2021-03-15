from re import L
import numpy as np
from parameters import *

def Activate_Temp_Patient(string_properties):
    user_id = int(string_properties['user_id'])
    
    ret, list_images = para.db.Get_Patient_Img(user_id)
    if ret == -1:
        return -1

    list_encoded_img = []
    for i in list_images:
        image = i.split('/')
        encoded_img = [np.float64(j) for j in image if j != '']
        encoded_img = np.array(encoded_img)
        list_encoded_img.append(encoded_img)

    ret_add_new_patient = para.identifying_user.Add_New_Patient(user_id, list_encoded_img)
    if ret_add_new_patient == -1:
        return -1
    return 0