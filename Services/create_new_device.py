from parameters import *
from common_functions.Connect_DB import *

from msrest.exceptions import HttpOperationError

######################################################################################
# Create new divice                                                                  #
# return:                                                                            #
#           -1: Fail                                                                 #
#            0: Success                                                              #
######################################################################################
def Create_New_Device(string_properties):
    hospital_ID = int(string_properties['hospital_ID'])
    building_code = str(string_properties['building_code'])
    device_code = str(string_properties['device_code'])

    add_device_db_flg = False

    # PREPROCESSING HOSPITAL OR BUILDING
    if len(building_code) != 2 or len(device_code) != 10:
        msg = "Invalid hospital_ID or building_code or device code"
        print("\t{}".format(msg))
        return {'return': -1, 'msg': msg}

    device_ID = para.db.Insert_New_Device(device_code, hospital_ID, building_code)
    if device_ID == -1:
        msg = "Fail to insert new device"
        print("\t{}".format(msg))
        return {'return': -1, 'msg': msg}
    
    print('Insert device with id: {} into DB successfully'.format(device_ID))
    
    add_device_db_flg = True

    try:
        # Change device_id into String
        device_ID = str(device_ID)
        # CreateDevice - let IoT Hub assign keys
        primary_key = ""
        secondary_key = ""
        device_state = "enabled"
        new_device = para.iothub_registry_manager.create_device_with_sas(device_ID, primary_key, secondary_key, device_state)

    except HttpOperationError as ex:
        para.db.Delete_Device(device_ID)
        print('Delete device with id: {} into DB successfully'.format(device_ID))

        if ex.response.status_code == 409:
            # 409 indicates a conflict. This happens because the device already exists.
            new_device = para.iothub_registry_manager.get_device(device_ID)
            msg = "The device ID is already exist"
            print("\t{}".format(msg))
            return {'return': -1, 'msg': msg}

        else:
            msg = "The fail to insert device id into iot hub"
            print("\t{}".format(msg))
            return {'return': -1, 'msg': msg}

    print("\tCreate successfully new device with ID: {}".format(device_ID))
    print("\tAt hospital: {}, building: {}".format(hospital_ID, building_code))
    
    return {'return': 0, 'msg': device_ID}