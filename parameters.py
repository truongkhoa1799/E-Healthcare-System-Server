# AZURE SERVICES
EVENT_HUB_CONNECTION = "Endpoint=sb://receivemsgsfromdevices.servicebus.windows.net/;SharedAccessKeyName=RootManageSharedAccessKey;SharedAccessKey=lM4liPS83Rni9DE72LJg2swfELncFmBKOIYTKm81eQY="
EVENT_HUB_NAME = "receivemsg"

STORAGE_CONNECTION = "DefaultEndpointsProtocol=https;AccountName=hospitalstoragethesis;AccountKey=Sr8cft9eLH9tp//4a1zlz7KXugQgyEw89zAXPFD4N8tHknhPlPmZjAV3j2N+b3XTBNoIpdEehtUPELhLzBFFbA==;EndpointSuffix=core.windows.net"
BLOB_RECEIVE_EVENT = "thesis"
BLOB_RECEIVE_IMG = "imgnewusers"
IMAGE_NEW_PATIENT = "/Users/khoa1799/GitHub/E-Healthcare-System-Server/file_img_new_user"

IOTHUB_CONNECTION = "HostName=E-HealthCare.azure-devices.net;SharedAccessKeyName=ServerRight;SharedAccessKey=coR5OV6uuuBPCxSriI7DibJsw+XiCb6255cONqZ6JWg="

# KNN MODEL
KNN_MODEL_PATH = "/Users/khoa1799/GitHub/E-Healthcare-System-Server/model_engine/knn_clf_model.clf"

# USER INFORMATION
PATH_USER_IMG_ENCODED = "/Users/khoa1799/GitHub/E-Healthcare-System-Server/model_engine/encoded_img"
PATH_USER_ID = "/Users/khoa1799/GitHub/E-Healthcare-System-Server/model_engine/id_user"

# FACE RECOGNITION MODEL
PREDICTOR_5_POINT_MODEL = '/Users/khoa1799/GitHub/E-Healthcare-System-Server/model_engine/shape_predictor_5_face_landmarks.dat'
RESNET_MODEL = '/Users/khoa1799/GitHub/E-Healthcare-System-Server/model_engine/dlib_face_recognition_resnet_model_v1.dat'
CNN_FACE_DETECTOR = '/Users/khoa1799/GitHub/E-Healthcare-System-Server/model_engine/mmod_human_face_detector.dat'

# Data
ORIGINAL_DATA = "/Users/khoa1799/GitHub/E-Healthcare-System-Server/Manipulate_Data/Original_Face"
PRCESSED_DATA = "/Users/khoa1799/GitHub/E-Healthcare-System-Server/Manipulate_Data/Prcessed_Face"
UNKNOWN_DATA = "/Users/khoa1799/GitHub/E-Healthcare-System-Server/Manipulate_Data/unknown_people"

# Parameters for image processing, and KNN model
IMAGE_SIZE = 150
BASE_BRIGHTNESS = 180
THRESHOLD_FACE_REC = 0.42
NUM_JITTERS = 1
NUM_NEIGHBROS = 10
KNN_ALGORITHM = 'ball_tree'
KNN_WEIGHTS = 'distance'

FRAC_NUMBER_USERS_RECOGNIZED = 0.7
NUMBER_USERS_RECOGNIZED = 18

CREATE_USER_REPONSE_METHOD = "Validate_User"


class Parameters:
    def __init__(self):
        # DB
        self.db = None
        
        # Identifying user
        self.identifying_user = None
        self.face_recognition = None
        self.return_user_id = None

        # Connect IoT hub and Event Hub
        self.iothub_registry_manager = None
        # Create an Azure blob checkpoint store to store the checkpoints.
        self.checkpoint_store = None
        self.image_user_container = None

        self.image_user_container = None

        self.request_msg = {"0": 'Validate_User', "1": 'Send_Examination', "2": 'Create_Patient', "3": "Create_New_Device", "4": "Get_Examination_Room"}


para = Parameters()