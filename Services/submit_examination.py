from parameters import *
from services.create_temp_patient import *

def Submit_Examination(properties, list_embedded_face):
    flag_insert_user_information = False
    flag_insert_sensor = False
    sensor_id = None
    stt = None
    # print(properties)
    try:
        # print(properties)
        # TRANSFER BACK PROPERTIES FROM STRING TO FLOAT
        hospital_ID = int(properties['hospital_ID'])
        building_code = str(properties['building_code'])
        room_code = str(properties['room_code'])
        patient_ID = int(properties['patient_ID'])

        # Sensor Information
        blood_pressure = round(float(properties['blood_pressure']), 0)
        pulse = round(float(properties['pulse']), 0)
        spo2 = round(float(properties['spo2']), 1)
        thermal = round(float(properties['thermal']), 1)
        height = round(float(properties['height']), 1)
        weight = round(float(properties['weight']), 1)

        # Check whether this user is new user or not
        if patient_ID == -1:
            ret, patient_ID = Create_Temp_Patient(list_embedded_face)
            # simulate error when insert temp patient
            # ret = -1
            if ret == -1:
                print("\t\t{}".format(patient_ID))
                return {'return': -1, 'msg': 'Fail to submit examination'}
            
            print("\t\tNew patient with ID {} has sumbitted examination".format(patient_ID))
            flag_insert_user_information = True
        else:
            print("\t\tPatient with ID {} has sumbitted examination".format(patient_ID))

        # First insert into sensor information
        # If success: go next state
        # Else: remove from database
        ret, sensor_id = para.db.Insert_Sensor_Information(blood_pressure, pulse, spo2, thermal, height, weight)
        # simulate error when insert senson information
        # ret = -1
        if ret == -1:
            message = "Fail to insert sensor information of patient into database"
            print("\t\t{}".format(message))
            return Error_Functions_Submit_Examination( 
                flag_insert_user_information, flag_insert_sensor,
                patient_ID, sensor_id, message)
        
        print("\t\tInsert successfully sensor information with ID {}".format(sensor_id))
        flag_insert_sensor = True
        
        ret, stt = para.db.Insert_Queue_Examination(hospital_ID, building_code, room_code, patient_ID, sensor_id)
        # simulate error when insert examination
        # ret = -1
        if ret == -1:
            message = "Fail to insert queue examination of patient into database"
            print("\t\t{}".format(message))
            return Error_Functions_Submit_Examination( 
                flag_insert_user_information, flag_insert_sensor,
                patient_ID, sensor_id, message)

        print("\t\tInsert successfully examination with ID {} at room {}".format(stt, "{}-{}-{}".format(hospital_ID, building_code, room_code)))
        return {'return': 0, 'stt': stt}

    except Exception as error:
        message = "Has error at module Submit_Examination in file submit_examination: {}".format(error)
        print("\t\t{}".format(message))
        return Error_Functions_Submit_Examination( 
                flag_insert_user_information, flag_insert_sensor,
                patient_ID, sensor_id, message)

def Error_Functions_Submit_Examination(
    flag_insert_user_information, flag_insert_sensor,
    patient_ID, sensor_id, message):

    if flag_insert_sensor:
        para.db.Delete_Sensor_Information(sensor_id)
        print("\t\tDelete successfully sensor information with ID {}".format(sensor_id))

    if flag_insert_user_information:
        para.db.Delete_Patien_Img(patient_ID)
        para.db.Delete_Patient(patient_ID)
        print("\t\tDelete temp patient with ID {}".format(patient_ID))

    return {'return': -1, 'msg': message}