from parameters import *
from services.create_temp_patient import *
from common_functions.utils import LogMesssage

def Submit_Examination(properties, list_embedded_face):
    stt = None
    sensor_id = None
    flag_insert_sensor = False
    flag_insert_user_information = False

    try:
        # TRANSFER BACK PROPERTIES FROM STRING TO FLOAT
        hospital_ID = int(properties['hospital_ID'])
        building_code = str(properties['building_code'])
        room_code = str(properties['room_code'])
        patient_ID = int(properties['patient_ID'])

        # Sensor Information
        bmi = round(float(properties['bmi']), 1)
        pulse = round(float(properties['pulse']), 0)
        spo2 = round(float(properties['spo2']), 0)
        thermal = round(float(properties['thermal']), 1)
        height = round(float(properties['height']), 2)
        weight = round(float(properties['weight']), 1)

        # Check whether this user is new user or not
        if patient_ID == -1:
            ret, patient_ID = Create_Temp_Patient(list_embedded_face)
            # simulate error when insert temp patient
            # ret = -1
            if ret == -1:
                return {'return': -1, 'msg': 'Fail to submit examination'}
            
            LogMesssage('\tNew patient with ID {} has sumbitted examination'.format(patient_ID))
            flag_insert_user_information = True

        elif patient_ID > 0:
            LogMesssage('\tPatient with ID {} has sumbitted examination'.format(patient_ID))

        elif patient_ID == 0 or patient_ID < -1:
            message = 'Invalid patient_ID'
            LogMesssage('\t{msg}'.format(msg=message), opt=2)
            return Error_Functions_Submit_Examination( 
                flag_insert_user_information, flag_insert_sensor,
                patient_ID, sensor_id, message)


        # First insert into sensor information
        # If success: go next state
        # Else: remove from database
        ret, sensor_id = para.db.Insert_Sensor_Information(bmi, pulse, spo2, thermal, height, weight)
        # simulate error when insert senson information
        # ret = -1
        if ret == -1:
            message = "Fail to insert sensor information of patient into database"
            LogMesssage('\t{msg}'.format(msg=message))
            return Error_Functions_Submit_Examination( 
                flag_insert_user_information, flag_insert_sensor,
                patient_ID, sensor_id, message)
        
        LogMesssage('\tInsert successfully sensor information with ID {id}'.format(id=sensor_id))
        flag_insert_sensor = True
        
        ret, stt = para.db.Insert_Queue_Examination(hospital_ID, building_code, room_code, patient_ID, sensor_id)
        # simulate error when insert examination
        # ret = -1
        if ret == -1:
            message = "Fail to insert queue examination of patient into database"
            LogMesssage('\t{msg}'.format(msg=message), opt=2)
            return Error_Functions_Submit_Examination( 
                flag_insert_user_information, flag_insert_sensor,
                patient_ID, sensor_id, message)
        
        LogMesssage('\tInsert successfully examination with ID {exam_id} at room {room_id}'.format(exam_id=stt, room_id="{}-{}-{}".format(hospital_ID, building_code, room_code)))
        return {'return': 0, 'stt': stt}

    except Exception as error:
        message = "Has error at module Submit_Examination in file submit_examination: {}".format(error)
        LogMesssage('\t{msg}'.format(msg=message), opt=2)
        return Error_Functions_Submit_Examination( 
                flag_insert_user_information, flag_insert_sensor,
                patient_ID, sensor_id, message)

def Error_Functions_Submit_Examination(
    flag_insert_user_information, flag_insert_sensor,
    patient_ID, sensor_id, message):

    if flag_insert_sensor:
        para.db.Delete_Sensor_Information(sensor_id)
        LogMesssage('\tDelete successfully sensor information with ID {id}'.format(id=sensor_id), opt=2)

    if flag_insert_user_information:
        para.db.Delete_Patient(patient_ID)
        LogMesssage("\tDelete temp patient with ID {id}".format(id=patient_ID), opt=2)

    return {'return': -1, 'msg': message}