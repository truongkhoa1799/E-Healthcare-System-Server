from parameters import *
import os, glob
import cv2
import numpy as np

def Create_New_Patient(user_information, request_data):
    # os.mkdir(os.path.join(IMAGE_NEW_PATIENT, ssn))
    flg_insert_patient_info = False
    flg_insert_patient_img = False
    list_embedded_face = []
    try:
        list_imgs = []
        list_image_name = request_data.split(' ')
        for name in list_image_name:
            if name != "":
                image = para.image_user_container.download_blob(blob=name).readall()
                list_imgs.append(image)
                para.image_user_container.delete_blob(blob=name)

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
        flag_valid = user_information['flag_valid']

        patient_ID = para.db.Insert_New_Patient(first_name, last_name, date_of_birth, gender, address, phone_number, ssn, user_name, password, e_mail, flag_valid)
        if patient_ID is None:
            msg = "Fail to insert new patient into database"
            print("\t{}".format(msg))
            return {'return': -1, 'msg': msg}
        
        flg_insert_patient_info = True

        for img in list_imgs:
            image = np.fromstring(img, np.uint8)
            image = cv2.imdecode(image, cv2.IMREAD_COLOR) # cv2.IMREAD_COLOR in OpenCV 3.1

            ret, face = para.face_recognition.Get_Face(image)
            if ret == 0:
                embedded_face = para.face_recognition.Encoding_Face(face)
                list_embedded_face.append(embedded_face)

                encoding_embedded_face = ""
                for i in embedded_face:
                    precision_i = '%.20f'%np.float64(i)
                    encoding_embedded_face += str(precision_i) + '/'
                
                ret_insert_patient_img = para.db.Insert_Patient_Img(patient_ID, encoding_embedded_face)
                if ret_insert_patient_img == -1:
                    message = "Has error when insert image of patient"
                    print("\t{}".format(message))
                    return Error_Functions_Create_New_Device(message, patient_ID, flg_insert_patient_info, flg_insert_patient_img)
            elif ret == -1:
                message = "Has error when process patient face, cannot find location of face in image"
                print("\t{}".format(message))
                return Error_Functions_Create_New_Device(message, patient_ID, flg_insert_patient_info, flg_insert_patient_img)
            elif ret == -2:
                message = "Has error when process patient face, have many faces in image"
                print("\t{}".format(message))
                return Error_Functions_Create_New_Device(message, patient_ID, flg_insert_patient_info, flg_insert_patient_img)
            else:
                message = "Has error when receive images for inserting new patient"
                print("\t{}".format(message))
                return Error_Functions_Create_New_Device(message, patient_ID, flg_insert_patient_info, flg_insert_patient_img)

            flg_insert_patient_img = True

        ret_add_new_patient = para.identifying_user.Add_New_Patient(patient_ID, list_embedded_face)
        if ret_add_new_patient == -1:
            msg = "Has error when insert new patient"
            return {'return': -1, 'msg': message}
        
        return {'return': 0, 'msg': ""}
    except Exception as e:
        print("\tHas error at def: Create_New_Patient in module: create_new_patient. {}".format(e))
        message = "Has error when receive images for inserting new patient"
        return Error_Functions_Create_New_Device(message, patient_ID, flg_insert_patient_info, flg_insert_patient_img)


def Error_Functions_Create_New_Device(message, patient_ID, flg_insert_patient_info, flg_insert_patient_img):
    if flg_insert_patient_img:
        para.db.Delete_Patien_Img(patient_ID)
    if flg_insert_patient_info:
        para.db.Delete_Patient(patient_ID)
    return {'return': -1, 'msg': message}
    
