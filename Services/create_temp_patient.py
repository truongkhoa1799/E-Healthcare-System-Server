from parameters import *
from common_functions.utils import LogMesssage

def Create_Temp_Patient(request_data):
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
        # patient_ID = -1
        if patient_ID == -1:
            LogMesssage('\tFail to insert temp patient into database', opt=2)
            return Error_Functions_Temp_Patient(patient_ID)
        
        list_encoded_img = []
        list_encoded_img = request_data.split(' ')
        for encoded_img in list_encoded_img:
            if encoded_img != "":
                ret_insert_patient_img = para.db.Insert_Patient_Img(patient_ID, encoded_img)
                # ret_insert_patient_img = -1
                if ret_insert_patient_img == -1:
                    LogMesssage('\tHas error when insert image of temp patient', opt=2)
                    return Error_Functions_Temp_Patient(patient_ID)
                
        return 0, patient_ID

    except Exception as e:
        LogMesssage('\tHas error at module: Create_Temp_Patient in module: create_temp_patient. {}'.format(e), opt=2)
        return Error_Functions_Temp_Patient(patient_ID)

def Error_Functions_Temp_Patient(patient_ID):
    para.db.Delete_Patient(patient_ID)
    return  -1, None