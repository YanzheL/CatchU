import abc

import six

from utils.counter import Counter
from utils.logger_router import LoggerRouter
from .datasource import *


@six.add_metaclass(abc.ABCMeta)
class Producer:
    global_running = True
    all_stopped = Counter('Producer')

    @classmethod
    def from_name(cls, name, **kwargs):
        for sub_cls in cls.__subclasses__():
            if name.lower() + "producer" == sub_cls.__name__.lower():
                return sub_cls(**kwargs)

    def __init__(self, output_queue, datasource):
        self.datasource = datasource
        self.output_queue = output_queue
        self.logger = LoggerRouter().getLogger(__name__)
        self.running = True

    def run(self):
        self.all_stopped.increase()
        try:
            while Producer.global_running and self.running:
                # print("PD")
                data = self.datasource.get()
                ret = self.process(data)
                self.output_queue.put(ret)
            
        except Exception as e:
            self.exception_handler(e)
        finally:
            self._stop()

    @abc.abstractmethod
    def process(self, data):
        return data

    def _stop(self):
        # if all_instance:
        #     Producer.global_running = False
        self.running = False
        self._clean_up()
        self.logger.info('Producer %s stopped' % (self.__class__.__name__))

        self.all_stopped.decrease()

    def stop(self,all_instance=True):
        self.datasource.stop()

    def exception_handler(self, exc):
        self.logger.error("Unexpected exception %s, now stopping..." % exc)

    def _clean_up(self):
        self.datasource.close()


class VideoProducer(Producer):
    sequence = 0

    def __init__(self, output_queue, video_source=0):
        super(VideoProducer, self).__init__(output_queue, VideoDataSource(video_source))

    def process(self, data):
        img = data[1]
        # cv2.resize(img, (1024, 768))
        ret = (self.sequence, img)
        self.sequence += 1
        return ret

    def exception_handler(self, exc):
        if isinstance(exc, KeyboardInterrupt):
            self.logger.info("Detected keyboard interrupt, %s is performing gracefully shut down..." % __name__)
        else:
            self.logger.error("Unexpected exception %s" % exc)