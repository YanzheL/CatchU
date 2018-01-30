# -*- coding: utf-8 -*-

# PyQT5 imports
# from PyQt5 import QtGui, QtCore, QtOpenGL, QtWidgets
# from ctypes import *

# PyOpenGL imports

from queue import Queue

# from .utils.config import *
from gui.framework import *
from utils.logger_router import LoggerRouter

logger = LoggerRouter().getLogger("main")
from utils.logger_router import LogSender
# from settings import THREADING_CONF
from multiproc_model.pipeline import Pipeline
from utils.config import Configure

THREADING_CONF = Configure().deserialize('threading')


def main():
    app = QApplication(sys.argv)
    try:
        datasource_queue = Queue(int(THREADING_CONF['input_que_size']))
        data_out_queue = Pipeline(int(THREADING_CONF['output_que_size']))
        demo = GUIMain(datasource_queue, data_out_queue)
        LogSender.gui_instance = demo
        demo.show()
    except KeyboardInterrupt as e:
        pass
    except Exception as e1:
        print(e1)
    finally:
        sys.exit(app.exec_())


if __name__ == '__main__':
    main()
