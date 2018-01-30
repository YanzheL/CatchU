from threading import Event

from multiproc_model.pooling import ThreadPool
from multiproc_model.producer import Producer
from multiproc_model.worker import Worker
from settings import *
from utils.singleton import Singleton
# from settings import PRODUCER_CONF
from utils.config import Configure


# PRODUCER_CONF = Configure().deserialize('producer')


class Backend(object, metaclass=Singleton):
    def __init__(self, inque, outque, config):
        self.initializing = Event()
        self.initialized = Event()
        self._config = config
        self.inque = inque
        self.outque = outque
        self.producer = None
        self.worker = None
        self.thread_pool = None
        self._configure = None

    def initialize(self):
        if not self.initialized.is_set():
            self.initializing.set()
            self._configure = Configure()
            video_source = self._configure['producer']['datasource']
            try:
                video_source = int(video_source)
            except ValueError:
                pass
            self.worker = Worker.from_name("Video", input_queue=self.inque, output_queue=self.outque,
                                           use_multiprocess=False)
            print(self.worker)
            self.producer = Producer.from_name("Video", output_queue=self.inque,
                                               video_source=video_source)
            print(self.producer)
            self.thread_pool = ThreadPool()
            self.thread_pool.add_worker(self.worker, nworkers=self._configure['threading']['workers'])
            self.thread_pool.add_worker(self.producer, name='main_producer')

            self.initialized.set()

    def start(self):
        self.initialized.wait()
        assert self.initialized, "Backend not initialized"
        self.thread_pool.start()

    def stop(self, block=False, **kwargs):
        if self.initialized.is_set():
            self.thread_pool.stop(**kwargs)
            if block:
                self.thread_pool.wait(**kwargs)

    def wait(self, **kwargs):
        assert self.initialized, "Backend not initialized"
        self.thread_pool.wait(**kwargs)

    def is_started(self, block=False):
        return self.initialized.is_set() and self.thread_pool.started
