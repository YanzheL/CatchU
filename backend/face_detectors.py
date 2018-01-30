# coding: utf-8
import abc
import os
import sys
import time

import cv2
import six
import tensorflow as tf

from settings import SESSION_CONF
from third_party.facenet.src.align import detect_face
from third_party.mxnet_mtcnn.mtcnn_detector import MtcnnDetector
from utils.config import Configure
from utils.logger_router import LoggerRouter
from utils.singleton import Singleton
from utils.drawer import draw_rect
logger = LoggerRouter().getLogger(__name__)


@six.add_metaclass(abc.ABCMeta)
class FaceDetector(object, metaclass=Singleton):
    @classmethod
    def from_name(cls, name, **kwargs):
        for sub_cls in cls.__subclasses__():
            if name.lower() + "facedetector" == sub_cls.__name__.lower():
                return sub_cls(**kwargs)
        raise NotImplementedError(
            "Cannot find a implemented class for face detection processor '%s'" % name
        )

    def __init__(self, model_folder='', method_name=''):
        self.model_folder = os.path.join(sys.path[0], model_folder)
        self.method_name = method_name
        self.configure = Configure()

    @abc.abstractmethod
    def get_faces_boxes(self, img, togray=False):
        raise NotImplementedError

    def get_eyes_boxes(self, img, togray=False):
        """
        get_eyes_boxes(img[,togray]) -> iterable

        :param img:     numpy formatted image
        :param togray:  bool
                        if true, then change 'img' to greyscale before detection
        :return:        eye boxes detected in 'img'
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_face_chips(self, img, togray=False, boxes=None, do=False):
        """
        get_face_chips(img[,togray][,boxes][,do]) -> iterable

        :param img:     numpy formatted image
        :param togray:  bool
                        if true, then change 'img' to greyscale before detection
        :param boxes:   return from get_faces_boxes
        :param do:      bool
                        if true, then call cv2.imshow() to display all face chips and return chips
                        else, just return
        :return:        face chips detected in 'img'
        """
        pass

    @staticmethod
    def cvt_gray(img):
        """
        cvt_gray(img) -> numpy array

        :param img:     numpy formatted image
        :return:        'img' as greyscale
        """
        return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    def draw_eye_rect(self, img, boxes=None, do=False):
        """
        draw_eye_rect(img[,boxes][,do]) -> numpy array

        :param img:         numpy formatted image
        :param boxes:       return from get_xxx_boxes
        :param do:          bool
                            if true, then call cv2.imshow() to display the return value
                            else, just return
        :return:            numpy formatted image, as final detection result with eyes boxes on it
        """
        pass

    @abc.abstractmethod
    def draw_rect(self, img, draw_eyes=True, boxes=None, do=False):
        """
        draw_rect(img[,draw_eyes][,boxes][,do]) -> numpy array

        :param img:         numpy formatted image
        :param draw_eyes:   bool
                            if true, then draw eyes boxes on return image
        :param boxes:       return from get_xxx_boxes
        :param do:          bool
                            if true, then call cv2.imshow() to display the return value
                            else, just return
        :return:            numpy formatted image, as final detection result with boxes on it
        """
        pass

    @staticmethod
    def get_box_len(boxes):
        """
        get_box_len(boxes) -> integer

        :param boxes: boxes return from get_xxx_boxes()
        :return: number of boxes

        General method for calculating number of boxes in result
        Please overload it if has other method to calculate
        """
        return len(boxes) if boxes is not None else 0


class OpenCvFaceDetector(FaceDetector):
    def __init__(self, model_folder='models/opencv/data/haarcascades/',
                 face_model='haarcascade_frontalface_default.xml', eye_model='haarcascade_eye.xml', min_face_size=48,
                 box_thickness=2):
        super(OpenCvFaceDetector, self).__init__(model_folder, 'OpenCV Haar Cascade Face Detection')
        self.face_cascade = cv2.CascadeClassifier(model_folder + face_model)
        self.eye_cascade = cv2.CascadeClassifier(model_folder + eye_model)
        self.min_face_size = (min_face_size, min_face_size)
        self.box_thickness = box_thickness
        pass

    def get_faces_boxes(self, img, togray=True):
        if togray:
            img = FaceDetector.cvt_gray(img)
        boxes = self.face_cascade.detectMultiScale(img, 1.3, 5, minSize=self.min_face_size)
        return boxes

    def get_eyes_boxes(self, img, togray=False):
        if togray:
            img = FaceDetector.cvt_gray(img)
        boxes = self.eye_cascade.detectMultiScale(img)
        return boxes

    def get_face_chips(self, img, togray=False, boxes=None, do=False):
        raise NotImplementedError
        pass

    def draw_eye_rect(self, img, boxes=None, do=False):
        if boxes is None:
            boxes = self.get_eyes_boxes(img)

        draw_rect(img, boxes, box_thickness=self.box_thickness)
        if do:
            cv2.imshow("Eye Detection", img)
        else:
            return img

    def draw_rect(self, img, draw_eyes=False, boxes=None, do=False):
        if boxes is None:
            boxes = self.get_faces_boxes(img)
        draw_rect(img,boxes,box_thickness=self.box_thickness)
        if do:
            cv2.imshow(self.method_name, img)
        else:
            return img


class MtcnnFaceNetFaceDetector(FaceDetector):
    def __init__(self, model_folder='models/facenet/CASIA-WebFace', min_face_ratio=0, min_face_size=48, threshold=None,
                 factor=0.709,
                 box_thickness=2):
        super(MtcnnFaceNetFaceDetector, self).__init__(model_folder,
                                                       'FaceNet MTCNN Face Detection Using TensorFlow With ' + model_folder.replace(
                                                           '/',
                                                           '_').capitalize())

        self.min_face_size = float(min_face_ratio) * self.configure['worker'].getint('resize_height') if float(
            min_face_ratio) else int(min_face_size)
        logger.info('Detector min_face_size = %d' % self.min_face_size)
        self.threshold = threshold if threshold else [0.6, 0.7, 0.7]
        self.factor = factor
        self.box_thickness = box_thickness
        t1 = time.time()
        logger.info('Generating MTCNN p,r,o nets...')
        with tf.Graph().as_default():
            self.sess = tf.Session(**SESSION_CONF)
            with self.sess.as_default():
                self.pnet, self.rnet, self.onet = detect_face.create_mtcnn(self.sess, self.model_folder)
        logger.info('Generated MTCNN p,r,o nets, time used = %f ms' % ((time.time() - t1) * 1000))

    def get_faces_boxes(self, img, togray=False):
        if togray:
            img = FaceDetector.cvt_gray(img)
        boxes, _ = detect_face.detect_face(img, self.min_face_size, self.pnet, self.rnet, self.onet, self.threshold,
                                           self.factor)
        return self.box_cvt(boxes)

    def get_eyes_boxes(self, img, togray=False):
        raise NotImplementedError

    def box_cvt(self, boxes):
        list_boxes = []
        for box in boxes:
            box = box.astype(int)
            list_boxes.append((box[0], box[1], box[2] - box[0], box[3] - box[1]))
        return list_boxes

    def get_face_chips(self, img, togray=False, boxes=None, do=False):
        if boxes is None:
            boxes = self.get_faces_boxes(img)
        chips = []
        for (x, y, w, h) in boxes:
            chips.append(img[y:y + h, x:x + w])
        if do:
            for chip in chips:
                cv2.imshow("Chip", chip)
        else:
            return chips

    def draw_rect(self, img, draw_eyes=True, boxes=None, do=False):
        if boxes is None:
            boxes = self.get_faces_boxes(img)
        draw = img
        # draw = img.copy()
        for (x,y,w,h) in boxes:
            cv2.rectangle(draw, (x, pos[1]), (pos[2], pos[3]), (0, 255, 0), self.box_thickness)
        if do:
            cv2.imshow(self.method_name, draw)
        else:
            return draw

    def draw_eye_rect(self, img, boxes=None, do=False):
        raise NotImplementedError


class MtcnnMxNetFaceDetector(FaceDetector):
    # _detector = None

    def __init__(self, box_thickness=2, **settings):
        super(MtcnnMxNetFaceDetector, self).__init__("", "MxNet MTCNN Face Detection")
        self.box_thickness = box_thickness
        settings['model_folder'] = 'models/mxnet'

        if 'min_face_size' in settings:
            settings['minsize'] = settings['min_face_size']
            settings.pop('min_face_size')
        self.detector = MtcnnDetector(**settings)

    def get_faces_boxes(self, img, togray=False):
        if togray:
            img = self.cvt_gray(img)
        ret = self.detector.detect_face(img)
        return ret

    def get_face_chips(self, img, togray=False, boxes=None, do=False):
        if togray:
            img = self.cvt_gray(img)

        if not boxes:
            results = self.get_faces_boxes(img, togray=False)
        else:
            results = boxes
        points = results[1]
        chips = self.detector.extract_image_chips(img, points, 256, 0.37)
        if do:
            for chip in chips:
                cv2.imshow("Chip", chip)
        return chips

    def draw_rect(self, img, draw_eyes=True, boxes=None, do=False):
        if not boxes:
            results = self.get_faces_boxes(img)
        else:
            results = boxes

        total_boxes = results[0]
        points = results[1]
        draw = img
        for b in total_boxes:
            cv2.rectangle(draw, (int(b[0]), int(b[1])), (int(b[2]), int(b[3])), (0, 255, 0), self.box_thickness)

        for p in points:
            for i in range(5):
                cv2.circle(draw, (p[i], p[i + 5]), 1, (0, 0, 255), 2)
        if do:
            cv2.imshow(self.method_name, draw)
        return draw

    @staticmethod
    def get_box_len(boxes):
        return len(boxes[0]) if boxes is not None else 0
