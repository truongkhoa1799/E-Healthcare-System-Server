from re import L
from parameters import *
import os, glob
import cv2
import numpy as np

def Create_Temp_Patient(user_information, request_data):
    flg_insert_patient_info = False
    flg_insert_patient_img = False
    try:
        first_name = user_information['first_name']
        last_name = user_information['last_name']
        date_of_birth = user_information['date_of_birth']
        gender = user_information['gender']
        address = user_information['address']
        phone_number = user_information['phone_number']
        ssn = user_information['ssn']
        user_name = user_information['user_name']
        password = user_information['password']
        e_mail = user_information['e_meail']
        # Specify valid flag for temporary patient
        flag_valid = '0'
        
        # return {'return': 0, 'msg': "Hello"}
        
        patient_ID = para.db.Insert_New_Patient(first_name, last_name, date_of_birth, gender, address, phone_number, ssn, user_name, password, e_mail, flag_valid)
        if patient_ID == -1:
            message = "Fail to insert temp patient into database"
            print("\t{}".format(message))
            return Error_Functions_Create_New_Device(message, patient_ID, flg_insert_patient_info, flg_insert_patient_img)
        
        # indicate that patient has information in database
        flg_insert_patient_info = True
        
        list_encoded_img = []
        list_encoded_img = request_data.split(' ')
        print(len(list_encoded_img))
        for encoded_img in list_encoded_img:
            ret_insert_patient_img = para.db.Insert_Patient_Img(patient_ID, encoded_img)
            if ret_insert_patient_img == -1:
                message = "Has error when insert image of patient"
                print("\t{}".format(message))
                return Error_Functions_Create_New_Device(message, patient_ID, flg_insert_patient_info, flg_insert_patient_img)
            
            flg_insert_patient_img == True if flg_insert_patient_img == False else True

        return {'return': 0, 'msg': patient_ID}

    except Exception as e:
        print("\tHas error at def: Create_Temp_Patient in module: create_temp_patient. {}".format(e))
        message = "Has error when create temporary patient"
        return Error_Functions_Create_New_Device(message, patient_ID, flg_insert_patient_info, flg_insert_patient_img)

def Error_Functions_Create_New_Device(message, patient_ID, flg_insert_patient_info, flg_insert_patient_img):
    if flg_insert_patient_img:
        para.db.Delete_Patien_Img(patient_ID)
    if flg_insert_patient_info:
        para.db.Delete_Patient(patient_ID)
    return {'return': -1, 'msg': message}