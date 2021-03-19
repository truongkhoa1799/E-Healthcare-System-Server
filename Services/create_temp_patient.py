from re import L
import numpy as np
from parameters import *

def Create_Temp_Patient(request_data):
    flg_insert_patient_info = False
    flg_insert_patient_img = False
    try:
        # Prepare information for new user
        first_name = 'temp'
        last_name = 'temp'
        date_of_birth = '1900-01-01'
        gender = 'm'
        address = 'temp'
        phone_number = '0971215000'
        ssn = '000000000'
        user_name = 'temp'
        password = 'temp123'
        e_mail = 'temp123@gmail.com'
        # Specify valid flag for temporary patient
        flag_valid = '0'
        
        
        # patient_id: int
        patient_ID = para.db.Insert_New_Patient(first_name, last_name, date_of_birth, gender, address, phone_number, ssn, user_name, password, e_mail, flag_valid)
        patient_ID = int(patient_ID)
        if patient_ID == -1:
            message = "Fail to insert temp patient into database"
            print("\t{}".format(message))
            return Error_Functions_Create_New_Device(message, patient_ID, flg_insert_patient_info, flg_insert_patient_img)
        
        # indicate that patient has information in database
        flg_insert_patient_info = True
        
        list_encoded_img = []
        list_encoded_img = request_data.split(' ')
        for encoded_img in list_encoded_img:
            if encoded_img != "":
                ret_insert_patient_img = para.db.Insert_Patient_Img(patient_ID, encoded_img)
                if ret_insert_patient_img == -1:
                    message = "Has error when insert image of patient"
                    print("\t{}".format(message))
                    return Error_Functions_Create_New_Device(message, patient_ID, flg_insert_patient_info, flg_insert_patient_img)
                
                flg_insert_patient_img = True if flg_insert_patient_img == False else True

        return 0, patient_ID

    except Exception as e:
        print("\tHas error at def: Create_Temp_Patient in module: create_temp_patient. {}".format(e))
        message = "Has error when create temporary patient"
        return Error_Functions_Create_New_Device(message, patient_ID, flg_insert_patient_info, flg_insert_patient_img)

def Error_Functions_Create_New_Device(message, patient_ID, flg_insert_patient_info, flg_insert_patient_img):
    if flg_insert_patient_img:
        para.db.Delete_Patien_Img(patient_ID)
    if flg_insert_patient_info:
        para.db.Delete_Patient(patient_ID)
    return  -1, message