######################################################################################
# Change the location of device with new hospital, new building                      #
######################################################################################
def ChangeLocation(device_ID, new_hospital, new_building):
    try:
        new_tags = {
                'location' : {
                    'hospital' : '%d'%new_hospital,
                    'building' : '%d'%new_building
                }
            }
        twin = para.iothub_registry_manager.get_twin(device_ID)
        twin_patch = Twin(tags=new_tags)
        twin = para.iothub_registry_manager.update_twin(device_ID, twin_patch, twin.etag)
        print("Update location of device: {} at new hospital: {}, building: {} sucessfully".format(device_ID, new_hospital, new_building))
        
        return 0
    except Exception as ex:
        print('Have unexpected error {0} when change location of device: {} at new hospital: {}, building: {}'.format(ex, device_ID, new_hospital, new_building))
        return -1

######################################################################################
# Get_Connection_Device                                                              #
# return:
#           -1: Not exist connection 0: has connection
######################################################################################
def Get_Connection_Device(device_ID):
    try:
        new_device = para.iothub_registry_manager.get_device(device_ID)
            
        primary_key = new_device.authentication.symmetric_key.primary_key
        iothub_connection = RESPONSE_IOTHUB_CONNECTION.format(primary_key)

        return 0, iothub_connection
    except Exception as ex:
        print ( "Unexpected error {0} while retreiving device connection".format(ex) )
        return -1, 0