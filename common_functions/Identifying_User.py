import os
import json
import pickle
import numpy as np

from sklearn import neighbors
from parameters import *

class IdentifyUser:
    ###############################################################################################
    # __init__                                                                                    #
    # Input:                                                                                      #
    #   list_ndarray    self.__known_face_encodings :   List of face encoded                      #
    #   list_str        self.__known_face_IDs       :   List of face ID according to face encoded #
    # Output:                                                                                     #
    #   None            None                        :   None                                      #
    ###############################################################################################
    def __init__(self):
        self.__known_face_encodings = []
        self.__known_face_IDs = []
        self.__knn_clf = None

        ret, self.__known_face_IDs, self.__known_face_encodings = self.__LoadData()
        if ret == -1:
            print("There is no user id or encoding face face to load")
            exit(-1)

        ret, self.__knn_clf = self.__LoadKNNModel()
        if ret == -1:
            print("There is KNN model to load")
            exit(-1)

    ###############################################################################################
    # __LoadData                                                                                  #                    
    # Input:                                                                                      #
    #   None            None                        :   None                                      #
    # Output:                                                                                     #
    #   ret             int                         :   -1 No Data Loaded, 0 success              #
    ###############################################################################################
    def __LoadData(self):
        known_face_IDs = None
        known_face_encodings = None
        if not os.path.exists(PATH_USER_ID):
            return -1, None, None

        with open (PATH_USER_ID, 'rb') as fp_1:
            known_face_IDs = pickle.load(fp_1)

        if not os.path.exists(PATH_USER_IMG_ENCODED):
            return -1, None, None

        with open (PATH_USER_IMG_ENCODED, 'rb') as fp_2:
            known_face_encodings = pickle.load(fp_2)
        
        return 0, known_face_IDs, known_face_encodings
    
    #################################################################################
    # __LoadKNNModel                                                                #                    
    # Input:                                                                        #
    #   model_path      :   path to save model                                      #
    # Output:                                                                       #
    #   ret             :   -1 no path, 0 success                                   #
    #   knn_clf         :   Model                                                   #
    #################################################################################
    def __LoadKNNModel(self):
        if not os.path.exists(KNN_MODEL_PATH):
            return -1, None

        with open(KNN_MODEL_PATH, 'rb') as f:
            knn_clf = pickle.load(f)
            return 0, knn_clf

    #################################################################################
    # __Count_Face                                                                #                    
    # Input:                                                                        #
    #   model_path      :   path to save model                                      #
    # Output:                                                                       #
    #   ret             :   -1 no path, 0 success                                   #
    #   knn_clf         :   Model                                                   #
    #################################################################################
    def __Get_Most_Face(self):
        freq = {}
        max_people = 0
        return_user_id = None

        for user_id in para.list_user_id: 
            if (user_id['user_id'] in freq): 
                freq[user_id['user_id'] ] += 1
            else: 
                freq[user_id['user_id'] ] = 1
            
            if freq[user_id['user_id'] ] > max_people:
                max_people = freq[user_id['user_id'] ]
                return_user_id = user_id['user_id'] 
                
        if max_people >= THRESHOLD_PATIENT_REC:
            return return_user_id
        else:
            return -1
    
    ###############################################################################################
    # GetFaceID                                                                                   #                    
    # Input:                                                                                      #
    #   ndarray         img                         :                                             #
    # Output:                                                                                     #
    #   Str             UserID                      :                                             #
    ###############################################################################################
    def Get_User_ID(self):
        for embedded_img in para.list_encoded_img:
            closet_distances = self.__knn_clf.kneighbors(embedded_img, n_neighbors = NUM_NEIGHBROS)
            face_id = self.__knn_clf.predict(embedded_img)
            # print(closet_distances)
            # print(face_id)

            meet_condition_threshold = [closet_distances[0][0][i] <= THRESHOLD_FACE_REC for i in range(len(closet_distances[0][0]))]
            for i in range(len(meet_condition_threshold)):
                if self.__known_face_IDs[closet_distances[1][0][i]] == face_id[-1] and meet_condition_threshold[i]:
                    para.list_user_id.append({'user_id':face_id[-1], 'distance': str(closet_distances[0][0][i])})
                    break
        
        para.return_user_id =  self.__Get_Most_Face()
