from threading import Event, Lock

from utils.logger_router import LoggerRouter

logger = LoggerRouter().getLogger(__name__)


class Counter(object):
    def __init__(self, name=''):
        self._cv = Lock()
        self.finished = Event()
        self._count = 0
        self.name = name

    def increase(self):
        with self._cv:
            # if not self.finished.is_set():
            self._count += 1
            logger.info("Started thread %s-%d\n" % (self.name, self._count))

    def decrease(self):
        with self._cv:
            # if not self.finished.is_set():
            self._count -= 1
            logger.info("Stopped thread %s-%d\n" % (self.name, self._count))
            if self._count == 0:
                logger.info("Now all instances of '%s' stopped " % self.name)
                self.finished.set()

    def wait(self):
        self.finished.wait()
