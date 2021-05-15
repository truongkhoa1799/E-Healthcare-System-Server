import os
import pickle
import numpy as np
import sys
sys.path.append('/Users/khoatr1799/GitHub/E-Healthcare-System-Server')

from sklearn import neighbors
from parameters import *
from common_functions.utils import LogMesssage

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
        self.__list_embedded_face = [] # [(128, ), (128, ), ...]
        self.__list_patient_ID = []
        self.__knn_clf = None
        ret, self.__list_patient_ID, self.__list_embedded_face = self.__LoadData()
        if ret == -1:
            LogMesssage('There is no user id or encoding face face to load', opt=2)
            exit(-1)

        ret, self.__knn_clf = self.__LoadKNNModel()
        if ret == -1:
            LogMesssage('There is KNN model to load', opt=2)
            exit(-1)
        
        LogMesssage('\tLoaded users data for encoding')
        LogMesssage('\tNumber of users: {num_users}'.format(num_users=len(self.__list_patient_ID)//5))
        
        # print(self.__list_patient_ID)

        # print(self.__list_embedded_face)
        # print(self.__list_patient_ID)
        # print(type(self.__list_patient_ID[0]))

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

    ###############################################################################################
    # GetFaceID                                                                                   #                    
    # Input:                                                                                      #
    #   ndarray         [(1, 128), (1, 128), ...]                                                 #
    # Output:                                                                                     #
    #   Str             UserID                      :                                             #
    ###############################################################################################
    def __getPatientID(self, list_encoded_img):
        list_patient_ID = []
        freq = {}
        max_people = 0
        return_patient_ID = None
        
        for embedded_img in list_encoded_img:
            # print(embedded_img.shape)
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
                    list_patient_ID.append({'patient_ID':face_id[-1], 'distance': str(closet_distances[0][0][i])})
                    break

        for patient_ID in list_patient_ID: 
            if (patient_ID['patient_ID'] in freq): 
                freq[patient_ID['patient_ID']] += 1
            else: 
                freq[patient_ID['patient_ID']] = 1
            
            if freq[patient_ID['patient_ID']] > max_people:
                max_people = freq[patient_ID['patient_ID']]
                return_patient_ID = patient_ID['patient_ID']

        
        LogMesssage('\t[__getPatientID]: Number of encoding face Number of predict face : {face_received}'.format(face_received=len(list_encoded_img)))
        LogMesssage('\t[__getPatientID]: Number of face predicted                       : {face_predicted}'.format(face_predicted=len(list_patient_ID)))
        LogMesssage('\t[__getPatientID]: Max number users predicted                     : {max_user_predicted}'.format(max_user_predicted=max_people))
        

        if len(list_patient_ID) != 0:
            list_distance = [np.float64(patient_ID['distance']) for patient_ID in list_patient_ID]
            LogMesssage('\t[__getPatientID]: Max distance of predict face                   : {max}'.format(max=np.max(list_distance)))
            LogMesssage('\t[__getPatientID]: Min distance of predict face                   : {min}'.format(min=np.min(list_distance)))
            LogMesssage('\t[__getPatientID]: Mean distance of predict face                  : {mean}'.format(mean=np.mean(list_distance)))

        if len(list_patient_ID) > NUMBER_USERS_RECOGNIZED and max_people >= FRAC_NUMBER_USERS_RECOGNIZED*len(list_patient_ID):
            return return_patient_ID
        else:
            return -1

    
    def __TrainKNN(self):
        LogMesssage("\t[__TrainKNN]: Starting train KNN Model")
        # Create and train the KNN classifier
        if len(self.__list_patient_ID) == 5:
            knn_clf = neighbors.KNeighborsClassifier(n_neighbors=5, algorithm=KNN_ALGORITHM, weights=KNN_WEIGHTS)
        else:
            knn_clf = neighbors.KNeighborsClassifier(n_neighbors=NUM_NEIGHBROS, algorithm=KNN_ALGORITHM, weights=KNN_WEIGHTS)

        # __known_face_encodings is list of ndarray
        # __known_face_IDs is list of str
        knn_clf.fit(self.__list_embedded_face, self.__list_patient_ID)

        LogMesssage("\t[__TrainKNN]: Finishing train KNN Model")
        self.__knn_clf = knn_clf

    def __SaveData(self):
        with open(PATH_USER_IMG_ENCODED, 'wb') as fp_2:
            pickle.dump(self.__list_embedded_face, fp_2)
        
        with open(PATH_USER_ID, mode='wb') as fp_1:
            pickle.dump(self.__list_patient_ID, fp_1)

    def __SaveKNNModel(self):
        with open(KNN_MODEL_PATH, 'wb') as f:
            pickle.dump(self.__knn_clf, f)

    # return 0: success, -1: fail
    # list_embedded_imgs_stored_db_decoded: [(128, ), (128, )]
    def __getImagePatientsOnDB(self, patient_ID):
        ret, list_embedded_imgs_stored_db = para.db.Get_Patient_Img(patient_ID)
        if ret != 0:
            LogMesssage("[__getImagePatientsOnDB]: Fail to get patient's embedded with patient's SSN", opt=2)
            return -1, None
        else:
            LogMesssage("[__getImagePatientsOnDB]: Successfully get patient's embedded with patient's SSN")

        ######################################################################
        # decoding images stored on db                                       #
        ######################################################################
        list_embedded_imgs_stored_db_decoded = []
        for i in list_embedded_imgs_stored_db:
            image = i.split('/')
            encoded_img = [np.float64(j) for j in image if j != '']
            encoded_img = np.array(encoded_img)
            list_embedded_imgs_stored_db_decoded.append(encoded_img)

        return 0, list_embedded_imgs_stored_db_decoded

##########################################################################################
# PUBLIC METHOD                                                                          #
##########################################################################################
    ######################################################################################
    # Identifying user                                                                   #
    # return:                                                                            #
    #           -1: Not exist otherwise patient_ID                                          #
    #           -2: patient is wearing mask                                              #
    #           -3: invalid ssn                                                          #
    ######################################################################################
    def Identifying_User(self, embedded_face, ssn):
        try:
            list_embedded_imgs_validation_decoded = []
            post_list_encoded_img = embedded_face.split(' ')
            for i in post_list_encoded_img:
                if i != '':
                    post_encoded_img = i.split('/')
                    encoded_img = [np.float64(j) for j in post_encoded_img if j != '']
                    encoded_img = np.array(encoded_img).reshape(1,-1)
                    list_embedded_imgs_validation_decoded.append(encoded_img)   # [(1, 128), (1, 128), ...]
            ##############################################################################
            # patient do not use second authority                                        #
            ##############################################################################
            if ssn == "-1":
                LogMesssage("[Identifying_User]: Normal Validation Patient")
                patient_ID = self.__getPatientID(list_embedded_imgs_validation_decoded)
                LogMesssage("[Identifying_User]: Predict patient with ID: {}".format(patient_ID))

                # wearing mask
                if patient_ID == -2:
                    LogMesssage("[Identifying_User]: Detected patient was wearing mask", opt=2)
                    return {'return': -2}

                elif patient_ID != -1:
                    ret, name, birthday, phone, address = para.db.Get_Patient_Information(patient_ID)
                    if ret == -1:
                        LogMesssage("[Identifying_User]: Cannot get patient's information", opt=2)
                        return {'return': -1}
                    else:
                        LogMesssage("[Identifying_User]: Successfully get patient's information")
                        return {'return': 0, 'patient_ID': patient_ID, 'name': name, 'birthday': birthday, 'phone': phone, 'address': address}

                else:
                    LogMesssage("[Identifying_User]: Fail to classifying patient's information", opt=2)
                    return {'return': -1}
            
            ##############################################################################
            # patient use second authority                                               #
            ##############################################################################
            else:
                index_replace_img = None
                replace_img = None
                min_distance = 10
                LogMesssage("[Identifying_User]: Validation Patient With SSN")

                ret, patient_ID = para.db.getPatientIDWithSSN(ssn)
                if ret == -1:
                    LogMesssage("[Identifying_User]: Fail to get patient id with patient's SSN", opt=2)
                    return {'return': -3}
                else:
                    LogMesssage("[Identifying_User]: Success get patient id with patient's SSN")

                ##########################################################################
                # Check whether this user is active or not. if not active                #
                ##########################################################################
                if self.CheckExistPatient(patient_ID) != 0:
                    LogMesssage("[Identifying_User]: Patient is not active. Load patient image from database and active")
                    
                    # Load images and decode from db
                    ret, list_embedded_imgs_stored_db_decoded = self.__getImagePatientsOnDB(patient_ID)
                    if ret == -1:
                        return {'return': -3}

                    # Start to train KNN model
                    para.lock_train_patient.acquire()
                    ret_add_new_patient = self.Add_New_Patient(patient_ID, list_embedded_imgs_stored_db_decoded)
                    para.lock_train_patient.release()
                    if ret_add_new_patient == -1:
                        LogMesssage('\t[Identifying_User]: Fail to activate patient with id: {id}'.format(id=patient_ID), opt=2)
                        return {'return': -3}
                    else:
                        LogMesssage('\t[Identifying_User]: Successfully activate patient with id: {id}'.format(id=patient_ID))
                else:
                    LogMesssage("[Identifying_User]: Patient is active")

                ##########################################################################
                # Check whether patient is match with local data or not                  #
                ##########################################################################
                list_distance = []
                list_embedded_imgs_stored_local_decoded = np.array([self.__list_embedded_face[i] for i in range(len(self.__list_patient_ID)) if self.__list_patient_ID[i] == patient_ID])
                # print(list_embedded_imgs_stored_local_decoded.shape)
                
                for i in range(len(list_embedded_imgs_validation_decoded)):
                    list_dup_img = np.array(5*[list_embedded_imgs_validation_decoded[i][0]])
                    ret = np.linalg.norm(list_embedded_imgs_stored_local_decoded - list_dup_img, axis=1)
                    # print(ret)
                    current_min_distance = np.amin(ret)
                    if current_min_distance< min_distance:
                        min_distance = current_min_distance
                        index_replace_img = i
                        replace_img = list_embedded_imgs_validation_decoded[i][0]
                    list_distance.append(ret)
                
                LogMesssage("[Identifying_User]: Index of image: {} with min distance: {} will replace".format(index_replace_img, min_distance))
                # print(replace_img)
                # print(replace_img.shape)
                # print(self.__list_embedded_face[0].shape)
                list_distance = np.array(list_distance)
                list_distance = np.reshape(list_distance, (1, -1))
                mean_distance = np.mean(list_distance)
                LogMesssage("[Identifying_User]: Mean distance for verifying patient: {}".format(mean_distance))

                patient_ID = int(patient_ID)
                if mean_distance <= THRESHOLD_VERIFY_FACE:
                    LogMesssage("[Identifying_User]: Successfully verify patient with SSN")

                    # Update replace image

                    LogMesssage("[Identifying_User]: Successfully update newer image of patient")
                    ret, name, birthday, phone, address = para.db.Get_Patient_Information(patient_ID)
                    return {'return': 0, 'patient_ID': patient_ID, 'name': name, 'birthday': birthday, 'phone': phone, 'address': address}
                else:
                    LogMesssage("[Identifying_User]: Cannot verify patient with SSN", opt=2)

            return {'return': -1}

        except Exception as e:
            LogMesssage('\t[Identifying_User]: Has error at module Identifying_User in identifying_user.py: {error}'.format(error=e), opt=2)
            return {'return': -1}
    
    def Add_New_Patient(self, patient_ID, list_embedded_face):
        patient_ID = int(patient_ID)

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

            LogMesssage("\t[Add_New_Patient]: Patient: {} was added successfully new patient's embedded images".format(patient_ID))
            return 0
        except Exception as e:
            LogMesssage('\t[Add_New_Patient]: Has error at Add_New_Patient in identifier_user: {error}.'.format(error=e), opt=2)
            self.__list_patient_ID = old_list_patient_ID
            self.__list_embedded_face = old_list_embedded_face
            self.__knn_clf = old_knn_clf
            LogMesssage('\t[Add_New_Patient]: Successfully reverse to previous data', opt=2)
            return -1
    
    def CheckExistPatient(self, patient_ID):
        # 0: exist
        # -1: none
        if patient_ID in self.__list_patient_ID:
            return 0
        else:
            return -1
    
    def Init_Data(self):
        self.__list_patient_ID = []
        self.__list_embedded_face = []
        self.__knn_clf = None
        self.__SaveData()
        self.__SaveKNNModel()

    def Delete_Patient(self, patient_ID):
        check_exist = False
        for i in range(len(self.__list_patient_ID)-1, -1, -1):
            print(self.__list_patient_ID[i])
            if self.__list_patient_ID[i] == patient_ID:
                check_exist = True
                self.__list_embedded_face.pop(i)
                self.__list_patient_ID.pop(i)
        
        if check_exist == False:
            return -1
        # print(self.__list_patient_ID)
        self.__TrainKNN()
        self.__SaveData()
        self.__SaveKNNModel()
        return 0

# test = IdentifyUser()
# test.Delete_Patient(10)