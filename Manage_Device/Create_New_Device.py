import sys
sys.path.append('/Users/khoa1799/GitHub/E-Healthcare-System-Server')
from parameters import *
from common_functions.Connect_DB import *

from azure.iot.hub.models import Twin
from msrest.exceptions import HttpOperationError
from azure.iot.hub import IoTHubRegistryManager
from azure.eventhub.extensions.checkpointstoreblobaio import BlobCheckpointStore
######################################################################################
# Create new divice                                                                  #
# return:                                                                            #
#           -1: Fail                                                                 #
#            0: Success                                                              #
######################################################################################
def Create_New_Device(hospital_ID, building_code, device_code):
    # INIT FLAG CHECK CREATE
    register_device_flg = False

    # PREPROCESSING HOSPITAL OR BUILDING
    if isinstance(hospital_ID, int) != True or isinstance(building_code, str) != True or isinstance(device_code, str) != True \
        or len(building_code) != 2 or len(device_code) != 10:
        msg = "Invalid hospital_ID or building_code or device code"
        print(msg)
        return None, msg
    elif para.db.Check_Valid_Hospital(hospital_ID) != 0  or para.db.Check_Valid_Buidling(hospital_ID, building_code) != 0:
        msg = "Not exist hospital_ID or building_code or device code"
        print(msg)
        return None, msg
    elif para.db.Check_Valid_Device(device_code) !=0:
        msg = "Exist device_code in database"
        print(msg)
        return None, msg

    try:
        # Get available device_ID
        device_ID, msg = para.db.Get_Available_Device_ID()
        if device_ID is None:
            return None, msg

        try:
            # CreateDevice - let IoT Hub assign keys
            primary_key = ""
            secondary_key = ""
            device_state = "enabled"
            new_device = para.iothub_registry_manager.create_device_with_sas(device_ID, primary_key, secondary_key, device_state)
        except HttpOperationError as ex:
            if ex.response.status_code == 409:
                # 409 indicates a conflict. This happens because the device already exists.
                new_device = para.iothub_registry_manager.get_device(device_ID)
                msg = "The device ID is already exist"
                print(msg)
                return None, msg
            else:
                raise
        
        register_device_flg = True
        primary_key = new_device.authentication.symmetric_key.primary_key
        # iothub_connection = RESPONSE_IOTHUB_CONNECTION.format(primary_key)
        # Update twin
        new_tags = {
                'location' : {
                    'hospital_ID' : '%d'%hospital_ID,
                    'building_code' : '%s'%building_code
                }
            }
        twin = para.iothub_registry_manager.get_twin(device_ID)
        twin_patch = Twin(tags=new_tags)
        twin = para.iothub_registry_manager.update_twin(device_ID, twin_patch, twin.etag)
        
        ret, msg = para.db.Insert_New_Device(device_ID, device_code, hospital_ID, building_code)
        if ret is None:
            para.iothub_registry_manager.delete_device(device_ID, etag=None)
            return None, msg

        print("Create successfully new device with ID: {}".format(device_ID))
        print("\tAt hospital: {}, building: {}".format(hospital_ID, building_code))
        
        return 0, device_ID

    except Exception as ex:
        if register_device_flg == True:
            para.iothub_registry_manager.delete_device(device_ID, etag=None)
        print ( "Unexpected error {0} while create new device".format(ex))
        return -1, 0

def Remove_Device(device_ID):
    try:
        para.iothub_registry_manager.delete_device(device_ID, etag=None)
        ret = para.db.Delete_All_Device()
    except Exception as ex:
        print ( "\tUnexpected error {0} while delete device".format(ex))

if __name__ == '__main__':
    para.db = DB()
    para.iothub_registry_manager = IoTHubRegistryManager(IOTHUB_CONNECTION)

    # Remove_Device(1)
    ret, device_id = Create_New_Device(1, 'A1', 'XB00000001')
    print(ret)
    print(device_id)