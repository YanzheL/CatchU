import tensorflow as tf
import os
import sys
from utils.config import Configure
session_conf=Configure().deserialize('session')

SESSION_CONF = {
    'config': tf.ConfigProto(
        gpu_options=tf.GPUOptions(
            per_process_gpu_memory_fraction=session_conf.getfloat('per_process_gpu_memory_fraction')
        ),
        log_device_placement=session_conf.getboolean('log_device_placement'),
        allow_soft_placement=session_conf.getboolean('allow_soft_placement')
    )
}

THREADING_CONF = {
    'workers': 100,
    'input_que_size': 60,
    'output_que_size': 60,
    'worker_spec': {
        # 'resize_height': 350,
        'resize_height': 350,
    }
}

PRODUCER_CONF = {
    'datasource': os.path.join(sys.path[0], 'video.mp4')
}

# print(os.path.abspath('models/facenet/CASIA-WebFace'))
# print(os.path.abspath('models/facenet/knn_classifier.model'))
DETECTOR_CONF = {
    'model_folder': os.path.join(sys.path[0], 'models/facenet/CASIA-WebFace'),
    'name': 'mtcnnfacenet',
    # 'min_face_size': 50,
    'min_face_ratio': 0.2
}

RECOGNIZER_CONF = {
    'classifier': os.path.join(sys.path[0], 'models/facenet/knn_classifier.model'),
    'chip_size': 96
}

GUI_CONF = {
    'preferred_fps': 24
}
