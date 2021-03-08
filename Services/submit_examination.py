from parameters import *

def Submit_Examination(properties):
    flag_insert_sensor = False
    flag_queue_examination = False
    sensor_id = None
    stt = None
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

        if patient_ID != -1:
            # First insert into sensor information
            # If success: go next state
            # Else: remove from database
            ret, sensor_id = para.db.Insert_Sensor_Information(blood_pressure, pulse, spo2, thermal, height, weight)
            if ret == -1:
                return {'return': -1, 'msg': 'Fail to submit examination'}
            else:
                flag_insert_sensor = True
            
            ret, stt = para.db.Insert_Queue_Examination(hospital_ID, building_code, room_code, patient_ID, sensor_id)
            if ret != -1:
                flag_queue_examination = True
                return {'return': 0, 'stt': stt}
            else:
                print("Hello 1")
                para.db.Delete_Sensor_Information(sensor_id)
            
        return {'return': 0, 'stt': 'Success'}
    except Exception as error:
        print("Hello")
        if flag_insert_sensor:
            para.db.Delete_Sensor_Information(sensor_id)
        if flag_queue_examination:
            para.db.Delete_Queue_Examination(hospital_ID, building_code, room_code, stt)

        print("Has error at moudle Submit_Examination in file submit_examination.py: {}".format(error))
        return {'return': -1, 'msg': 'Fail to submit examination'}