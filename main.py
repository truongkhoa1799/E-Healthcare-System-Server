import os
import sys
import time
import pickle
import asyncio
import numpy as np
from time import sleep

from azure.iot.hub.models import Twin
from msrest.exceptions import HttpOperationError
from azure.iot.hub.models import CloudToDeviceMethod
from azure.eventhub.aio import EventHubConsumerClient
# from azure.eventhub import EventHubConsumerClient
from azure.iot.hub import IoTHubRegistryManager
from azure.eventhub.extensions.checkpointstoreblobaio import BlobCheckpointStore
# from azure.eventhub.extensions.checkpointstoreblob import BlobCheckpointStore
from azure.storage.blob import ContainerClient

from parameters import *
from common_functions.Connect_DB import DB
from common_functions.identifying_user import IdentifyUser
from common_functions.face_recognition import FaceRecognition
# from common_functions.manage_device import *

from services.create_new_patient import *
from services.create_new_device import *
from services.get_examination_room import *

######################################################################################
# Response_Devices                                                                   #
######################################################################################
def Response_Devices(device_ID, res_msg, method_name):
    # Call the direct method.
    # print(device_ID)
    # print(res_msg)
    # print(method_name)
    # time.sleep(2000)
    deviceMethod = CloudToDeviceMethod(method_name=method_name, payload=res_msg)
    response = para.iothub_registry_manager.invoke_device_method(device_ID, deviceMethod)

    print ( "\tResponse status          : {0}".format(response.status) )
    print ( "\tResponse payload         : {0}".format(response.payload) )
    print ( "" )

######################################################################################
# Receive_Message_From_Devices                                                       #
# Listening message from Event hub                                                   #
######################################################################################
async def on_event(partition_context, event):
# def on_event(partition_context, event):
    type_request = None
    device_ID = None
    try:
        await partition_context.update_checkpoint(event)
        # partition_context.update_checkpoint(event)

        bytes_properties = dict(event.properties)
        string_properties = {}

        # Change keys and values in properties from bytes to string
        for key in bytes_properties:
            string_properties[key.decode("utf-8")] = bytes_properties[key].decode("utf-8")
        
        device_ID = string_properties['device_ID']
        type_request = string_properties['type_request']
        request_id = string_properties['request_id']
        
        current_time = time.strftime("%H:%M:%S",time.localtime())
        print("[{time}]".format(time=current_time))

        if type_request == '0':
            data = event.body_as_str(encoding='UTF-8')
            print("\tRequest: {} validating user from device: {}".format(request_id, device_ID))
            res_msg = para.identifying_user.Identifying_User(data)
        elif type_request == '2':
            print("\tRequest: {} create new user from device: {}".format(request_id, device_ID))
            # data = event.body_as_json(encoding='UTF-8')
            data = event.body_as_str(encoding='UTF-8')
            res_msg = Create_New_Patient(string_properties, data)
        elif type_request == '3':
            print("\tRequest create new device")
            hospital_ID = int(string_properties['hospital_ID'])
            building_code = str(string_properties['building_code'])
            device_code = str(string_properties['device_code'])
            res_msg = Create_New_Device(hospital_ID, building_code, device_code)
        elif type_request == '4':
            print("\tRequest id: {}, getting examination room from device id: {}".format(request_id, device_ID))
            res_msg = Get_Examination_Room(device_ID)

        res_msg['request_id'] = request_id
        Response_Devices(device_ID, res_msg, para.request_msg[type_request])
        print()
    except Exception as ex:
        print ( "\tUnexpected error {0} while receiving message".format(ex))
        if type_request == "0":
            msg = "Has error when validate user"
        elif type_request == "2":
            msg = "Has error when create new user"
        elif type_request == "3":
            msg = "Has error when create new device"
        elif type_request == "4":
            msg = "Has error when get examination room"

        res_msg['request_id'] = request_id
        Response_Devices(device_ID, {'return': -1, 'msg': msg}, para.request_msg[type_request])
        print()

async def Receive_Message_From_Devices():
# def Receive_Message_From_Devices():
    print("Start receiving message from devices")

    # Create a consumer client for the event hub.
    client = EventHubConsumerClient.from_connection_string(
        EVENT_HUB_CONNECTION, 
        consumer_group="$Default", 
        eventhub_name=EVENT_HUB_NAME, 
        checkpoint_store=para.checkpoint_store
    )
    async with client:
        # Call the receive method. Read from the beginning of the partition (starting_position: "-1")
        await client.receive(on_event=on_event,  starting_position="-1")

    # try:
    #     with client:
    #         # Call the receive method. Read from the beginning of the partition (starting_position: "-1")
    #         client.receive(on_event=on_event,  starting_position="-1")
    # except KeyboardInterrupt:
    #     print('Stopped receiving.')

def Init_Server():
    # Init parameters
    para.identifying_user = IdentifyUser()
    para.face_recognition = FaceRecognition()
    para.db = DB()
    para.iothub_registry_manager = IoTHubRegistryManager(IOTHUB_CONNECTION)
    para.checkpoint_store = BlobCheckpointStore.from_connection_string(STORAGE_CONNECTION, BLOB_RECEIVE_EVENT)
    para.image_user_container = ContainerClient.from_connection_string(STORAGE_CONNECTION, container_name=BLOB_RECEIVE_IMG)
    # location = Get_Twin_Information('test_device')
    # ChangeLocation('test_device', 1, 'B1')
    # print(location)
    # exit(-1)

if __name__ == '__main__':
    # Remove_Device(1)
    try:
        Init_Server()
        # Run the main method.
        loop = asyncio.get_event_loop()
        loop.run_until_complete(Receive_Message_From_Devices())
        # Receive_Message_From_Devices()
    except KeyboardInterrupt:
        print("press control-c again to quit")
