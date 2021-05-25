from parameters import *
import json
from common_functions.utils import LogMesssage
from azure.iot.hub.models import CloudToDeviceMethod

######################################################################################
# Response_Devices                                                                   #
######################################################################################
def sendListExamRoomsToDevices(hospital_ID):
    list_sent_devices = []
    error_msg = 'Fail to update list exam rooms to devices'
    try:
        # Get list device id according to hospital_ID
        ret, list_device_ID = para.db.getListDeviceID(hospital_ID)
        if ret == -1:
            return {
                'return': "-1", 
                'parameters': error_msg
            }
        
        print(list_device_ID)
        
        # get list_Exam_rooms
        ret, list_exam_rooms = para.db.Get_Exam_Room(hospital_ID)
        if ret == -1:
            return {
                'return': "-1", 
                'parameters': error_msg
            }
        
        print(list_exam_rooms)

        # Prepare data and send to all devices
        res_msg = {
            'return': "0", 
            'type_request': para.SERVER_REQUEST_UPDATE_EXAM_ROOM,
            'parameters': list_exam_rooms,
            'request_id': '0'
        }

        # deviceMethod = CloudToDeviceMethod(method_name=method_name, payload=res_msg)
        props={}
        response_msg = json.dumps(res_msg)
        props["response_msg"] = response_msg

        for device_ID in list_device_ID:
            try:
                print('Send list exam rooms to device: {}'.format(device_ID))

                para.iothub_registry_manager.send_c2d_message(device_ID, "", properties=props)
                list_sent_devices.append(device_ID)
                
            except Exception as e:
                print(e)
                pass
        
        return {
            'return': "0", 
            'parameters': list_sent_devices
        }

    except Exception as e:
        LogMesssage('Has error at moudle sendListExamRoomsToDevices in file send_list_exam_rooms.py: {error}'.format(error=e), opt=2)
        return {
            'return': "-1", 
            'parameters': error_msg
        }