from logging.handlers import *
from queue import Queue
from utils.singleton import Singleton
import sys
from PyQt5.QtCore import pyqtSignal, QObject
from PyQt5.QtWidgets import QWidget


class LoggerRouter(metaclass=Singleton):
    def __init__(self, listener_no=4):
        self.level = None
        self.formatter = None
        self.handlers = []
        self.initialize_default_config()
        self.queue = Queue(100)
        self.que_handler = self._config_handler(QueueHandler(self.queue))
        self.listeners = [QueueListener(self.queue, *self.handlers) for i in range(listener_no)]
        for ls in self.listeners:
            ls.start()

    def getLogger(self, name=None):
        return self._config_logger(logging.getLogger(name))

    def _config_handler(self, hd, fmt=None, lvl=None):
        fmt = fmt if fmt else self.formatter
        lvl = lvl if lvl else self.level
        hd.setLevel(lvl)
        hd.setFormatter(fmt)
        return hd

    def _config_logger(self, logger):
        logger.addHandler(self.que_handler)
        logger.setLevel(self.level)
        return logger

    def initialize_default_config(self):
        self.level = logging.INFO
        self.formatter = logging.Formatter('%(asctime)s %(levelname)-8s [%(name)s:%(lineno)s] %(message)s',
                                           datefmt='%Y-%m-%d %H:%M:%S')
        self.handlers = [
            # logging.NullHandler(),
            self._config_handler(
                logging.StreamHandler(sys.stdout),
            ),
            self._config_handler(LogGUIHandler())
        ]


class LogSender(QObject):
    gui_instance = None
    connected = False
    signal = pyqtSignal(str)

    def emit(self, msg):
        # pass
        if LogSender.gui_instance:
            if not LogSender.connected:
                self.signal.connect(LogSender.gui_instance.update_log)
                LogSender.connected = True
            self.signal.emit(msg)

    def close(self):
        if LogSender.connected:
            try:
                self.signal.disconnect()
            except Exception:
                pass



class LogGUIHandler(logging.Handler):
    '''
    Customized logging handler that puts logs to the GUI.
    pymongo required
    '''

    def __init__(self):
        super().__init__()
        logging.Handler.__init__(self)
        self.sender = LogSender()

    def emit(self, record):
        self.sender.emit(self.format(record))

        # if not LogGUIHandler.connected:
        #     LogGUIHandler.signal.connect(LogGUIHandler.gui_instance.update_log)
        #     LogGUIHandler.connected = True
        #
        # LogGUIHandler.signal.emit(self.format(record))

        # LogGUIHandler.gui_instance.update_log(self.format(record))
        # pass

    def close(self):
        self.sender.close()

