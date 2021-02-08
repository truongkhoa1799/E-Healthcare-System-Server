from parameters import *
from common_functions.identifying_user import IdentifyUser
from common_functions.face_recognition import FaceRecognition
import cv2
import os, re, uuid
import numpy as np
from test_server import Server
from azure.storage.blob import BlobServiceClient, ContainerClient, __version__

from azure.iot.device import IoTHubDeviceClient
from azure.core.exceptions import AzureError

server = Server()
list_name = []
def __image_files_in_folder(folder):
    return [os.path.join(folder, f) for f in os.listdir(folder) if re.match(r'.*\.(jpg|jpeg|png)', f, flags=re.I)]

def Compose_String(encoded_img):
    ret_string = ""
    for i in encoded_img:
        precision_i = '%.20f'%np.float64(i)
        ret_string += str(precision_i) + '/'
    
    return ret_string

def test_validate(user_id):
    para.identifying_user = IdentifyUser()
    para.face_recognition = FaceRecognition()

    for img in __image_files_in_folder(ORIGINAL_DATA + '/test/' + str(user_id)):
    # for img in __image_files_in_folder(UNKNOWN_DATA):
        loaded_img = cv2.imread(img)
        ret, face = para.face_recognition.Get_Face(loaded_img)
        if ret != 0:
            continue
        embedded_img = para.face_recognition.Encoding_Face(face)
        encoded_img_string = Compose_String(embedded_img)
        para.list_encoded_img += encoded_img_string + ' '

    server.Validate_User()
    while (server.has_response == False):
        continue

def test_create_new_patient(user_id, user_information):
    list_imgs = ""
    count = 0
    for img in __image_files_in_folder(ORIGINAL_DATA + '/train/' + str(user_id)):
        img_name = str(uuid.uuid4()) + '-{}'.format(count) + ".jpg"
        list_imgs += img_name + ' '
        list_name.append(img_name)

        container_client = ContainerClient.from_connection_string(STORAGE_CONNECTION, container_name=BLOB_RECEIVE_IMG)

        print("\nUploading to Azure Storage as blob:\n\t" + img_name)

        # Upload the created file
        with open(img, "rb") as data:
            container_client.upload_blob(img_name ,data)
        count += 1
    # print(list_imgs)
    
    # print(user_information)

    server.Insert_New_Patient(user_information, list_imgs)
    while (server.has_response == False):
        continue


def receive_img():
    # Create the BlobServiceClient object which will be used to create a container client
    # para.blob_service_client = BlobServiceClient.from_connection_string(STORAGE_CONNECTION)
    # Create a blob client using the local file name as the name for the blob

    list_imgs = []
    container_client = ContainerClient.from_connection_string(STORAGE_CONNECTION, container_name=BLOB_RECEIVE_IMG)
    for name in list_name:
        image = container_client.download_blob(blob=name).readall()
        list_imgs.append(image)
        container_client.delete_blob(blob=name)

    image = np.fromstring(list_imgs[-1], np.uint8)
    image = cv2.imdecode(image, cv2.IMREAD_COLOR) # cv2.IMREAD_COLOR in OpenCV 3.1
    cv2.imshow('test', image)
    cv2.waitKey(2000)

def create_new_device(hospital_ID, building_code, device_code):
    server.Insert_New_Device(hospital_ID, building_code, device_code)
    while (server.has_response == False):
        continue

if __name__ == '__main__':
    server.has_response = False
    # server.Close()
    khoa = {
        'first_name' : 'Khoa',
        'last_name' : 'Truong Le Vinh Khoa',
        'date_of_birth' : '1999-07-01',
        'gender' : 'm',
        'address' : '954/33 Quang Trung, p08, Go Vap, TPHCM',
        'phone_number' : '0971155910',
        'ssn' : '025874412',
        'user_name' : 'khoa',
        'password' : 'khoa123',
        'e_meail' : 'khoa123@gmail.com'}
    khuong = {
        'first_name' : 'khuong',
        'last_name' : 'Le Nguyen An',
        'date_of_birth' : '1999-04-12',
        'gender' : 'm',
        'address' : '394 Tran Hung Dao, p.14, Q1, TPHCM',
        'phone_number' : '0971155912',
        'ssn' : '025874441',
        'user_name' : 'khuong',
        'password' : 'khuong123',
        'e_meail' : 'khuong123@gmail.com'}
    # test_create_new_patient(2, khuong)
    # test_validate(1)
    # test_validate(2)
    # receive_img()

    create_new_device(1, 'A1', 'XB00000002')


