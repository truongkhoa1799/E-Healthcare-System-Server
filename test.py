# from parameters import *
# from Identifying_User import *
# import cv2
# import dlib

# pose_predictor_5_point = dlib.shape_predictor(PREDICTOR_5_POINT_MODEL)
# face_encoder = dlib.face_recognition_model_v1(RESNET_MODEL)

# def face_encodings(face_image, known_face_locations):
#     raw_landmarks = _raw_face_landmarks(face_image, known_face_locations)
#     return [np.array(face_encoder.compute_face_descriptor(face_image, raw_landmark_set, 1)) for raw_landmark_set in raw_landmarks]

# def _css_to_rect(css):
#     return dlib.rectangle(css[3], css[0], css[1], css[2])

# def _raw_face_landmarks(face_image, face_locations):
#     if face_locations is None:
#         face_locations = _raw_face_locations(face_image)
#     else:
#         face_locations = [_css_to_rect(face_location) for face_location in face_locations]

#     pose_predictor = pose_predictor_5_point

#     return [pose_predictor(face_image, face_location) for face_location in face_locations]

# ###############################################################################################
# # Preprocessing image                                                                         #
# ###############################################################################################
# def preprocessing(img):
#     # Resize image
#     resized_img = cv2.resize(img, (IMAGE_SIZE,IMAGE_SIZE))

#     # Adjust bright image
#     hsv_img = cv2.cvtColor(resized_img, cv2.COLOR_BGR2HSV) #convert it to hsv
#     v = hsv_img[:, :, 2]
#     mean_v = np.mean(v)
#     diff = BASE_BRIGHTNESS - mean_v
                   
#     if diff < 0:
#         v = np.where(v < abs(diff), v, v + diff)
#     else:
#         v = np.where( v + diff > 255, v, v + diff)

#     hsv_img[:, :, 2] = v
#     adjust_bright_img = cv2.cvtColor(hsv_img, cv2.COLOR_HSV2BGR)

#     # Change to RGB image
#     RGB_resized_img = cv2.cvtColor(adjust_bright_img, cv2.COLOR_BGR2RGB)

#     # return RGB image
#     return RGB_resized_img

# if __name__ == '__main__':
#     para.identifying_user = IdentifyUser()
#     # test_img = cv2.imread(FACE_TEST_PATH + '/unknown_face/face_1.jpg')
#     test_img = cv2.imread(FACE_TEST_PATH + '/00002/0-Khoa_1.jpeg')
#     # cv2.imshow('test', test_img)
#     # cv2.waitKey(2000)
#     test_img = preprocessing(test_img)
#     embedded_img = face_encodings(test_img, [(0,IMAGE_SIZE,IMAGE_SIZE,0)])[0]
#     embedded_img = np.array(embedded_img).reshape(1,-1)
#     for i in range(10):
#         para.list_encoded_img.append(embedded_img)

#     para.identifying_user.Get_User_ID()

#     # for i in para.list_user_id:
#     #     print(i['user_id'])
#     #     print(i['distance'])
#     print(para.return_user_id)

import logging
import threading
import time

def thread_function(name):
    print("Thread: starting")
    time.sleep(1)

if __name__ == "__main__":
    threads = list()
    for index in range(3):
        x = threading.Thread(target=thread_function, args=(index,))
        threads.append(x)
        x.start()

    for index, thread in enumerate(threads):
        thread.join()