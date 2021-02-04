import os
import sys
import pickle
import asyncio
import numpy as np
from time import sleep

from azure.iot.hub.models import Twin
from msrest.exceptions import HttpOperationError
from azure.iot.hub.models import CloudToDeviceMethod
from azure.eventhub.aio import EventHubConsumerClient
from azure.iot.hub import IoTHubRegistryManager
from azure.eventhub.extensions.checkpointstoreblobaio import BlobCheckpointStore

from parameters import *
from common_functions.Connect_DB import DB
from common_functions.Identifying_User import IdentifyUser

######################################################################################
# Identifying user                                                                   #
# return:                                                                            #
#           -1: Not exist otherwise user_id                                          #
######################################################################################
def Identifying_User():
    try:
        para.list_encoded_img = []
        para.list_user_id = []
        post_list_encoded_img = para.request_data.split(' ')
        for i in post_list_encoded_img:
            if i != '':
                post_encoded_img = i.split('/')
                encoded_img = [np.float64(j) for j in post_encoded_img if j != '']
                encoded_img = np.array(encoded_img).reshape(1,-1)
                para.list_encoded_img.append(encoded_img)
        
        para.identifying_user.Get_User_ID()
        return para.return_user_id
    except Exception as ex:
        print ( "\tUnexpected error {0} while identifying user".format(ex))
        return -1

######################################################################################
# Response_Devices                                                                   #
######################################################################################
def Response_Devices(device_ID, res_msg):
    # Call the direct method.
    deviceMethod = CloudToDeviceMethod(method_name=CREATE_USER_REPONSE_METHOD, payload=res_msg)
    response = para.iothub_registry_manager.invoke_device_method(device_ID, deviceMethod)

    print ( "\tResponse status          : {0}".format(response.status) )
    print ( "\tResponse payload         : {0}".format(response.payload) )
    print ( "" )

######################################################################################
# Receive_Message_From_Devices                                                       #
# Listening message from Event hub                                                   #
######################################################################################
async def on_event(partition_context, event):
    try:
        bytes_properties = dict(event.properties)
        string_properties = {}

        # Change keys and values in properties from bytes to string
        for key in bytes_properties:
            string_properties[key.decode("utf-8")] = bytes_properties[key].decode("utf-8")
        
        device_ID = int(string_properties['device_ID'])
        type_request = string_properties['type_request']
        para.request_data = event.body_as_str(encoding='UTF-8')

        if type_request == '0':
            print("Request validating user at device: {}".format(device_ID))
            user_ID = Identifying_User()
            print('\t{}'.format(user_ID))
            res_msg = {'answer': user_ID}

        Response_Devices(device_ID, res_msg)
    except Exception as ex:
        print ( "\tUnexpected error {0} while receiving message".format(ex))

    await partition_context.update_checkpoint(event)

async def Receive_Message_From_Devices():
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

def Init_Server():
    # Init parameters
    para.identifying_user = IdentifyUser()
    para.db = DB()
    para.iothub_registry_manager = IoTHubRegistryManager(IOTHUB_CONNECTION)
    para.checkpoint_store = BlobCheckpointStore.from_connection_string(STORAGE_CONNECTION, BLOB_NAME)

if __name__ == '__main__':
    # Remove_Device(1)
    try:
        Init_Server()

        # Run the main method.
        loop = asyncio.get_event_loop()
        loop.run_until_complete(Receive_Message_From_Devices())
    except KeyboardInterrupt:
        print("press control-c again to quit")
