# -*- coding: utf-8 -*-

# PyQT5 imports
# from PyQt5 import QtGui, QtCore, QtOpenGL, QtWidgets
# from ctypes import *

import configparser
from os import path, access, R_OK  # W_OK for write permission.
import abc
import six
# PyOpenGL imports
from OpenGL.GLUT import *

from utils.logger_router import LoggerRouter
from utils.singleton import Singleton

logger = LoggerRouter().getLogger(__name__)


def check_file(filename):
    # current_path = os.path.dirname(os.path.abspath(__file__))  # 当前目录
    my_path = filename
    if filename == "":
        # raise ValueError("文件名不能为空")
        return False, "文件名不能为空"
    if path.exists(my_path) and path.isfile(my_path) and access(my_path, R_OK):
        return True, my_path
        # return True
    else:
        # my_path = current_path + "/" + my_path
        if path.exists(my_path) and path.isfile(my_path) and access(my_path, R_OK):
            return True, my_path
        else:
            # raise FileNotFoundError("文件名'%s'不正确" % filename)
            return False, "文件名\"" + filename + "\"不正确"


def check_path(pathname):
    current_path = os.path.dirname(os.path.abspath(__file__))  # 当前目录
    my_path = pathname
    if pathname == "":
        return False, "文件名不能为空"

    if path.exists(my_path) and not path.isfile(my_path) and access(my_path, R_OK):
        return True, my_path
    else:
        my_path = current_path + "/" + my_path
        if path.exists(my_path) and not path.isfile(my_path) and access(my_path, R_OK):
            return True, my_path
        else:
            return False, "路径名\"%s\"不正确" % pathname


# @six.add_metaclass(abc.ABCMeta)
# class Configure(object):
#     _write_permitted = True
#
#     def __init__(self, filepath=os.path.join(sys.path[0], 'configure.ini')):
#         self.filepath = filepath
#         self.fileconf = configparser.ConfigParser()
#
#     def load(self):
#         self.fileconf.read(self.filepath)
#         # self.fileconf.
#         pass
#
#     @abc.abstractmethod
#     def save(self):
#         pass
#
#     @property
#     def write_permitted(self):
#         return self._write_permitted
#
#     @write_permitted.setter
#     def write_perimitted(self, p):
#         self._write_permitted = p
#
#     def set_property(self,k,v):
#         if self._write_permitted:
#             setattr(self,'_'+k,v)


class Configure(object):
    DEFAULT = 0
    USER = 1

    def __init__(self, mode=USER, path=''):
        self.mode = mode
        if path:
            self.path = path
        elif mode == Configure.USER:
            self.path = os.path.join(sys.path[0], 'settings.ini')
        else:
            self.path = os.path.join(sys.path[0], 'default.ini')

        self.config = configparser.ConfigParser()
        self.config.read(self.path)

    # def serialize(self, doc, section):
    #     for k, v in doc.items():
    #         self.config.set(section, k, v)

    def deserialize(self, section):

        return self.config[section]

    def __getitem__(self, section):
        return self.config[section]

    def __setitem__(self, section, doc):
        for k, v in doc.items():
            self.config.set(section, k, v)
        self.write()

    def write(self):
        if self.mode != Configure.DEFAULT:
            logger.info("Writing config data {%s}" % (str(self.config)))
            self.config.write(open(self.path, 'w', encoding='UTF8'))


class Config:
    def __init__(self):
        self.current_path = os.path.dirname(os.path.abspath(__file__))  # 当前目录
        # os.path.dirname(__file__) 返回脚本的绝对路径
        # os.path.abspath(__file__) 返回脚本的相对对路径
        self.conf = configparser.ConfigParser()
        self.Settings = dict(
            conf_file=os.path.join(self.current_path, 'cv.ini'),
            default_conf=self.conf,
            user_conf=self.conf
        )
        self.set_default()

    def set_default(self):  # 重置默认设置
        if not self.reload_user_conf():
            conf = self.Settings['default_conf']
            # conf.read(Settings['conf_file'])
            # 写入宿舍配置文件
            try:
                conf.add_section("Path")
                conf.set("Path", "video_path", self.current_path)
                conf.set("Path", "video_file_name", "")
                conf.set("Path", "img_path", self.current_path)
                conf.set("Path", "img_file_name", "")
            except configparser.DuplicateSectionError:
                logger.info("Section 'Path' already exists")
            conf.write(open(self.Settings['conf_file'], "w", encoding='UTF8'))
            self.Settings['user_conf'] = conf

    def reload_user_conf(self):  # 读取用户配置文件
        conf = self.Settings['user_conf']
        conf.read(self.Settings['conf_file'], encoding='UTF8')
        if not conf.has_section("Path"):
            return False

        user_video_path = self.get_user_conf('Path', 'video_path')
        path_ok = path.exists(user_video_path) and not path.isfile(user_video_path) and access(user_video_path, R_OK)

        if user_video_path is None or not path_ok:
            conf.set("Path", "video_path", self.current_path)

        user_img_path = self.get_user_conf('Path', 'img_path')
        path_ok = path.exists(user_img_path) and not path.isfile(user_img_path) and access(user_img_path, R_OK)
        if user_img_path is None or not path_ok:
            conf.set("Path", "img_path", self.current_path)

        conf.write(open(self.Settings['conf_file'], "w", encoding='UTF8'))

        return True

    def get_user_conf(self, section, key, default=None):  # 获取section中的key对应的value
        conf = self.Settings['user_conf']
        try:
            value = conf.get(section, key)
        except (configparser.NoSectionError, configparser.NoOptionError):
            value = default
        return value

    def set_user_conf(self, section, key, value):  # 设定section中的key对应的value
        conf = self.Settings['user_conf']
        try:
            conf.set(section, key, value)
        except configparser.DuplicateSectionError:
            logger.info("Section 'Path' already exists")
        conf.write(open(self.Settings['conf_file'], "w", encoding='UTF8'))
