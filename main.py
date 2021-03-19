import time
import asyncio

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
from services.create_temp_patient import *
from services.create_new_device import *
from services.get_examination_room import *
from services.submit_examination import *
from services.activate_temp_patient import *

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
        # NOTE: EVERY VALUES IN JSON HAVE TO BE TRANSFERED TO STRING
        string_properties = {}

        # Change keys and values in properties from bytes to string
        for key in bytes_properties:
            string_properties[key.decode("utf-8")] = bytes_properties[key].decode("utf-8")
        
        # All attributes is String
        device_ID = str(string_properties['device_ID'])
        type_request = str(string_properties['type_request'])
        request_id = str(string_properties['request_id'])
        
        current_time = time.strftime("%H:%M:%S",time.localtime())
        print("[{time}]".format(time=current_time))

        if type_request == '0':
            data = event.body_as_str(encoding='UTF-8')
            print("\tID {}. Request validate patient. From device id: {}".format(request_id, device_ID))
            res_msg = para.identifying_user.Identifying_User(data)

        elif type_request == '2':
            print("\tID {}. Request create new patient. From device id: {}".format(request_id, device_ID))
            # data = event.body_as_json(encoding='UTF-8')
            data = event.body_as_str(encoding='UTF-8')
            res_msg = Create_New_Patient(string_properties, data)

        elif type_request == '3':
            print("\tID {}. Request new device. From device id: {}")
            res_msg = Create_New_Device(string_properties)

        elif type_request == '4':
            print("\tID {}. Request get examination room. From device id: {}".format(request_id, device_ID))
            res_msg = Get_Examination_Room(device_ID)
            
        elif type_request == '5':
            print("\tID {}. Request submit examination. From device id: {}".format(request_id, device_ID))
            data = event.body_as_str(encoding='UTF-8')
            # print(len(data))
            res_msg = Submit_Examination(string_properties, data)

        elif type_request == "6":
            data = event.body_as_str(encoding='UTF-8')
            res_msg = Create_Temp_Patient(string_properties, data)
            print("\tID {}. Request create temporary patient. From device id: {}".format(request_id, device_ID))

        res_msg['request_id'] = request_id
        Response_Devices(device_ID, res_msg, para.request_msg[type_request])
        print()
    except Exception as ex:
        print ( "\tUnexpected error {0} while receiving message".format(ex))
        if type_request == "0":
            msg = "Has error when validate user"
        elif type_request == "2":
            msg = "Has error when create new patient"
        elif type_request == "3":
            msg = "Has error when create new device"
        elif type_request == "4":
            msg = "Has error when get examination room"
        elif type_request == "5":
            msg = "Has error when submit examination room"
        elif type_request == "6":
            msg = "Has error when create temporary patient"

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
    print("Start Identifying User moule")
    para.identifying_user = IdentifyUser()
    print()

    print("Start Recognizing User moule")
    para.face_recognition = FaceRecognition()
    print()

    print("Start Connecting Database moule")
    para.db = DB()
    print()

    print("Start Connecting Azure services")
    para.iothub_registry_manager = IoTHubRegistryManager(IOTHUB_CONNECTION)
    para.checkpoint_store = BlobCheckpointStore.from_connection_string(STORAGE_CONNECTION, BLOB_RECEIVE_EVENT)
    para.image_user_container = ContainerClient.from_connection_string(STORAGE_CONNECTION, container_name=BLOB_RECEIVE_IMG)
    print()

    time.sleep(2)
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
