from common_functions.manage_device import *
from parameters import *

def Get_Examination_Room(device_ID):
    try:
        location = Get_Twin_Information(device_ID)
        hospital_ID = int(location['hospital_ID'])
        ret, exam_room = para.db.Get_Exam_Room(hospital_ID)
        if ret == 0:
            return {'return': 0, 'msg': exam_room}
        else:
            return {'return': -1, 'msg': 'Fail to get examination room'}
    except Exception as error:
        print("Has error at moudle Get_Examination_Room in file get_examination_room.py: {}".format(error))
        return {'return': -1, 'msg': 'Fail to get examination room'}
    