import pickle
import numpy as np
import cv2
import sys
sys.path.append('/Users/khoa1799/GitHub/E-Healthcare-System-Server')

# import face_recognition
import dlib
from parameters import *
from common_functions.utils import LogMesssage

class FaceRecognition:
    def __init__(self):
        # pose 68 points and point 5 do not affect the performance of encoding
        if MODEL_SHAPE_PREDICTOR == '68':
            LogMesssage('\tLoad SHAPE_PREDICTOR 68')
            self.__pose_predictor = dlib.shape_predictor(PREDICTOR_68_POINT_MODEL)
        else:
            LogMesssage('\tLoad SHAPE_PREDICTOR 5')
            self.__pose_predictor = dlib.shape_predictor(PREDICTOR_5_POINT_MODEL)
        
        if MODEL_FACE_DETECTOR == 'cnn':
            LogMesssage('\tLoad FACE_DETECTOR CNN')
            self.__face_detector_cnn = dlib.cnn_face_detection_model_v1(CNN_FACE_DETECTOR)
        else:
            LogMesssage('\tLoad FACE_DETECTOR HOG')
            self.__face_detector = dlib.get_frontal_face_detector()

        self.__face_encoder = dlib.face_recognition_model_v1(RESNET_MODEL)
        
        test_img = None
        with open ('/Users/khoa1799/GitHub/E-Healthcare-System-Server/model_engine/test_encoding_img', mode='rb') as f1:
            test_img = pickle.load(f1)

        test_encoded = self.__face_encodings(test_img, [(1, 149, 1, 149)])
        # (top, right, bottom, left)
        # sub-image = image[top:bottom, left:right]
        # ret = self.__Get_Face_Locations(test_img, model = 'hog')[0]
        # print(ret)
        # cv2.imshow('test', test_img[ret[0]:ret[2], ret[3]:ret[1]])
        # cv2.waitKey(2000)
        # time.sleep(1)

        LogMesssage('\tDone load dlib model')
    
    def __AdjustBright(self, img):
        hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV) #convert it to hsv
        v = hsv_img[:, :, 2]
        mean_v = np.mean(v)
        diff = BASE_BRIGHTNESS - mean_v
                    
        if diff < 0:
            v = np.where(v < abs(diff), v, v + diff)
        else:
            v = np.where( v + diff > 255, v, v + diff)

        hsv_img[:, :, 2] = v
        ret_img = cv2.cvtColor(hsv_img, cv2.COLOR_HSV2BGR)
        # return BRG image
        return ret_img
        
    def Preprocessing_Img(self, img):
        resized_img = cv2.resize(img, (IMAGE_SIZE,IMAGE_SIZE))
        resized_adjusted_bright_img = self.__AdjustBright(resized_img)
        RGB_resized_adjusted_bright_img = cv2.cvtColor(resized_adjusted_bright_img, cv2.COLOR_BGR2RGB)
        return RGB_resized_adjusted_bright_img
    
    ###############################################################################################
    # face_encodings                                                                              #
    # Input:                                                                                      #
    #   list_ndarray    face_image :   image to encode                                            #
    #   list_str        known_face_locations       :   bounding box for face                      #
    # Output:                                                                                     #
    #   None            128-vector                        :   encoding vector                     #
    ###############################################################################################
    def __face_encodings(self, face_image, known_face_locations):
        raw_landmarks = self.Get_Landmarks(face_image, known_face_locations)
        return [np.array(self.__face_encoder.compute_face_descriptor(face_image, raw_landmark_set, 1)) for raw_landmark_set in raw_landmarks]

    ###############################################################################################
    # _css_to_rect                                                                                #
    # Input:                                                                                      #
    #   list_ndarray    css(left, top, right, bottm)            :   bounding box                  #
    # Output:                                                                                     #
    #   None            dlib.rectangle(bottom, left, top, right):   encoding vector               #
    ###############################################################################################
    def __css_to_rect(self, css):
        return dlib.rectangle(css[3], css[0], css[1], css[2])

    def __rect_to_css(self, rect):
        """
        Convert a dlib 'rect' object to a plain tuple in (top, right, bottom, left) order

        :param rect: a dlib 'rect' object
        :return: a plain tuple representation of the rect in (top, right, bottom, left) order
        """
        return rect.top(), rect.right(), rect.bottom(), rect.left()

    def __trim_css_to_bounds(self, css, image_shape):
        """
        Make sure a tuple in (top, right, bottom, left) order is within the bounds of the image.

        :param css:  plain tuple representation of the rect in (top, right, bottom, left) order
        :param image_shape: numpy shape of the image array
        :return: a trimmed plain tuple representation of the rect in (top, right, bottom, left) order
        """
        return max(css[0], 0), min(css[1], image_shape[1]), min(css[2], image_shape[0]), max(css[3], 0)

    def __raw_face_locations(self, img, number_of_times_to_upsample):
        """
        Returns an array of bounding boxes of human faces in a image

        :param img: An image (as a numpy array)
        :param number_of_times_to_upsample: How many times to upsample the image looking for faces. Higher numbers find smaller faces.
        :param model: Which face detection model to use. "hog" is less accurate but faster on CPUs. "cnn" is a more accurate
                    deep-learning model which is GPU/CUDA accelerated (if available). The default is "hog".
        :return: A list of dlib 'rect' objects of found face locations
        """
        if MODEL_FACE_DETECTOR == "cnn":
            return self.__face_detector_cnn(img, number_of_times_to_upsample)
        else:
            return self.__face_detector(img, number_of_times_to_upsample)


    def __raw_face_landmarks(self, face_image, face_locations):
        if face_locations is None:
            face_locations = self.__raw_face_locations(face_image)
        else:
            face_locations = [self.__css_to_rect(face_location) for face_location in face_locations]

        return [self.__pose_predictor(face_image, face_location) for face_location in face_locations]

    def Encoding_Face(self, img):
        # Pre-processing
        RGB_resized_adjusted_bright_img = self.Preprocessing_Img(img)

        embedded_face = self.__face_encodings(RGB_resized_adjusted_bright_img, [(0, IMAGE_SIZE, IMAGE_SIZE,0)])[0]
        return embedded_face

    def __Get_Face_Locations(self, img):
        """
        Returns an array of bounding boxes of human faces in a image

        :param img: An image (as a numpy array)
        :param number_of_times_to_upsample: How many times to upsample the image looking for faces. Higher numbers find smaller faces.
        :param model: Which face detection model to use. "hog" is less accurate but faster on CPUs. "cnn" is a more accurate
                    deep-learning model which is GPU/CUDA accelerated (if available). The default is "hog".
        :return: A list of tuples of found face locations in css (top, right, bottom, left) order
        """
        if MODEL_FACE_DETECTOR == "cnn":
            return [self.__trim_css_to_bounds(self.__rect_to_css(face.rect), img.shape) for face in self.__raw_face_locations(img, 1)]
        else:
            return [self.__trim_css_to_bounds(self.__rect_to_css(face), img.shape) for face in self.__raw_face_locations(img, 1)]

    def Get_Face(self, img):
        try:
            ret, face_location = self.Get_Location_Face(img)
            if ret == 0:
            # img[top:bottom, left:right]
                face = img[face_location[0]:face_location[1], face_location[2]:face_location[3]]
                return ret, face
            else:
                return -1, None
        except Exception as e:
            LogMesssage('Has error in Get_Location_Face of face_recognition: {error}'.format(error=e), opt=2)
            return -1, None
    
    def Get_Landmarks(self, face_image, known_face_locations):
        raw_landmarks = self.__raw_face_landmarks(face_image, known_face_locations)
        return raw_landmarks
    
    def Get_Location_Face(self, img):
        try:
            fra = 300 / max(img.shape[0], img.shape[1]) 
            resized_img = cv2.resize(img, (int(img.shape[1] * fra), int(img.shape[0] * fra)))
            GRAY_resized_img = cv2.cvtColor(resized_img, cv2.COLOR_BGR2GRAY)

            ret = self.__Get_Face_Locations(GRAY_resized_img)
            if len(ret) == 0:
                LogMesssage('Cannot find location of face in image', opt=2)
                return -1, None
            elif len(ret) != 1:
                LogMesssage('Has many faces in image', opt=2)
                return -2, None

            # location = (top, rigth, bottom, left)

            top = int(ret[0][0] / fra)
            bottom = int(ret[0][2] / fra)
            left = int(ret[0][3] / fra)
            right = int(ret[0][1] / fra)
            
            face_location = (top, bottom, left, right)
            return 0, face_location
        except Exception as e:
            LogMesssage('Has error in Get_Face of face_recognition, {error}'.format(error=e), opt=2)
            return -3, None

# test = FaceRecognition()
# img = cv2.imread(ORIGINAL_DATA + '/1/IMG_3415.jpg')
# ret, face = test.Get_Face(img)
# cv2.imshow('test', face)
# cv2.waitKey(2000)