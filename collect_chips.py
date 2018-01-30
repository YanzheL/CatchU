# from sklearn.neighbors import KNeighborsClassifier
#
# a=KNeighborsClassifier()


import os
import time

import cv2

from backend.face_detectors import FaceDetector
from utils.config import Configure
from utils.logger_router import LoggerRouter

logger = LoggerRouter().getLogger(__name__)

DETECTOR_CONF = dict(Configure().deserialize('detector'))
fd = FaceDetector.from_name(**DETECTOR_CONF)
path = os.path.expanduser('~/premodeling/dataset/nonalign')
imgs = [os.path.join(path, i) for i in os.listdir(path)]
for i in imgs:
    frame = cv2.imread(i)
    detect_begin_time = time.time()
    cps = fd.get_face_chips(frame)
    detect_end_time = time.time()
    logger.info(
        "Detected %d face(s) used time: %f ms" % (
            len(cps), (detect_end_time - detect_begin_time) * 1000
        )
    )
    if len(cps):
        for i, cp in enumerate(cps):
            cv2.imwrite(os.path.expanduser('~/premodeling/dataset/0/other_%d.png' % i), cp)
