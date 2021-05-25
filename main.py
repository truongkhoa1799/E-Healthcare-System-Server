import time, json, requests
import asyncio

from azure.iot.hub.models import CloudToDeviceMethod
from azure.eventhub.aio import EventHubConsumerClient
from azure.iot.hub import IoTHubRegistryManager
from azure.eventhub.extensions.checkpointstoreblobaio import BlobCheckpointStore
from azure.storage.blob import ContainerClient

from parameters import *
from common_functions.utils import LogMesssage
from common_functions.Connect_DB import DB
from common_functions.identifying_user import IdentifyUser
from common_functions.face_recognition import FaceRecognition

from services.create_new_device import *
# from services.create_new_patient import *
from services.submit_examination import *
# from services.get_examination_room import *
from services.send_list_exam_rooms import *
from services.activate_temp_patient import *
from services.get_init_parameters import *
from services.extract_sympton.get_sympton import Get_Sympton

from threading import Timer
class RepeatTimer(Timer):
    def run(self):
        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)

def establishIoTHubReceiveConnection():
    LogMesssage('[establishIoTHubReceiveConnection]: Re-establish iot hub connection')

    para.lock_reset_connection.acquire()
    try:
        para.iothub_registry_manager = IoTHubRegistryManager(IOTHUB_CONNECTION)
    except:
        LogMesssage('[establishIoTHubReceiveConnection]: Fail to re-establish iot hub connection')
    para.lock_reset_connection.release()

######################################################################################
# Response_Devices                                                                   #
######################################################################################
def Response_Devices(device_ID, res_msg):
    print(res_msg)
    props={}
    response_msg = json.dumps(res_msg)
    props["response_msg"] = response_msg

    para.lock_reset_connection.acquire()
    try:
        para.iothub_registry_manager.send_c2d_message(device_ID, "123", properties=props)
    except:
        pass
    para.lock_reset_connection.release()


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

        res_msg = {}
        LogMesssage('Request {res_id}, {res_name}, device: {device_id}'.format(res_id=request_id, res_name=para.request_msg[type_request], device_id=device_ID))

        if type_request == para.SERVER_REQUEST_VALIDATION:
            embedded_face = event.body_as_str(encoding='UTF-8')
            ssn = str(string_properties['ssn'])
            res_msg = para.identifying_user.Identifying_User(embedded_face, ssn)

        # elif type_request == '2':
        #     data = event.body_as_str(encoding='UTF-8')
        #     res_msg = Create_New_Patient(string_properties, data)

        # elif type_request == '3':
        #     res_msg = Create_New_Device(string_properties)

        # elif type_request == '4':
        #     res_msg = Get_Examination_Room(device_ID)
            
        elif type_request == para.SERVER_REQUEST_SUBMIT_EXAMINATION:
            data = event.body_as_str(encoding='UTF-8')
            res_msg = Submit_Examination(string_properties, data)
        
        elif type_request == para.SERVER_REQUEST_ACTIVE_PATIENT:
            res_msg = Activate_Temp_Patient(string_properties)
            return
        
        elif type_request == para.SERVER_REQUEST_GET_SYMPTOMS:
            user_voice = event.body_as_str(encoding='UTF-8')
            res_msg = Get_Sympton(user_voice)

        elif type_request == para.SERVER_REQUEST_GET_INIT_PARA:
            # return message: {'return': , 'parameters': }
            res_msg = getInitParameters(device_ID)
        
        elif type_request == para.SERVER_REQUEST_UPDATE_EXAM_ROOM:
            hospital_ID = int(string_properties['hospital_ID'])
            res_msg = sendListExamRoomsToDevices(hospital_ID)

        # attach the request id, and type request and send back to client
        res_msg['request_id'] = request_id
        res_msg['type_request'] = type_request
        Response_Devices(device_ID, res_msg)
        print()
    except Exception as ex:
        LogMesssage('Unexpected error {error} while receiving message'.format(error=ex), opt=2)
        if type_request == "0":
            msg = "Has error when validate user"

        # elif type_request == "2":
        #     msg = "Has error when create new patient"

        # elif type_request == "3":
        #     msg = "Has error when create new device"

        # elif type_request == "4":
        #     msg = "Has error when get examination room"

        elif type_request == "5":
            msg = "Has error when submit examination room"
            
        elif type_request == "6":
            return

        elif type_request == "7":
            msg = "Has error when submit examination room"

        elif type_request == "8":
            msg = "Has error when getting init parameters"
        
        elif type_request == "9":
            msg = "Has error when updating list exam rooms to devices"

        res_msg = {
            'request_id': request_id,
            'type_request': type_request,
            'return': -1,
            'msg': msg
        }
        Response_Devices(device_ID, res_msg)
        print()

async def Receive_Message_From_Devices():
    LogMesssage('Start receiving message from devices')

    # Create a consumer client for the event hub.
    client = EventHubConsumerClient.from_connection_string(
        EVENT_HUB_CONNECTION, 
        consumer_group="$Default", 
        eventhub_name=EVENT_HUB_NAME, 
        checkpoint_store=para.checkpoint_store
    )
    async with client:
        # Call the receive method. Read from the beginning of the partition (starting_position: "-1")
        await client.receive(
            on_event=on_event,
            partition_id = '0',
            starting_position="-1"
        )

def Init_Server():
    # Init parameters
    LogMesssage('Start Identifying User moule', opt=0)
    para.identifying_user = IdentifyUser()
    print()

    LogMesssage('Start Recognizing User moule', opt=0)
    para.face_recognition = FaceRecognition()
    print()

    LogMesssage('Start Connecting Database moule', opt=0)
    para.db = DB()
    print()

    LogMesssage('Start Connecting Azure services', opt=0)
    para.iothub_registry_manager = IoTHubRegistryManager(IOTHUB_CONNECTION)
    para.checkpoint_store = BlobCheckpointStore.from_connection_string(STORAGE_CONNECTION, BLOB_RECEIVE_EVENT)
    # para.image_user_container = ContainerClient.from_connection_string(STORAGE_CONNECTION, container_name=BLOB_RECEIVE_IMG)
    print()

    # sendListExamRoomsToDevices([1,2], "123", para.request_msg["9"])
    
    # Get and add device information
    # location = Get_Twin_Information('test_device')
    # print(location)
    # ChangeLocation('test_device', 1, 'B1')
    # print(location)
    # exit(-1)

    # delete patient all information
    # para.identifying_user.Delete_Patient(76)
    # para.db.Delete_Patient(76)
    # exit(-1)

if __name__ == '__main__':
    # Remove_Device(1)
    try:
        para.timer_reset=RepeatTimer(200, establishIoTHubReceiveConnection)
        para.timer_reset.daemon = True
        para.timer_reset.start()

        Init_Server()
        # Run the main method.
        loop = asyncio.get_event_loop()
        loop.run_until_complete(Receive_Message_From_Devices())
        # Receive_Message_From_Devices()
    except KeyboardInterrupt:
        print("press control-c again to quit")
