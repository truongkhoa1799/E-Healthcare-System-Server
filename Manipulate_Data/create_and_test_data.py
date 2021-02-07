import time
import os
import sys
import re
import cv2
import pickle
import numpy as np
from sklearn import neighbors
sys.path.append('/Users/khoa1799/GitHub/E-Healthcare-System-Server')
from sklearn.metrics import precision_score
from sklearn.metrics import recall_score

from parameters import *
from common_functions.face_recognition import FaceRecognition

def __image_files_in_folder(folder):
    return [os.path.join(folder, f) for f in os.listdir(folder) if re.match(r'.*\.(jpg|jpeg|png)', f, flags=re.I)]

###############################################################################################
# __LoadNewData                                                                               #                    
# Input:                                                                                      #
#   None            None                        :   None                                      #
# Output:                                                                                     #
#   ret                                         :   -1 No Data Loaded, 0 success              #
###############################################################################################
def LoadOriginalData(face_rec):
    time_request = time.time()
    list_embedded_face = []
    list_user_ID = []
    temp_list = [1,2]

    # Loop through each person in the training set
    for class_dir in os.listdir(os.path.join(ORIGINAL_DATA, 'train')):
        print(class_dir)
        if not os.path.isdir(os.path.join(ORIGINAL_DATA, 'train', class_dir)) or int(class_dir) not in temp_list:
            continue
        
        # Loop through each training image for the current person and past image path for encoing individualy
        for img in __image_files_in_folder(os.path.join(ORIGINAL_DATA, 'train', class_dir)):
            path = img.split('/')
            user_ID = int(class_dir)
            img_name = path[-1]
            loaded_img = cv2.imread(img)
            print("Loaded image {} ".format(img_name))
            
            ret, face = face_rec.Get_Face(loaded_img)
            if ret == 0:
                embedded_face = face_rec.Encoding_Face(face)
            else:
                exit(-1)

            list_embedded_face.append(embedded_face)
            list_user_ID.append(user_ID)

    print("\ttime load data {}".format(time.time() - time_request))

    if len(list_embedded_face) != len(list_embedded_face) \
        or len(list_embedded_face) == 0 \
        or len(list_user_ID) == 0:
        return -1, None, None

    return 0, list_user_ID, list_embedded_face

###############################################################################################
# __SaveData                                                                                  #                    
# Input:                                                                                      #
#   None            None                        :   None                                      #
# Output:                                                                                     #
#   ret             int                         :   -1 No Data Loaded, 0 success              #
###############################################################################################
def SaveData(list_user_ID, list_embedded_face):
    with open(PATH_USER_ID, mode='wb') as fp_1:
        pickle.dump(list_user_ID, fp_1)
    
    with open(PATH_USER_IMG_ENCODED, 'wb') as fp_2:
        pickle.dump(list_embedded_face, fp_2)
    

# #################################################################################
# # __SaveKNNModel                                                                #                    
# # Input:                                                                        #
# #   knn_clf         :   Model after trained                                     #
# #   model_save_path :   path to save model                                      #
# # Output:                                                                       #
# #   ret             :   -1 no path, 0 success                                   #
# #################################################################################
def SaveKNNModel( knn_clf,model_save_path):
    if model_save_path is not None:
        with open(model_save_path, 'wb') as f:
            pickle.dump(knn_clf, f)

###############################################################################################
# __TrainKNN                                                                                  #                    
# Input:                                                                                      #
#   int             n_neighbors                 :   Bumber of neighbors                       #
#   str             knn_algorithm               :   algorithm implement KNN                   #
#   str             knn_weights                 :   weights to calculate diff                 #
# Output:                                                                                     #
#   knn_clf         knn_clf                     :   knn classification model                  #
###############################################################################################
def TrainKNN( n_neighbors, knn_algorithm, knn_weights, list_user_ID, list_embedded_face):
    print("Starting train KNN Model")
    # Determine how many neighbors to use for weighting in the KNN classifier
    if n_neighbors is None:
        n_neighbors = int(round(math.sqrt(len(list_embedded_face))))
        print("Chose n_neighbors automatically:", n_neighbors)

    # Create and train the KNN classifier
    knn_clf = neighbors.KNeighborsClassifier(n_neighbors=n_neighbors, algorithm=knn_algorithm, weights=knn_weights)

    # __known_face_encodings is list of ndarray
    # __known_face_IDs is list of str
    knn_clf.fit(list_embedded_face, list_user_ID)

    print("Finishing train KNN Model")
    return knn_clf

def Test(list_user_ID, list_embedded_face, knn_clf):
    predict_knwon_user = []
    real_user = []
    temp_list = [1,2]
    # Loop through each person in the training set
    for class_dir in os.listdir(os.path.join(ORIGINAL_DATA, 'test')):
        # print(class_dir)
        if not os.path.isdir(os.path.join(os.path.join(ORIGINAL_DATA, 'test', class_dir))) or int(class_dir) not in temp_list:
            continue

        for img in __image_files_in_folder(os.path.join(ORIGINAL_DATA, 'test', class_dir)):
            path = img.split('/')
            real_user.append(int(class_dir))
            # print(class_dir)
            
            img_name = path[-1]
            loaded_img = cv2.imread(img)
            # print("Loaded image {} ".format(img_name))

            ret, face = face_rec.Get_Face(loaded_img)
            if ret == 0:
                has_face = False
                embedded_face = face_rec.Encoding_Face(face)
                embedded_face = np.array(embedded_face).reshape(1,-1)

                user_id = knn_clf.predict(embedded_face)
                closet_distances = knn_clf.kneighbors(embedded_face, n_neighbors = NUM_NEIGHBROS)
                print(closet_distances)
                meet_condition_threshold = [closet_distances[0][0][i] <= THRESHOLD_FACE_REC for i in range(len(closet_distances[0][0]))]
                
                for i in range(len(meet_condition_threshold)):
                    if list_user_ID[closet_distances[1][0][i]] == user_id[-1] and meet_condition_threshold[i]:
                        predict_knwon_user.append(user_id[-1])
                        # print("\t{}".format(user_id[-1]))
                        has_face = True
                        break
                if has_face == False:
                    predict_knwon_user.append(-1)
            else:
                exit(-1)
    
    print("Real known person")
    print(real_user)
    print()
    print("Predict known person")
    print(predict_knwon_user)
    print()

    # precision_score_known_faces = precision_score(real_user, predict_knwon_user, average='weighted')
    # recall_score_known_faces = recall_score(real_user, predict_knwon_user, average='weighted')

    # print("\t\tPrecision score: {}".format(precision_score_known_faces))
    # print("\t\tRecall score: {}".format(recall_score_known_faces))
    # print()

    # predict_unknwon_user = []
    # # Loop through each person in the training set
    # for img in __image_files_in_folder(os.path.join(UNKNOWN_DATA)):
    #     loaded_img = cv2.imread(img)
    #     print(img)
    #     # print("Loaded image {} ".format(img_name))
    #     has_face = False

    #     embedded_face = face_rec.Encoding_Face(loaded_img)
    #     embedded_face = np.array(embedded_face).reshape(1,-1)

    #     user_id = knn_clf.predict(embedded_face)
    #     closet_distances = knn_clf.kneighbors(embedded_face, n_neighbors = NUM_NEIGHBROS)
    #     meet_condition_threshold = [closet_distances[0][0][i] <= THRESHOLD_FACE_REC for i in range(len(closet_distances[0][0]))]
        
    #     for i in range(len(meet_condition_threshold)):
    #         if list_user_ID[closet_distances[1][0][i]] == user_id[-1] and meet_condition_threshold[i]:
    #             predict_unknwon_user.append(user_id[-1])
    #             has_face = True
    #             break
    #     if has_face == False:
    #         predict_unknwon_user.append(-1)
    
    # print("Predict unknown person")
    # print(predict_unknwon_user)
    # print()

if __name__ == '__main__':
    face_rec = FaceRecognition()
    ret, list_user_ID, list_embedded_face = LoadOriginalData(face_rec)
    SaveData(list_user_ID, list_embedded_face)
    print(list_user_ID)

    knn_clf = TrainKNN(NUM_NEIGHBROS, KNN_ALGORITHM, KNN_WEIGHTS, list_user_ID, list_embedded_face)
    SaveKNNModel(knn_clf, KNN_MODEL_PATH)
    Test(list_user_ID, list_embedded_face, knn_clf)