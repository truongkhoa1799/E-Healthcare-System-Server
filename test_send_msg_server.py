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
    list_encoded_img = ""

    for img in __image_files_in_folder(ORIGINAL_DATA + '/test/' + str(user_id)):
    # for img in __image_files_in_folder(UNKNOWN_DATA):
        loaded_img = cv2.imread(img)
        ret, face = para.face_recognition.Get_Face(loaded_img)
        if ret != 0:
            continue
        
        # cv2.imshow('test', face)
        # cv2.waitKey(2000)
        embedded_img = para.face_recognition.Encoding_Face(face)
        encoded_img_string = Compose_String(embedded_img)
        list_encoded_img += encoded_img_string + ' '

    server.Validate_User(list_encoded_img)
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

def Get_Exam_Room():
    server.Get_Exam_Room()
    while (server.has_response == False):
        continue

def test_create_temp_user(user_id, user_information):
    para.face_recognition = FaceRecognition()
    list_image_encoeded = ""
    for img in __image_files_in_folder(ORIGINAL_DATA + '/train/' + str(user_id)):
        loaded_img = cv2.imread(img)
        # print("Loaded image {} ".format(img))
        
        ret, face = para.face_recognition.Get_Face(loaded_img)
        if ret == 0:
            embedded_face = para.face_recognition.Encoding_Face(face)
            encoded_img_string = Compose_String(embedded_face)
            list_image_encoeded += encoded_img_string + ' '
        else:
            print("Has no face")
            exit(-1)
    
    server.Insert_Temp_Patient(user_information, list_image_encoeded)
    while (server.has_response == False):
        continue

def activate_temp_patient(user_id):
    server.Activate_Temp_Patient(user_id)


def Submit_Examiantion():
    msg = {
        'request_id': '44b6064c-5fd1-443e-ad8f-ef5ef0ffd795', 
        'type_request': '5', 
        'device_ID': 'test_device', 

        'hospital_ID': '1', 
        'building_code': 'C1', 
        'room_code': '101', 
        'patient_ID': '1', 
        
        'blood_pressure': '120', 
        'pulse': '98', 
        'thermal': '38', 
        'spo2': '90',
        'height': '172.4',
        'weight': '70.4'
    }

    server.Submit_Examination(msg)
    while (server.has_response == False):
        continue

if __name__ == '__main__':
    server.has_response = False
    # server.Close()
    khoa = {
        'first_name' : 'Khoa',
        'last_name' : 'Truong Le Vinh',
        'date_of_birth' : '1999-07-01',
        'gender' : 'm',
        'address' : '954/33 Quang Trung, p08, Go Vap, TPHCM',
        'phone_number' : '0971155910',
        'ssn' : '025874412',
        'user_name' : 'khoa',
        'password' : 'khoa123',
        'e_meail' : 'khoa123@gmail.com',
        'flag_valid' : '1'}
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
        'e_meail' : 'khuong123@gmail.com',
        'flag_valid' : '1'}
    cuccungchan = {
        'first_name' : 'Ngoc',
        'last_name' : 'Vu Hong Khanh',
        'date_of_birth' : '2000-08-15',
        'gender' : 'f',
        'address' : '133/38/18 Cong Lo, P.15, Tan Binh, TP.HCM',
        'phone_number' : '0971155123',
        'ssn' : '025874423',
        'user_name' : 'ngoc',
        'password' : 'ngoc123',
        'e_meail' : 'ngoc123@gmail.com',
        'flag_valid' : '1'}
    hao = {
        'first_name' : 'Hao',
        'last_name' : 'Le',
        'date_of_birth' : '2000-02-05',
        'gender' : 'm',
        'address' : '123 Quang Trung, p12, Go Vap, TP.HCM',
        'phone_number' : '0971155141',
        'ssn' : '025813412',
        'user_name' : 'Hao',
        'password' : 'hao123',
        'e_meail' : 'hao123@gmail.com',
        'flag_valid' : '1'}
    linh = {
        'first_name' : 'linh',
        'last_name' : 'Le',
        'date_of_birth' : '1999-01-07',
        'gender' : 'f',
        'address' : '123 Quang Trung, p12, Go Vap, TP.HCM',
        'phone_number' : '0971155141',
        'ssn' : '025813411',
        'user_name' : 'linh',
        'password' : 'linh123',
        'e_meail' : 'linh123@gmail.com',
        'flag_valid' : '1'}
    
    bo = {
        'first_name' : 'Khoa',
        'last_name' : 'Truong Le Anh',
        'date_of_birth' : '2013-11-02',
        'gender' : 'm',
        'address' : '123 Quang Trung, p12, Go Vap, TP.HCM',
        'phone_number' : '0971155311',
        'ssn' : '025813111',
        'user_name' : 'bo',
        'password' : 'bo123',
        'e_meail' : 'bo123@gmail.com',
        'flag_valid' : '1'}

    jenny = {
        'first_name' : 'Jenny',
        'last_name' : 'Huynh',
        'date_of_birth' : '2004-11-02',
        'gender' : 'f',
        'address' : '123 Quang Trung, p12, Go Vap, TP.HCM',
        'phone_number' : '0971215311',
        'ssn' : '025813110',
        'user_name' : 'jenny',
        'password' : 'jenny123',
        'e_meail' : 'jenny123@gmail.com',
        'flag_valid' : '1'}

    kiet = {
        'first_name' : 'Kiet',
        'last_name' : 'Truong Gia',
        'date_of_birth' : '2004-11-02',
        'gender' : 'f',
        'address' : '123 Quang Trung, p12, Go Vap, TP.HCM',
        'phone_number' : '0971215421',
        'ssn' : '025233110',
        'user_name' : 'kiet',
        'password' : 'kiet123',
        'e_meail' : 'kiet123@gmail.com',
        'flag_valid' : '1'}

    temp_patient = {
        'first_name' : 'temp',
        'last_name' : 'temp',
        'date_of_birth' : '2004-11-02',
        'gender' : 'm',
        'address' : 'temp',
        'phone_number' : '0971215000',
        'ssn' : '000000000',
        'user_name' : 'temp',
        'password' : 'temp123',
        'e_meail' : 'temp123@gmail.com',
        'flag_valid' : '0'}



    # test_create_new_patient(2, khuong)
    # test_create_new_patient(3, cuccungchan)
    # test_create_new_patient(4, hao)
    # test_create_new_patient(5, linh)
    # test_create_new_patient(6, bo)
    # test_create_new_patient(7, jenny)
    # test_create_new_patient(1, khoa)
    # test_create_new_patient(8, kiet)
    # test_validate(1)
    # test_validate(8)
    # test_validate(3)
    # receive_img()
    test_create_temp_user(9, temp_patient)
    # activate_temp_patient(9)
    # test_validate(9)
    # Get_Exam_Room()
    # Submit_Examiantion()
    # create_new_device(1, 'A1', 'XB00000002')
    # create_new_device(1, 'B1', 'XB00000003')
    # create_new_device(1, 'B1', 'XB00000004')



