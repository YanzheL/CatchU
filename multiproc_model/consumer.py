import six
import abc

from utils.logger_router import LoggerRouter
from utils.counter import Counter


@six.add_metaclass(abc.ABCMeta)
class Consumer:
    global_running = True
    all_stopped = Counter('Consumer')

    @classmethod
    def from_name(cls, name, **kwargs):
        for sub_cls in cls.__subclasses__():
            if name.lower() + "consumer" == sub_cls.__name__.lower():
                return sub_cls(**kwargs)

    def __init__(self, input_queue):
        self.input_queue = input_queue
        self.logger = LoggerRouter().getLogger(__name__)
        self.running = True

    def run(self):
        if not self.all_stopped.finished.is_set():
            self.all_stopped.increase()
            try:
                while Consumer.global_running and self.running:
                    # print("WK")
                    in_data = self.input_queue.get()
                    ret = self.process(in_data)
                    if ret[1] is not None:
                        self.output_queue.put(ret)
            except Exception as e:
                self.exception_handler(e)
            finally:
                # pass
                self.stop()

    def stop(self, all_instance=False):
        if not self.all_stopped.finished.is_set():
            if all_instance:
                Consumer.global_running = False
            self.running = False
            self._clean_up()
            self.logger.info('Worker %s stopped' % (self.__class__.__name__))
            self.all_stopped.decrease()

    @abc.abstractmethod
    def process(self, data):
        return data

    def exception_handler(self, exc):
        self.logger.error("Unexpected exception %s, now stopping..." % exc)

    def _clean_up(self):
        pass


class GUIConsumer(Consumer):
    def __init__(self, input_queue, gui):
        super(GUIConsumer, self).__init__(input_queue)
        self.gui = gui

    def process(self, data):
        self.gui.set_image(data[1])
