import numpy as np
from parameters import *
from common_functions.utils import LogMesssage

def Activate_Temp_Patient(string_properties):
    # return 0
    user_id = int(string_properties['user_id'])
    
    # First check whether this patient is activate or not
    exist_patient = para.identifying_user.CheckExistPatient(user_id)
    if exist_patient == 0:
        LogMesssage('\tRequest to activate exist patient')
        return -1
    
    ret, list_images = para.db.Get_Patient_Img(user_id)
    if ret == -1:
        LogMesssage('\tFail to activate patient with id: {id}'.format(id=user_id), opt=2)
        return -1
    
    # Check whether this user has image in db or not
    if len(list_images) != 5:
        return -1

    list_encoded_img = []
    for i in list_images:
        image = i.split('/')
        encoded_img = [np.float64(j) for j in image if j != '']
        encoded_img = np.array(encoded_img)
        list_encoded_img.append(encoded_img)

    para.lock_train_patient.acquire()
    ret_add_new_patient = para.identifying_user.Add_New_Patient(user_id, list_encoded_img)
    para.lock_train_patient.release()
    if ret_add_new_patient == -1:
        LogMesssage('\tFail to activate patient with id: {id}'.format(id=user_id), opt=2)
        return -1
    return 0