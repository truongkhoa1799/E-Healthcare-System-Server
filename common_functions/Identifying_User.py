import os
import json
import pickle
import numpy as np
import sys
sys.path.append('/Users/khoa1799/GitHub/E-Healthcare-System-Server')

from sklearn import neighbors
from parameters import *

class IdentifyUser:
    ###############################################################################################
    # __init__                                                                                    #
    # Input:                                                                                      #
    #   list_ndarray    self.__list_embedded_face :   List of face encoded                      #
    #   list_str        self.__list_patient_ID       :   List of face ID according to face encoded #
    # Output:                                                                                     #
    #   None            None                        :   None                                      #
    ###############################################################################################
    def __init__(self):
        self.__list_embedded_face = []
        self.__list_patient_ID = []
        self.__knn_clf = None

        ret, self.__list_patient_ID, self.__list_embedded_face = self.__LoadData()
        if ret == -1:
            print("There is no user id or encoding face face to load")
            exit(-1)

        ret, self.__knn_clf = self.__LoadKNNModel()
        if ret == -1:
            print("There is KNN model to load")
            exit(-1)
        
        print("\tLoaded users data for encoding")
        print("\tNumber of users: {}".format(len(self.__list_patient_ID)//5))
                

        # print(self.__list_embedded_face)
        # print(self.__list_patient_ID)

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
                
        if len(para.list_user_id) > 20 and max_people >= THRESHOLD_PATIENT_REC*len(para.list_user_id):
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
    def __Get_User_ID(self, list_encoded_img):
        list_user_id = []
        freq = {}
        max_people = 0
        return_user_id = None
        
        for embedded_img in list_encoded_img:
            if len(self.__list_patient_ID) == 5:
                closet_distances = self.__knn_clf.kneighbors(embedded_img, n_neighbors = 5)
            else:
                closet_distances = self.__knn_clf.kneighbors(embedded_img, n_neighbors = NUM_NEIGHBROS)
            face_id = self.__knn_clf.predict(embedded_img)
            # print(closet_distances)
            # print(face_id)

            meet_condition_threshold = [closet_distances[0][0][i] <= THRESHOLD_FACE_REC for i in range(len(closet_distances[0][0]))]
            for i in range(len(meet_condition_threshold)):
                if self.__list_patient_ID[closet_distances[1][0][i]] == face_id[-1] and meet_condition_threshold[i]:
                    list_user_id.append({'user_id':face_id[-1], 'distance': str(closet_distances[0][0][i])})
                    break

        for user_id in list_user_id: 
            if (user_id['user_id'] in freq): 
                freq[user_id['user_id']] += 1
            else: 
                freq[user_id['user_id']] = 1
            
            if freq[user_id['user_id']] > max_people:
                max_people = freq[user_id['user_id']]
                return_user_id = user_id['user_id']
        
        print("\tNumber of received encoding face: {}".format(len(list_encoded_img)))
        print("\tNumber of predict face: {}".format(len(list_user_id)))
        # print(para.list_user_id)

        if len(list_user_id) != 0:
            list_distance = [np.float64(user_id['distance']) for user_id in list_user_id]
            print("\tMax distance of predict face: {}".format(np.max(list_distance)))
            print("\tMin distance of predict face: {}".format(np.min(list_distance)))

        if len(list_user_id) > NUMBER_USERS_RECOGNIZED and max_people >= FRAC_NUMBER_USERS_RECOGNIZED*len(list_user_id):
            return return_user_id
        else:
            return -1
    
    ######################################################################################
    # Identifying user                                                                   #
    # return:                                                                            #
    #           -1: Not exist otherwise user_id                                          #
    ######################################################################################
    def Identifying_User(self, data):
        res_msg = None
        try:
            list_encoded_img = []
            post_list_encoded_img = data.split(' ')
            for i in post_list_encoded_img:
                if i != '':
                    post_encoded_img = i.split('/')
                    encoded_img = [np.float64(j) for j in post_encoded_img if j != '']
                    encoded_img = np.array(encoded_img).reshape(1,-1)
                    list_encoded_img.append(encoded_img)
            
            user_ID = self.__Get_User_ID(list_encoded_img)

            if user_ID != -1:
                ret, name, birthday, phone, address = para.db.Get_Patient_Information(user_ID)
                if ret == -1:
                    res_msg = {'return': -1}
                else:
                    res_msg = {'return': 0, 'name': name, 'birthday': birthday, 'phone': phone, 'address': address}
            else:
                res_msg = {'return': -1}

            return res_msg
        except Exception as ex:
            print ( "\tHas error at module Identifying_User in identifying_user.py: {}".format(ex))
            return {'return': -1}
    
    def __TrainKNN(self):
        print("\tStarting train KNN Model")
        # Create and train the KNN classifier
        if len(self.__list_patient_ID) == 5:
            knn_clf = neighbors.KNeighborsClassifier(n_neighbors=5, algorithm=KNN_ALGORITHM, weights=KNN_WEIGHTS)
        else:
            knn_clf = neighbors.KNeighborsClassifier(n_neighbors=NUM_NEIGHBROS, algorithm=KNN_ALGORITHM, weights=KNN_WEIGHTS)

        # __known_face_encodings is list of ndarray
        # __known_face_IDs is list of str
        knn_clf.fit(self.__list_embedded_face, self.__list_patient_ID)

        print("\tFinishing train KNN Model")
        self.__knn_clf = knn_clf

    def __SaveData(self):
        with open(PATH_USER_IMG_ENCODED, 'wb') as fp_2:
            pickle.dump(self.__list_embedded_face, fp_2)
        
        with open(PATH_USER_ID, mode='wb') as fp_1:
            pickle.dump(self.__list_patient_ID, fp_1)

    def __SaveKNNModel(self):
        with open(KNN_MODEL_PATH, 'wb') as f:
            pickle.dump(self.__knn_clf, f)

    def Add_New_Patient(self, patient_ID, list_embedded_face):
        old_list_patient_ID = self.__list_patient_ID
        old_list_embedded_face = self.__list_embedded_face
        old_knn_clf = self.__knn_clf
        try:
            for embedded_face in list_embedded_face:
                self.__list_patient_ID.append(patient_ID)
                self.__list_embedded_face.append(embedded_face)
            
            self.__TrainKNN()
            self.__SaveData()
            self.__SaveKNNModel()
            return 0
        except Exception as e:
            print("Has error at Add_New_Patient in identifier_user: {}".format(e))
            self.__list_patient_ID = old_list_patient_ID
            self.__list_embedded_face = old_list_embedded_face
            self.__knn_clf = old_knn_clf
            return -1
    
    def Init_Data(self):
        self.__list_patient_ID = []
        self.__list_embedded_face = []
        self.__knn_clf = None
        self.__SaveData()
        self.__SaveKNNModel()


# test = IdentifyUser()
# test.Init_Data()
