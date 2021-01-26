import sys
import os
import pickle

from time import sleep
from azure.iot.hub import IoTHubRegistryManager
from azure.iot.hub.models import Twin, TwinProperties, QuerySpecification, QueryResult
from msrest.exceptions import HttpOperationError
from azure.iot.hub import IoTHubRegistryManager

import asyncio
from azure.eventhub.aio import EventHubConsumerClient
from azure.eventhub.extensions.checkpointstoreblobaio import BlobCheckpointStore

EVENT_HUB_CONNECTION = "Endpoint=sb://receivemsgsfromdevices.servicebus.windows.net/;SharedAccessKeyName=RootManageSharedAccessKey;SharedAccessKey=lM4liPS83Rni9DE72LJg2swfELncFmBKOIYTKm81eQY="
EVENT_HUB_NAME = "receivemsg"

STORAGE_CONNECTION = "DefaultEndpointsProtocol=https;AccountName=hospitalstoragethesis;AccountKey=Sr8cft9eLH9tp//4a1zlz7KXugQgyEw89zAXPFD4N8tHknhPlPmZjAV3j2N+b3XTBNoIpdEehtUPELhLzBFFbA==;EndpointSuffix=core.windows.net"
BLOB_NAME = "thesis"


IOTHUB_CONNECTION_STRING = "HostName=E-HealthCare.azure-devices.net;SharedAccessKeyName=ServerRight;SharedAccessKey=coR5OV6uuuBPCxSriI7DibJsw+XiCb6255cONqZ6JWg="
DEVICE_ID = "MyNodeDevice"
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

def Create_New_Device(device_ID, new_hospital, new_building):
    try:
        iothub_registry_manager = IoTHubRegistryManager(IOTHUB_CONNECTION_STRING)
        try:
            # CreateDevice - let IoT Hub assign keys
            primary_key = ""
            secondary_key = ""
            device_state = "enabled"
            new_device = iothub_registry_manager.create_device_with_sas(device_ID, primary_key, secondary_key, device_state)
        except HttpOperationError as ex:
            if ex.response.status_code == 409:
                # 409 indicates a conflict. This happens because the device already exists.
                new_device = iothub_registry_manager.get_device(DEVICE_ID)
            else:
                raise

        print("device <" + device_ID +"> has primary key = " + new_device.authentication.symmetric_key.primary_key)

        # Update twin
        new_tags = {
                'location' : {
                    'hospital' : '%d'%new_hospital,
                    'building' : '%d'%new_building
                }
            }
        twin = iothub_registry_manager.get_twin(device_ID)
        twin_patch = Twin(tags=new_tags)
        twin = iothub_registry_manager.update_twin(device_ID, twin_patch, twin.etag)
        
        print ( "" )
        print ( "Create successfully new device with ID: {} at hospital: {}, building: {}:".format(device_ID, new_hospital, new_building))
        
        return 0

    except Exception as ex:
        print ( "Unexpected error {0} while create new device".format(ex) )
        return -1


async def on_event(partition_context, event):
    # Print the event data.
    print(event)
    print("Received the event: \"{}\" from the partition with ID: \"{}\"".format(event.body_as_str(encoding='UTF-8'), partition_context.partition_id))

    # Update the checkpoint so that the program doesn't read the events
    # that it has already read when you run it next time.
    await partition_context.update_checkpoint(event)

async def Receive_Message_From_Devices():
    # Create an Azure blob checkpoint store to store the checkpoints.
    checkpoint_store = BlobCheckpointStore.from_connection_string(STORAGE_CONNECTION, BLOB_NAME)

    # Create a consumer client for the event hub.
    client = EventHubConsumerClient.from_connection_string(EVENT_HUB_CONNECTION, consumer_group="$Default", eventhub_name=EVENT_HUB_NAME, checkpoint_store=checkpoint_store)
    async with client:
        # Call the receive method. Read from the beginning of the partition (starting_position: "-1")
        await client.receive(on_event=on_event,  starting_position="-1")

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    # Run the main method.
    loop.run_until_complete(Receive_Message_From_Devices())
    # ret = Create_New_Device(DEVICE_ID, 2, 2)