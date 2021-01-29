import os
import re
import cv2
import time
import json
import pickle
import numpy as np

# import face_recognition
import dlib
from sklearn import neighbors

from parameters import *

pose_predictor_5_point = dlib.shape_predictor(PREDICTOR_5_POINT_MODEL)
face_encoder = dlib.face_recognition_model_v1(RESNET_MODEL)

known_face_encodings = []
known_face_IDs = []
global knn_clf
knn_clf = None

###############################################################################################
# Face Recognition model                                                                      #
###############################################################################################
def face_encodings(face_image, known_face_locations):
    raw_landmarks = _raw_face_landmarks(face_image, known_face_locations)
    return [np.array(face_encoder.compute_face_descriptor(face_image, raw_landmark_set, 1)) for raw_landmark_set in raw_landmarks]

def _css_to_rect(css):
    return dlib.rectangle(css[3], css[0], css[1], css[2])

def _raw_face_landmarks(face_image, face_locations):
    if face_locations is None:
        face_locations = _raw_face_locations(face_image)
    else:
        face_locations = [_css_to_rect(face_location) for face_location in face_locations]

    pose_predictor = pose_predictor_5_point

    return [pose_predictor(face_image, face_location) for face_location in face_locations]

###############################################################################################
# Preprocessing image                                                                         #
###############################################################################################
def preprocessing(img):
    # Resize image
    resized_img = cv2.resize(img, (IMAGE_SIZE,IMAGE_SIZE))

    # Adjust bright image
    hsv_img = cv2.cvtColor(resized_img, cv2.COLOR_BGR2HSV) #convert it to hsv
    v = hsv_img[:, :, 2]
    mean_v = np.mean(v)
    diff = BASE_BRIGHTNESS - mean_v
                   
    if diff < 0:
        v = np.where(v < abs(diff), v, v + diff)
    else:
        v = np.where( v + diff > 255, v, v + diff)

    hsv_img[:, :, 2] = v
    adjust_bright_img = cv2.cvtColor(hsv_img, cv2.COLOR_HSV2BGR)

    # Change to RGB image
    RGB_resized_img = cv2.cvtColor(adjust_bright_img, cv2.COLOR_BGR2RGB)

    # return RGB image
    return RGB_resized_img
    
def LoadNewData():
    try:
        time_request = time.time()

        # Creating a list that store each encoding thread
        list_thread_encoding_image = []

        # Loop through each person in the training set
        for class_dir in os.listdir(FACE_TRAIN_PATH):
            print(class_dir)
            if not os.path.isdir(os.path.join(FACE_TRAIN_PATH, class_dir)):
                continue
        
            # Loop through each training image for the current person and past image path for encoing individualy
            for img in image_files_in_folder(os.path.join(FACE_TRAIN_PATH, class_dir)):
                path = img.split('/')
                user_ID = class_dir
                img_name = path[-1]
                loaded_img = cv2.imread( img )
                print("Loaded image {} ".format(img_name))
                
                # embedded_face: type ndarray (256,)
                # embedded_face = __face_iden(loaded_img)
                preprocessing_img = preprocessing(loaded_img)
                embedded_face = face_encodings(preprocessing_img, [(0,IMAGE_SIZE,IMAGE_SIZE,0)])[0]
                # embedded_face = np.array(embedded_face).reshape(-1,1)
                # print(type(embedded_face))
                # print(embedded_face.shape)
                # embedded_face = embedded_face.reshape((1,len(embedded_face)))
                # print(type(embedded_face))
                # print(embedded_face.shape)

                known_face_encodings.append(embedded_face)
                known_face_IDs.append(user_ID)

        if len(known_face_encodings) != len(known_face_IDs) \
            or len(known_face_encodings) == 0 \
            or len(known_face_IDs) == 0:
            return -1

        print("\ttime load data {}".format(time.time() - time_request))
        print()
        return 0

    except Exception as ex:
        print ( "\tUnexpected error {0} while loading data".format(ex))
        return -1

###############################################################################################
# __SaveData                                                                                  #                    
# Input:                                                                                      #
#   None            None                        :   None                                      #
# Output:                                                                                     #
#   ret             int                         :   -1 No Data Loaded, 0 success              #
###############################################################################################
def SaveData():
    try:
        with open(PATH_USER_ID, mode='wb') as fp_1:
            pickle.dump(known_face_IDs, fp_1)
        
        with open(PATH_USER_IMG_ENCODED, 'wb') as fp_2:
            pickle.dump(known_face_encodings, fp_2)
        
        return 0
    except Exception as ex:
        print ( "\tUnexpected error {0} while loading data".format(ex))
        return -1
    
def image_files_in_folder(folder):
    return [os.path.join(folder, f) for f in os.listdir(folder) if re.match(r'.*\.(jpg|jpeg|png)', f, flags=re.I)]

#################################################################################
# __SaveKNNModel                                                                #                    
# Input:                                                                        #
#   knn_clf         :   Model after trained                                     #
#   model_save_path :   path to save model                                      #
# Output:                                                                       #
#   ret             :   -1 no path, 0 success                                   #
#################################################################################
def SaveKNNModel():
    try:
        if KNN_MODEL_PATH is not None:
            with open(KNN_MODEL_PATH, 'wb') as f:
                pickle.dump(knn_clf, f)
    except Exception as ex:
        print ( "\tUnexpected error {0} while save KNN model".format(ex))
        return -1

###############################################################################################
# __TrainKNN                                                                                  #                    
# Input:                                                                                      #
#   int             n_neighbors                 :   Bumber of neighbors                       #
#   str             knn_algorithm               :   algorithm implement KNN                   #
#   str             knn_weights                 :   weights to calculate diff                 #
# Output:                                                                                     #
#   knn_clf         knn_clf                     :   knn classification model                  #
###############################################################################################
def TrainKNN():
    global knn_clf
    try:
        time_request = time.time()
        print("Starting train KNN Model")

        # Create and train the KNN classifier
        knn_clf = neighbors.KNeighborsClassifier(n_neighbors=NUM_NEIGHBROS, algorithm=KNN_ALGORITHM, weights=KNN_WEIGHTS)

        # known_face_encodings is list of ndarray
        # known_face_IDs is list of str
        knn_clf.fit(known_face_encodings, known_face_IDs)

        print("Finishing train KNN Model")

        print("\ttime load data {}".format(time.time() - time_request))
        print()
        return 0

    except Exception as ex:
        print ( "\tUnexpected error {0} while training KNN model".format(ex))
        return -1

if __name__ == '__main__':
    # global knn_clf
    if LoadNewData() != 0:
        exit(-1)
    if SaveData() != 0:
        exit(-1)
    if TrainKNN() != 0:
        exit(-1)
    SaveKNNModel()