# import time
#
# import cv2
#
# from face_detectors import FaceDetector
# from face_recognizers import FaceRecognitor
# from settings import DETECTOR_CONF
# from utils.logger_router import LoggerRouter
#
# logger = LoggerRouter().getLogger(__name__)
#
# # facial_area_ratio = 0.06
#
# face_detect_processor = FaceDetector.from_name(
#     **DETECTOR_CONF
# )
#
#
# face_reg = FaceRecognitor()
#
#
#
# def analysis(data, kwargs):
#     frame = data
#     # frame = cv2.resize(frame, kwargs['new_shape'])
#     # frame = cv2.resize(frame, (640, 360))
#     draw = frame
#     detect_begin_time = time.time()
#     face_boxes = face_detect_processor.get_faces_boxes(frame)
#     face_num = face_detect_processor.get_box_len(face_boxes)
#     if face_num != 0:
#         # face_chips = face_detector.get_face_chips(frame, boxes=face_boxes, do=True)
#         draw = face_detect_processor.draw_rect(frame, boxes=face_boxes)
#         chips = face_detect_processor.get_face_chips(frame, boxes=face_boxes)
#         d = face_reg.predict(draw, chips)
#
#     detect_end_time = time.time()
#     logger.info(
#         "Detected %d face(s) used time: %f ms" % (
#             face_num, (detect_end_time - detect_begin_time) * 1000
#         )
#     )
#     return draw
