import sys
import os
import pickle

from time import sleep
from azure.iot.hub import IoTHubRegistryManager
from azure.iot.hub.models import Twin, TwinProperties, QuerySpecification, QueryResult
from msrest.exceptions import HttpOperationError
from azure.iot.hub import IoTHubRegistryManager
from azure.iot.hub.models import CloudToDeviceMethod, CloudToDeviceMethodResult

import asyncio
from azure.eventhub.aio import EventHubConsumerClient
from azure.eventhub.extensions.checkpointstoreblobaio import BlobCheckpointStore

from Connect_DB import *

EVENT_HUB_CONNECTION = "Endpoint=sb://receivemsgsfromdevices.servicebus.windows.net/;SharedAccessKeyName=RootManageSharedAccessKey;SharedAccessKey=lM4liPS83Rni9DE72LJg2swfELncFmBKOIYTKm81eQY="
EVENT_HUB_NAME = "receivemsg"

STORAGE_CONNECTION = "DefaultEndpointsProtocol=https;AccountName=hospitalstoragethesis;AccountKey=Sr8cft9eLH9tp//4a1zlz7KXugQgyEw89zAXPFD4N8tHknhPlPmZjAV3j2N+b3XTBNoIpdEehtUPELhLzBFFbA==;EndpointSuffix=core.windows.net"
BLOB_NAME = "thesis"

IOTHUB_CONNECTION = "HostName=E-HealthCare.azure-devices.net;SharedAccessKeyName=ServerRight;SharedAccessKey=coR5OV6uuuBPCxSriI7DibJsw+XiCb6255cONqZ6JWg="
DEVICE_ID = "MyNodeDevice"

RESPONSE_METHOD_NAME = "Listen_Reponse_Server"

RESPONSE_IOTHUB_CONNECTION = "HostName=E-HealthCare.azure-devices.net;DeviceId=MyNodeDevice;SharedAccessKey={}"

db = DB()
######################################################################################
# Change the location of device with new hospital, new building                      #
######################################################################################
def ChangeLocation(device_ID, new_hospital, new_building):
    iothub_registry_manager = IoTHubRegistryManager(IOTHUB_CONNECTION_STRING)
    try:
        new_tags = {
                'location' : {
                    'hospital' : '%d'%new_hospital,
                    'building' : '%d'%new_building
                }
            }
        twin = iothub_registry_manager.get_twin(device_ID)
        twin_patch = Twin(tags=new_tags)
        twin = iothub_registry_manager.update_twin(device_ID, twin_patch, twin.etag)
        print("Update location of device: {} at new hospital: {}, building: {} sucessfully".format(device_ID, new_hospital, new_building))
        
        return 0
    except Exception as ex:
        print('Have unexpected error {0} when change location of device: {} at new hospital: {}, building: {}'.format(ex, device_ID, new_hospital, new_building))
        return -1

######################################################################################
# Create new divice                                                                  #
# return:                                                                            #
#           -1: Fail                                                                 #
#            0: Success                                                              #
######################################################################################
def Create_New_Device(hospital_ID, building_code, device_code):
    # PREPROCESSING HOSPITAL OR BUILDING
    if isinstance(hospital_ID, int) != True or isinstance(building_code, str) != True or isinstance(device_code, str) != True \
        or len(building_code) != 2 or len(device_code) != 10:
        print("Invalid hospital_ID or building_code or device code")
        return -1, 0, 0
    elif db.Check_Valid_Hospital(hospital_ID) != 0  or db.Check_Valid_Buidling(hospital_ID, building_code) != 0:
        print("Not exist hospital_ID or building_code or device code")
        return -1, 0, 0
    elif db.Check_Valid_Device(device_code) !=0:
        print("Exist device_code in database")
        return -1, 0, 0

    try:
        iothub_registry_manager = IoTHubRegistryManager(IOTHUB_CONNECTION)
        # Get available device_ID
        device_ID = db.Get_Available_Device_ID()
        try:
            # CreateDevice - let IoT Hub assign keys
            primary_key = ""
            secondary_key = ""
            device_state = "enabled"
            new_device = iothub_registry_manager.create_device_with_sas(device_ID, primary_key, secondary_key, device_state)
        except HttpOperationError as ex:
            if ex.response.status_code == 409:
                # 409 indicates a conflict. This happens because the device already exists.
                new_device = iothub_registry_manager.get_device(device_ID)
                print("The device ID is already exist")
                return -1, 0, 0
            else:
                raise

        primary_key = new_device.authentication.symmetric_key.primary_key
        iothub_connection = RESPONSE_IOTHUB_CONNECTION.format(primary_key)

        # Update twin
        new_tags = {
                'location' : {
                    'hospital_ID' : '%d'%hospital_ID,
                    'building_code' : '%s'%building_code
                }
            }
        twin = iothub_registry_manager.get_twin(device_ID)
        twin_patch = Twin(tags=new_tags)
        twin = iothub_registry_manager.update_twin(device_ID, twin_patch, twin.etag)
        
        ret = db.Insert_New_Device(device_ID, device_code, hospital_ID, building_code)
        if ret != 0:
            print("Fail to insert new device")
            iothub_registry_manager.delete_device(device_ID, etag=None)

        print("Create successfully new device with ID: {}".format(device_ID))
        print("\tAt hospital: {}, building: {}".format(hospital_ID, building_code))
        print("\tWith IoT Hub connection string: {}".format(iothub_connection))
        
        return 0, device_ID, iothub_connection

    except Exception as ex:
        print ( "Unexpected error {0} while create new device".format(ex) )
        return -1, 0, 0

######################################################################################
# Get_Connection_Device                                                               #
# return:
#           -1: Not exist connection 0: has connection
######################################################################################
def Get_Connection_Device(device_ID):
    try:
        iothub_registry_manager = IoTHubRegistryManager(IOTHUB_CONNECTION)
        new_device = iothub_registry_manager.get_device(device_ID)
            
        primary_key = new_device.authentication.symmetric_key.primary_key
        iothub_connection = RESPONSE_IOTHUB_CONNECTION.format(primary_key)

        return 0, iothub_connection
    except Exception as ex:
        print ( "Unexpected error {0} while retreiving device connection".format(ex) )
        return -1, 0


def Response_Devices(method_name, device_ID, msg):
    global registry_manager
    # Call the direct method.
    deviceMethod = CloudToDeviceMethod(method_name=method_name, payload=msg)
    response = registry_manager.invoke_device_method(device_ID, deviceMethod)

    print ( "\tResponse status          : {0}".format(response.status) )
    print ( "\tResponse payload         : {0}".format(response.payload) )
    print ( "" )

async def on_event(partition_context, event):
    try:
        bytes_properties = dict(event.properties)
        string_data = event.body_as_str(encoding='UTF-8')
        string_properties = {}

        # Change keys and values in properties from bytes to string
        for key in bytes_properties:
            string_properties[key.decode("utf-8")] = bytes_properties[key].decode("utf-8")

        if (string_properties['type_msg'] == "0"):
            print("Request creating new device")
            print("\tData message: {}".format(string_data))

            print("\tResponse to device")
            Response_Devices("Create_New_Device", "MyNodeDevice", "Hoho")
    except Exception as ex:
        print ( "\tUnexpected error {0} while create new device".format(ex))
    await partition_context.update_checkpoint(event)

async def Receive_Message_From_Devices():
    print("Start receiving message from devices")
    # Create an Azure blob checkpoint store to store the checkpoints.
    checkpoint_store = BlobCheckpointStore.from_connection_string(STORAGE_CONNECTION, BLOB_NAME)

    # Create a consumer client for the event hub.
    client = EventHubConsumerClient.from_connection_string(
        EVENT_HUB_CONNECTION, 
        consumer_group="$Default", 
        eventhub_name=EVENT_HUB_NAME, 
        checkpoint_store=checkpoint_store
        )
    async with client:
        # Call the receive method. Read from the beginning of the partition (starting_position: "-1")
        await client.receive(on_event=on_event,  starting_position="-1")

global registry_manager

if __name__ == '__main__':
    # global registry_manager
    # try:
    #     # Run the main method.
    #     registry_manager = IoTHubRegistryManager(IOTHUB_CONNECTION)
    #     loop = asyncio.get_event_loop()
    #     loop.run_until_complete(Receive_Message_From_Devices())
    #     # ret = Create_New_Device(DEVICE_ID, 2, 2)
    # except KeyboardInterrupt:
    #     print("press control-c again to quit")
    ret, device_id, iothub_connection = Create_New_Device(1, 'A1', 'XB00000000')
    print(ret)
    # print(len(iothub_connection))
