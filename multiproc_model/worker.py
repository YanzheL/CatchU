import abc
import time
import traceback

import cv2
import six
from backend.face_recognizers import FaceRecognitor

from backend.face_detectors import FaceDetector
from utils.config import Configure
# from settings import DETECTOR_CONF, THREADING_CONF
from utils.counter import Counter
from utils.drawer import draw_rect
from utils.logger_router import LoggerRouter
from .pooling import SingletonProcessPool

logger = LoggerRouter().getLogger(__name__)
DETECTOR_CONF = dict(Configure().deserialize('detector'))
WORKER_CONF = Configure().deserialize('worker')


@six.add_metaclass(abc.ABCMeta)
class Worker:
    global_running = True
    # global_running = Event()
    all_stopped = Counter('Worker')

    @classmethod
    def from_name(cls, name, **kwargs):
        for sub_cls in cls.__subclasses__():
            if name.lower() + "worker" == sub_cls.__name__.lower():
                return sub_cls(**kwargs)

    def __init__(self, input_queue, output_queue):
        self.input_queue = input_queue
        self.output_queue = output_queue
        self.logger = LoggerRouter().getLogger(__name__)
        self.running = True

    def run(self):
        if not self.all_stopped.finished.is_set():
            self.all_stopped.increase()
            try:
                while Worker.global_running and self.running:
                    # print("WK")
                    in_data = self.input_queue.get()
                    ret = self.process(in_data)
                    if ret[1] is not None:
                        self.output_queue.put(ret)
            except Exception as e:
                self.exception_handler(e)
            finally:
                # pass
                # print("ddddddddddddddddddddddddddddddddddddddddddd")
                # self.all_stopped.decrease()
                self._stop()

    def _stop(self):
        if not self.all_stopped.finished.is_set():
            self.running = False
            self._clean_up()
            self.logger.info('Worker %s stopped' % (self.__class__.__name__))
            self.all_stopped.decrease()

    def stop(self, all_instance=False):
        # Worker.global_running.set()
        self.output_queue.stop()

        # if not self.all_stopped.finished.is_set():
        #     if all_instance:
        #         Worker.global_running = False
        #     self.running = False
        #     self._clean_up()
        #     self.logger.info('Worker %s stopped' % (self.__class__.__name__))
        #     self.all_stopped.decrease()

    @abc.abstractmethod
    def process(self, data):
        return data

    def exception_handler(self, exc):
        self.logger.error("Unexpected exception %s, now stopping..." % exc)

    def _clean_up(self):
        pass


class VideoWorker(Worker):
    _face_detector = None
    _face_recognizer = None

    _last_boxes = None
    _last_seq = 0

    def __init__(self, input_queue, output_queue, use_multiprocess=False):
        super(VideoWorker, self).__init__(input_queue, output_queue)
        self.use_multiproc = use_multiprocess
        if self.use_multiproc:
            self.process_pool = SingletonProcessPool()
        self.face_recognizer = FaceRecognitor()
        FaceRecognitor.initialized.wait()
        self.face_detector = FaceDetector.from_name(
            **DETECTOR_CONF
        )

    @property
    def face_detector(self):
        assert self._face_detector, "face_detector not initialized"
        return self._face_detector

    @face_detector.setter
    def face_detector(self, d):
        if not self._face_detector:
            self._face_detector = d

    @property
    def face_recognizer(self):
        assert self._face_recognizer, "face_recognizer not initialized"
        return self._face_recognizer

    @face_recognizer.setter
    def face_recognizer(self, d):
        if not self._face_recognizer:
            self._face_recognizer = d

    def process(self, data):
        origin_shape = data[1].shape
        origin_shape_ratio = origin_shape[1] / origin_shape[0]
        new_height = WORKER_CONF.getint('resize_height')
        new_shape = (int(new_height * origin_shape_ratio), new_height)

        frame = data[1]
        frame = cv2.resize(frame, new_shape)
        boxes_with_param = []

        detect_begin_time = time.time()
        if data[0] % 1 == 0:
            face_boxes = self.face_detector.get_faces_boxes(frame)
            self._last_boxes = face_boxes
            chips = self.face_detector.get_face_chips(frame, boxes=face_boxes)
            predicted_cls = self.face_recognizer.predict(chips)
            for i, cls in enumerate(predicted_cls):
                color = (0, 0, 255) if cls == 1 else (0, 255, 0)
                boxes_with_param.append((face_boxes[i], color, 3))
        else:
            face_boxes = VideoWorker._last_boxes

        face_num = len(face_boxes)
        draw = frame
        if face_num != 0:
            for bp in boxes_with_param:
                draw = draw_rect(draw, *bp)

                # face_chips = face_detector.get_face_chips(frame, boxes=face_boxes, do=True)
                # draw = self.face_detector.draw_rect(frame, boxes=face_boxes)

                # if len(chips):
                #     for i, c in enumerate(chips):
                #         try:
                #             cv2.imwrite(os.path.join(sys.path[0], 'me/me_%d_%d.png' % (data[0], i)),
                #                         cv2.resize(c, (160, 160)))
                #         except Exception as e:
                #             logger.error(e)

        detect_end_time = time.time()
        if data[0] % 2 == 0:
            logger.info(
                "Detected %d face(s) used time: %f ms" % (
                    face_num, (detect_end_time - detect_begin_time) * 1000
                )
            )

        return (data[0], draw)

    def exception_handler(self, exc):
        if isinstance(exc, KeyboardInterrupt):
            self.logger.info("Detected keyboard interrupt, %s is performing gracefully shut down..." % __name__)
        elif isinstance(exc, BrokenPipeError):
            self.logger.error("Broken pipe exception %s" % exc)
        else:
            self.logger.error("Unexpected exception %s" % exc)
            traceback.print_exc()

    def _clean_up(self):
        if self.use_multiproc:
            self.process_pool.close()


class VideoRawWorker(Worker):
    def __init__(self, input_queue, output_queue, use_multiprocess=False):
        super(VideoRawWorker, self).__init__(input_queue, output_queue)
        self.use_multiproc = use_multiprocess
        if self.use_multiproc:
            self.process_pool = SingletonProcessPool()

    def process(self, data):
        return data

    def exception_handler(self, exc):
        if isinstance(exc, KeyboardInterrupt):
            self.logger.info("Detected keyboard interrupt, %s is performing gracefully shut down..." % __name__)
        else:
            self.logger.error("Unexpected exception %s" % exc)

    def _clean_up(self):
        if self.use_multiproc:
            self.process_pool.close()
