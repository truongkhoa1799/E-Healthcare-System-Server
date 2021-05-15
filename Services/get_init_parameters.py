from parameters import *
from common_functions.manage_device import *
from common_functions.utils import LogMesssage

def getInitParameters(device_ID):
    error_msg_fail = 'Fail to get init parameters'
    error_msg_invalid = 'Device ID is invalid'
    try:
        device_ID = int(device_ID)
        # Check status of device
        ret, status = para.db.getStatusDevice(device_ID)
        if ret == -1:
            return {'return': -2, 'parameters': error_msg_invalid}

        elif ret == 0 and status == 0:
            LogMesssage('[getInitParameters]: The device is inactive.', opt=2)
            return {'return': -2, 'parameters': error_msg_invalid}

        ret, hospital_ID = para.db.GetHospitalIdOfDevice(device_ID)
        if ret == -1:
            return {'return': -1, 'parameters': error_msg_fail}

        ret, list_exam_rooms = para.db.Get_Exam_Room(hospital_ID)
        if ret == -1:
            return {'return': -1, 'parameters': error_msg_fail}
        
        parameters = {}
        parameters['hospital_ID'] = hospital_ID
        parameters['list_exam_rooms'] = list_exam_rooms
        return {'return': 0, 'parameters': parameters}

    except Exception as e:
        LogMesssage('Has error at moudle getInitParameters in file get_init_parameters.py: {error}'.format(error=e), opt=2)
        return {'return': -1, 'parameters': error_msg_fail}
    