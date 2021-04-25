from parameters import *
from common_functions.utils import LogMesssage
from azure.iot.hub.models import CloudToDeviceMethod

######################################################################################
# Response_Devices                                                                   #
######################################################################################
def sendListExamRoomsToDevices(hospital_ID, method_name):
    list_sent_devices = []
    error_msg = 'Fail to update list exam rooms to devices'
    try:
        # Get list device id according to hospital_ID
        ret, list_device_ID = para.db.getListDeviceID(hospital_ID)
        if ret == -1:
            return {'return': -1, 'parameters': error_msg}
        
        print(list_device_ID)
        
        # get list_Exam_rooms
        ret, list_exam_rooms = para.db.Get_Exam_Room(hospital_ID)
        if ret == -1:
            return {'return': -1, 'parameters': error_msg}
        
        print(list_exam_rooms)

        # Prepare data and send to all devices
        res_msg = {'return': 0, 'list_exam_rooms': list_exam_rooms}
        deviceMethod = CloudToDeviceMethod(method_name=method_name, payload=res_msg)

        for device_ID in list_device_ID:
            try:
                print('Send list exam rooms to device: {}'.format(device_ID))
                response = para.iothub_registry_manager.invoke_device_method(device_ID, deviceMethod)

                LogMesssage('Response status          : {status}'.format(status=response.status))
                LogMesssage('Response payload         : {payload}'.format(payload=response.payload))

                list_sent_devices.append(device_ID)
            except Exception as e:
                print(e)
                pass
        
        return {'return': 0, 'list_sent_devices': list_sent_devices}

    except Exception as e:
        LogMesssage('Has error at moudle sendListExamRoomsToDevices in file send_list_exam_rooms.py: {error}'.format(error=e), opt=2)
        return {'return': -1, 'parameters': error_msg}