import tensorflow as tf
from third_party.facenet.src.align import detect_face
from third_party.mxnet_mtcnn.mtcnn_detector import MtcnnDetector
# import logging
import cv2
import time
from utils.logger_router import LoggerRouter

logger = LoggerRouter().getLogger(__name__)

facial_area_ratio = 0.06

min_face_size = 48
threshold = [0.6, 0.7, 0.7]
factor = 0.709

session_opts = {
    'config': tf.ConfigProto(
        gpu_options=tf.GPUOptions(
            per_process_gpu_memory_fraction=0.3
        ),
        log_device_placement=False
    )
}

box_thickness = 2
model_folder = 'models/facenet/CASIA-WebFace'

logger.info('Generating p,r,o nets')
with tf.Graph().as_default():
    sess = tf.Session(**session_opts)
    with sess.as_default():
        pnet, rnet, onet = detect_face.create_mtcnn(sess, model_folder)


def analysis(data, kwargs):
    data = cv2.resize(data, kwargs['new_shape'])
    # frame = cv2.resize(frame, (640, 360))


    detect_begin_time = time.time()
    boxes, _ = detect_face.detect_face(data, min_face_size, pnet, rnet, onet, threshold, factor)
    detect_end_time = time.time()
    for pos in boxes:
        pos = pos.astype(int)
        cv2.rectangle(data, (pos[0], pos[1]), (pos[2], pos[3]), (0, 255, 0), box_thickness)

    face_num = len(boxes) if boxes is not None else 0
    logger.info(
        "Detected %s face(s) used time: %s ms" % (
            str(face_num), str((detect_end_time - detect_begin_time) * 1000)
        )
    )

    return data
