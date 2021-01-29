EVENT_HUB_CONNECTION = "Endpoint=sb://receivemsgsfromdevices.servicebus.windows.net/;SharedAccessKeyName=RootManageSharedAccessKey;SharedAccessKey=lM4liPS83Rni9DE72LJg2swfELncFmBKOIYTKm81eQY="
EVENT_HUB_NAME = "receivemsg"

STORAGE_CONNECTION = "DefaultEndpointsProtocol=https;AccountName=hospitalstoragethesis;AccountKey=Sr8cft9eLH9tp//4a1zlz7KXugQgyEw89zAXPFD4N8tHknhPlPmZjAV3j2N+b3XTBNoIpdEehtUPELhLzBFFbA==;EndpointSuffix=core.windows.net"
BLOB_NAME = "thesis"

IOTHUB_CONNECTION = "HostName=E-HealthCare.azure-devices.net;SharedAccessKeyName=ServerRight;SharedAccessKey=coR5OV6uuuBPCxSriI7DibJsw+XiCb6255cONqZ6JWg="

# KNN MODEL
KNN_MODEL_PATH = "/Users/khoa1799/GitHub/E-Healthcare-System-Server/model_engine/knn_clf_model.clf"

# USER INFORMATION
PATH_USER_IMG_ENCODED = "/Users/khoa1799/GitHub/E-Healthcare-System-Server/model_engine/encoded_img"
PATH_USER_ID = "/Users/khoa1799/GitHub/E-Healthcare-System-Server/model_engine/id_user"

# FACE RECOGNITION MODEL
PREDICTOR_5_POINT_MODEL = '/Users/khoa1799/GitHub/E-Healthcare-System-Server/model_engine/shape_predictor_5_face_landmarks.dat'
RESNET_MODEL = '/Users/khoa1799/GitHub/E-Healthcare-System-Server/model_engine/dlib_face_recognition_resnet_model_v1.dat'

# Data
FACE_TEST_PATH = "/Users/khoa1799/GitHub/E-Healthcare-System-Server/Face_Data/test"
FACE_TRAIN_PATH = "/Users/khoa1799/GitHub/E-Healthcare-System-Server/Face_Data/train"
DATA_PATH = "/Users/khoa1799/GitHub/E-Healthcare-System-Server/Face_Data/"

# Parameters for image processing, and KNN model
IMAGE_SIZE = 150
BASE_BRIGHTNESS = 180
THRESHOLD_FACE_REC = 0.5
NUM_JITTERS = 1
NUM_NEIGHBROS = 3
KNN_ALGORITHM = 'ball_tree'
KNN_WEIGHTS = 'distance'

THRESHOLD_PATIENT_REC = 5

CREATE_USER_REPONSE_METHOD = "Validate_User"


class Parameters:
    def __init__(self):
        # DB
        self.db = None
        
        # Identifying user
        self.identifying_user = None
        self.list_encoded_img = []
        self.list_user_id = []
        self.return_user_id = None

        # Connect IoT hub and Event Hub
        self.iothub_registry_manager = None
        # Create an Azure blob checkpoint store to store the checkpoints.
        self.checkpoint_store = None

        self.request_data = None
        self.request_msg = {"0": 'Validate_User', "1": 'Send_Examination'}


para = Parameters()