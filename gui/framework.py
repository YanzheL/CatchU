# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from backend.bootstrap import Backend
from backend.face_recognizers import FaceRecognitor
from multiproc_model.producer import *
from multiproc_model.worker import VideoWorker
from utils.config import *
from utils.logger_router import LoggerRouter

logger = LoggerRouter().getLogger(__name__)
# from settings import GUI_CONF
from utils.config import Configure
from .setup_page import SetupPage
GUI_CONF = Configure().deserialize('gui')


class GUITask(QRunnable):
    def __init__(self, target, args=()):
        super().__init__()
        self.target = target
        self.args = args

    def run(self):
        self.target(*self.args)


class GUIMain(QWidget):
    def __init__(self, inque, outque):
        super(GUIMain, self).__init__()  # TODO 常看IDE的提示哦！调用父类构造函数的时候少传了参数，虽然也能运行，但IDE提出的建议尽可能采纳一下
        self.timer_camera = QtCore.QTimer()
        self.inque = inque
        self.outque = outque
        self.backend = Backend(self.inque, self.outque, None)
        self.init_ui()
        self._slot_init()

    def _slot_init(self):
        self.startButton.clicked.connect(self._video_switch_on_click)
        self.timer_camera.timeout.connect(self._show_camera)
        self.stopButton.clicked.connect(self.close)
        if not FaceRecognitor.initializing.is_set():
            self._background_run(FaceRecognitor)

    def _background_run(self, target, args=()):
        QThreadPool.globalInstance().start(GUITask(target, args))

    def _video_switch_on_click(self):
        if not self.timer_camera.isActive():
            self.timer_camera.start(1000 // int(GUI_CONF['preferred_fps']))
            if not self.backend.initializing.is_set():
                self._background_run(self.backend.initialize)
            if not self.backend.is_started():
                self._background_run(self.backend.start)
            self.settingsButton.setDisabled(True)
            self.startButton.setText(u'暂 停')
        else:
            self._pause()
            # self.settingsButton.setDisabled(False)
            self.startButton.setText(u'继 续')

    def _pause(self):
        self.timer_camera.stop()
        self.widget_video.clear()

    def _show_camera(self):
        try:
            if not self.backend.is_started():
                return
            seq, image = self.outque.get()
            self.set_image(image)
        except BrokenPipeError as e:
            logger.error(e)
            self.timer_camera.stop()

    def closeEvent(self, event):
        ok = QtWidgets.QPushButton()
        cacel = QtWidgets.QPushButton()

        msg = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, u"关闭", u"是否关闭！")

        msg.addButton(ok, QtWidgets.QMessageBox.ActionRole)
        msg.addButton(cacel, QtWidgets.QMessageBox.RejectRole)
        ok.setText(u'确定')
        cacel.setText(u'取消')
        if msg.exec_() == QtWidgets.QMessageBox.RejectRole:
            event.ignore()
        else:
            logger.info("App closing...")
            self._pause()
            self.setVisible(False)
            if self.backend.is_started():
                self._background_run(self._clean_up)
            logger.info("Bye bye!")
            event.accept()

    def _clean_up(self):
        # self.backend.stop(block=True, cls=VideoWorker)
        # self.backend.stop(block=True, cls=VideoProducer)
        self.outque.stop()
        self.backend.wait(cls=VideoWorker)
        VideoDataSource.stopped = True
        self.backend.wait(cls=VideoProducer)

    def init_ui(self):
        self.hbox = QHBoxLayout(self)
        self.groupBox = QGroupBox(self)
        self.horizontalLayout = QHBoxLayout(self.groupBox)

        self.widget_video = QtWidgets.QLabel(self.groupBox)
        self.widget_video.setAlignment(Qt.AlignCenter)
        # self.widget_video.resize(640, 480)
        # self.widget_video.move(5,5)
        self.widget_video.show()
        #  self.widget_video =QOpenGLWidget(self.groupBox)

        self.widget_pic_btn = QWidget(self.groupBox)
        self.widget_pic = QWidget(self.widget_pic_btn)
        self.widget_btn = QWidget(self.widget_pic_btn)
        self.settingsButton = QPushButton(self.widget_btn)
        self.startButton = QPushButton(self.widget_btn)
        self.PortraitLabel = QtWidgets.QLabel(self.widget_pic)
        self.stopButton = QPushButton(self.widget_btn)
        self.splitter02 = QSplitter(Qt.Vertical)
        self.table01 = QTableWidget(20, 3)
        self.logTextEdit = QTextEdit()
        # self.logTextEdit.setDisabled(True)
        self.logTextEdit.setMinimumWidth(800)
        self.logCursor = self.logTextEdit.textCursor()
        self.logScrolled = False
        # self.logTextEdit.textChanged.connect(self.check_full_log)
        self.setWindowTitle('人员追踪')
        self.setGeometry(100, 200, 600, 800)

        # self.groupBox.setGeometry(QtCore.QRect(20, 100, 671, 378))
        self.groupBox.setMinimumSize(QtCore.QSize(0, 378))
        self.groupBox.setMaximumSize(QtCore.QSize(4000, 378))
        self.groupBox.setObjectName("groupBox")
        self.groupBox.setStyleSheet("#groupBox{background-color: #444444}")

        self.horizontalLayout.setObjectName("horizontalLayout")

        # self.widget_video.resize(350,350)
        # self.widget_video.setFixedSize(350, 350)
        # self.widget_video.setMinimumWidth(350)
        # self.widget_video.setMinimumSize(QtCore.QSize(350, 350))
        # self.widget_video.setMaximumSize(QtCore.QSize(16777215, 350))
        self.widget_video.setObjectName("widget_video")
        self.widget_video.setStyleSheet(
            "#widget_video{background-color: #666666}")
        self.horizontalLayout.addWidget(self.widget_video)

        self.widget_video.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.widget_pic_btn.setMinimumSize(QtCore.QSize(300, 350))
        self.widget_pic_btn.setMaximumSize(QtCore.QSize(300, 350))
        self.widget_pic_btn.setObjectName("widget_pic_btn")
        self.widget_pic_btn.setStyleSheet(
            "#widget_pic_btn{background-color: #444444}")

        self.widget_pic.setGeometry(QtCore.QRect(0, 0, 300, 300))
        self.widget_pic.setMinimumSize(QtCore.QSize(300, 300))
        self.widget_pic.setMaximumSize(QtCore.QSize(300, 300))
        self.widget_pic.setObjectName("widget_pic")
        self.widget_pic.setStyleSheet("#widget_pic{background-color: #666666}")

        self.widget_btn.setGeometry(QtCore.QRect(0, 300, 300, 50))
        self.widget_btn.setMinimumSize(QtCore.QSize(300, 50))
        self.widget_btn.setMaximumSize(QtCore.QSize(300, 50))
        self.widget_btn.setObjectName("widget_btn")

        self.settingsButton.setGeometry(QtCore.QRect(15, 13, 70, 30))
        self.settingsButton.setObjectName("pushButton_1")
        self.settingsButton.setText("设 置")

        self.startButton.setGeometry(QtCore.QRect(115, 13, 70, 30))
        self.startButton.setObjectName("pushButton_2")
        self.startButton.setText("开 始")

        self.stopButton.setGeometry(QtCore.QRect(215, 13, 70, 30))
        self.stopButton.setObjectName("pushButton_3")
        self.stopButton.setText("退 出")
        self.horizontalLayout.addWidget(self.widget_pic_btn)

        self.PortraitLabel.resize(290, 290)
        self.PortraitLabel.move(5, 5)

        self.defaultFacePath = os.path.join(sys.path[0], "gui/face0001.jpg")  # sys.path[0] 主脚本所在绝对路径
        # logger.info(defaultFacePath)
        self.defaultFacePixMap = QtGui.QPixmap(self.defaultFacePath)
        self.PortraitLabel.setPixmap(self.defaultFacePixMap)
        self.PortraitLabel.show()

        self.logTextEdit.setReadOnly(True)  # 设置为只读模式

        self.logTextEdit.setText("Realtime Logging Console")

        self.splitter02.addWidget(self.groupBox)
        self.splitter02.addWidget(self.logTextEdit)

        self.table01.setHorizontalHeaderLabels(["时段", "info", "传输状态"])

        # #设置表格整体字体
        # font_table = QtGui.QFont()
        # font_table.setPointSize(11)
        # table01.setFont(font_table) #设置表格整体字体
        # #设置表头字体
        # font_item = QtGui.QFont()
        # font_item.setPointSize(12)
        # table01.horizontalHeaderItem(0).setFont(font_item)
        # table01.horizontalHeaderItem(1).setFont(font_item)
        # table01.horizontalHeaderItem(2).setFont(font_item)

        self.table01.verticalHeader().setFixedWidth(30)  # 设置行表头的宽度，即水平抬头对应的宽度

        self.table01.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch)  # 自适应水平宽度，不出现水平方向滚动条
        self.table01.setColumnWidth(2, 250)
        self.table01.setEditTriggers(
            QAbstractItemView.NoEditTriggers)  # 表格禁止编辑

        # table01.horizontalHeader().setFixedWidth(25) #设置列表头的宽度，即行号对应的宽度
        # table01.horizontalHeader().setStyleSheet(
        # "QHeaderView::section{background-color:rgb(40,143,218);font:11pt '宋体';color: white;};")
        # table01.setColumnWidth(0,150)
        # table01.setColumnWidth(2,150)

        self.table01.setSelectionBehavior(
            QAbstractItemView.SelectRows)  # 设置选中整行
        self.splitter02.addWidget(self.table01)

        # 下面3句设置上下3行的高度比为3：1：2
        self.splitter02.setStretchFactor(0, 2)
        self.splitter02.setStretchFactor(2, 3)
        self.splitter02.setStretchFactor(3, 5)

        self.hbox.addWidget(self.splitter02)
        self.setLayout(self.hbox)

        qss = os.path.join(sys.path[0], "gui/black.qss")  # sys.path[0] 主脚本所在绝对路径
        with open(qss) as file:
            str = file.readlines()
            str = ''.join(str).strip('\n')
        self.setStyleSheet(str)
        self.settingsButton.clicked.connect(self.show_config_page)

    @pyqtSlot(str, name="update")
    def update_log(self, msg):
        if not self.logScrolled:
            self.logCursor.movePosition(QtGui.QTextCursor.End)
            self.logScrolled = True
        self.logTextEdit.append(msg)
        #     cursor = self.logTextEdit.textCursor()
        # # cursor.movePosition(QtGui.QTextCursor.End)
        # #     self.logCursor.insertText(msg+"\n")

        if self.logTextEdit.document().blockCount() > 200:
            # self.logCursor.movePosition(QtGui.QTextCursor.Start)
            # self.logCursor.select(QtGui.QTextCursor.LineUnderCursor)
            # self.logCursor.removeSelectedText()
            # self.logCursor.deleteChar()
            self.logTextEdit.clear()
        self.logTextEdit.ensureCursorVisible()

    @pyqtSlot(QPixmap,name="portrait")
    def update_portrait(self,pix):
        self.PortraitLabel.setPixmap(pix)

    def set_image(self, frame):
        # frame=cv2.resize(frame, (480, 320))
        height, width, bytesPerComponent = frame.shape
        bytesPerLine = bytesPerComponent * width
        # 变换彩色空间顺序
        cv2.cvtColor(frame, cv2.COLOR_BGR2RGB, frame)
        # 转为QImage对象
        image = QImage(frame.data, width, height, bytesPerLine, QImage.Format_RGB888)
        self.widget_video.setPixmap(QPixmap.fromImage(image))

    def read_user_conf(self):
        parent_path = self.cfg.get_user_conf("Path", "img_path")
        file_name = self.cfg.get_user_conf("Path", "img_file_name")
        file_path = parent_path + "/" + file_name
        check_ok, check_info = check_file(file_path)
        if check_ok:
            self.PortraitLabel.setPixmap(QtGui.QPixmap(check_info).scaled(290, 290, Qt.KeepAspectRatio))
            self.PortraitLabel.show()

    def show_config_page(self):

        cfg_info = ["", ""]
        # cfg_info=Config()
        # self.config_widegt.setModal(True)
        # self.config_widegt.show()
        config_widegt = SetupPage(cfg_info,self)  # 设置对话框
        res = config_widegt.exec_()  # 以模态窗口显示 或以上两行取代
        logger.info(res)
        # if res == QDialog.rejected() :
        # if res is False:
        #     logger.info("放弃配置信息")
        # else:
        #     logger.info("确认配置信息")
        #
        #     logger.info(cfg_info)
        #     self.PortraitLabel.setPixmap(QtGui.QPixmap(
        #         cfg_info[1]).scaled(290, 290, Qt.KeepAspectRatio))
        #     self.PortraitLabel.show()


# class SetupPage(QDialog):
#     def __init__(self, config_info):
#         super(SetupPage, self).__init__()
#         self.initUI()
#         cfg = config_info
#
#     def initUI(self):
#         hbox = QHBoxLayout(self)
#         self.setWindowTitle('设置')
#         self.setGeometry(100, 200, 480, 390)
#         self.setMinimumSize(QtCore.QSize(480, 390))
#         self.setMaximumSize(QtCore.QSize(480, 390))
#         self.groupBox = QGroupBox(self)
#         self.groupBox.setMinimumSize(QtCore.QSize(480, 390))
#         self.groupBox.setMaximumSize(QtCore.QSize(480, 390))
#         self.groupBox.setObjectName("groupBox")
#         self.groupBox.setStyleSheet("#groupBox{background-color: #444444}")
#         self.horizontalLayout = QHBoxLayout(self.groupBox)
#         self.horizontalLayout.setObjectName("horizontalLayout")
#         # ---------------------------------------------------------------------
#         self.tabWidget01 = QTabWidget(self)
#         self.tabWidget01.setGeometry(QtCore.QRect(20, 30, 450, 80))
#         self.tabWidget01.setMinimumSize(QtCore.QSize(450, 80))
#         self.tabWidget01.setMaximumSize(QtCore.QSize(450, 80))
#         self.tabWidget01.setObjectName("tabWidget01")
#
#         self.tab_1 = QWidget()
#         self.tab_1.setObjectName("tab_1")
#         self.tabWidget01.addTab(self.tab_1, "视频文件")
#         self.tab_2 = QtWidgets.QWidget()
#         self.tab_2.setObjectName("tab_2")
#         self.tabWidget01.addTab(self.tab_2, "摄像头")
#
#         self.lineEit_1 = QLineEdit(self.tab_1)
#         self.lineEit_1.setGeometry(10, 14, 350, 30)
#         self.lineEit_1.setMinimumSize(350, 30)
#         self.lineEit_1.setMaximumSize(350, 30)
#
#         self.pushButton_openfile_video = QPushButton(self.tab_1)
#         self.pushButton_openfile_video.setGeometry(
#             QtCore.QRect(370, 14, 70, 30))
#         self.pushButton_openfile_video.setObjectName("openfile_video")
#         self.pushButton_openfile_video.setText("打开文件")
#         self.pushButton_openfile_video.clicked.connect(
#             self.openfile_video_Dialog)
#         # ---------------------------------------------------------------------
#         self.tabWidget02 = QTabWidget(self)
#         self.tabWidget02.setGeometry(QtCore.QRect(20, 130, 450, 80))
#         self.tabWidget02.setMinimumSize(QtCore.QSize(450, 80))
#         self.tabWidget02.setMaximumSize(QtCore.QSize(450, 80))
#         self.tabWidget02.setObjectName("tabWidget02")
#
#         self.tab_3 = QWidget()
#         self.tab_3.setObjectName("tab_3")
#         self.tabWidget02.addTab(self.tab_3, "图片文件")
#
#         self.lineEit_2 = QLineEdit(self.tab_3)
#         self.lineEit_2.setGeometry(10, 14, 350, 30)
#         self.lineEit_2.setMinimumSize(350, 30)
#         self.lineEit_2.setMaximumSize(350, 30)
#
#         self.pushButton_openfile_image = QPushButton(self.tab_3)
#         self.pushButton_openfile_image.setGeometry(
#             QtCore.QRect(370, 14, 70, 30))
#         self.pushButton_openfile_image.setObjectName("openfile_image")
#         self.pushButton_openfile_image.setText("打开文件")
#         self.pushButton_openfile_image.clicked.connect(
#             self.openfile_image_Dialog)
#         # ---------------------------------------------------------------------
#         self.tabWidget03 = QTabWidget(self)
#         self.tabWidget03.setGeometry(QtCore.QRect(20, 230, 450, 100))
#         self.tabWidget03.setMinimumSize(QtCore.QSize(450, 100))
#         self.tabWidget03.setMaximumSize(QtCore.QSize(450, 100))
#         self.tabWidget03.setObjectName("tabWidget03")
#
#         self.tab_4 = QWidget()
#         self.tab_4.setObjectName("tab_4")
#         self.tabWidget03.addTab(self.tab_4, "主机地址设置")
#
#         self.lineEit_3 = QLineEdit(self.tab_4)
#         self.lineEit_3.setGeometry(10, 14, 350, 30)
#         self.lineEit_3.setMinimumSize(350, 30)
#         self.lineEit_3.setMaximumSize(350, 30)
#
#         self.pushButton_connect_host = QPushButton(self.tab_4)
#         self.pushButton_connect_host.setGeometry(QtCore.QRect(370, 14, 70, 30))
#         self.pushButton_connect_host.setObjectName("openfile_image")
#         self.pushButton_connect_host.setText("连接测试")
#         self.pushButton_connect_host.clicked.connect(self.host_connect_test)
#
#         self.label_host_connect_status = QLabel(self.tabWidget03)
#         self.label_host_connect_status.setGeometry(12, 65, 200, 30)
#         self.label_host_connect_status.setText("主机连接状态：")
#         # ---------------------------------------------------------------------
#         self.pushButton_config_Cancel = QPushButton(self.groupBox)
#         self.pushButton_config_Cancel.setGeometry(280, 345, 70, 30)
#         self.pushButton_config_Cancel.setText("取消")
#         self.pushButton_config_Cancel.clicked.connect(self.btn_config_Cancel)
#
#         self.pushButton_config_Ok = QPushButton(self.groupBox)
#         self.pushButton_config_Ok.setGeometry(380, 345, 70, 30)
#         self.pushButton_config_Ok.setText("确定")
#         self.pushButton_config_Ok.clicked.connect(self.btn_config_Ok)
#         # ---------------------------------------------------------------------
#
#         qss = "black.qss"  # sys.path[0] 主脚本所在绝对路径
#
#         with open(qss) as file:
#             str = file.readlines()
#             str = ''.join(str).strip('\n')
#         self.setStyleSheet(str)
#
#     def openfile_video_Dialog(self):
#         # 打开文件路径
#         # 设置文件扩展名过滤,注意用双分号间隔
#         videoName, imgType = QFileDialog.getOpenFileName(self,
#                                                          "打开视频",
#                                                          "",
#                                                          " *.mp4;*.avi;*.flv;*.mkv;;All Files (*)")
#         if videoName:
#             logger.info(videoName)
#             self.lineEit_1.setText(videoName)
#             # file = open(videoName,'r')
#             # data = file.read()
#             # self.textEdit.setText(data)
#
#     def openfile_image_Dialog(self):
#         # 打开文件路径
#         # 设置文件扩展名过滤,注意用双分号间隔
#         imgName, imgType = QFileDialog.getOpenFileName(self,
#                                                        "打开图片",
#                                                        "",
#                                                        " *.jpg;*.png;*.jpeg;*.bmp;;All Files (*)")
#         if imgName:
#             logger.info(imgName)
#             self.lineEit_2.setText(imgName)
#             # file = open(imgName,'r')
#             # data = file.read()
#             # self.textEdit.setText(data)
#
#     def host_connect_test(self):
#         logger.info("主机连接中。。。。 稍后")
#
#     def btn_config_Cancel(self):
#         self.reject()  # 对话框标准退出方式(取消)
#         # self.close()	#通用窗口退出方式
#
#     def btn_config_Ok(self):
#
#         # TODO: 配置是否正确的检查应该和后续的提示操作分开,而不是一起放在一个btn_config_Ok()函数里。这样check()返回的布尔值才可以给别处复用。并且配置检查的结果要给一个类属性 valid_setting 赋布尔值
#
#         PATH = self.lineEit_1.text()
#         logger.info("视频文件名： " + PATH)
#         if path.exists(PATH) and path.isfile(PATH) and access(PATH, R_OK):
#             logger.info("视频文件名正确")
#         else:
#             logger.info("视频文件找不到，请重新输入")
#             QMessageBox.information(
#                 self, "Information", self.tr("视频文件找不到，请重新输入!"))
#             return
#
#         PATH = self.lineEit_2.text()
#         logger.info("图片文件名： " + PATH)
#         if path.exists(PATH) and path.isfile(PATH) and access(PATH, R_OK):
#             logger.info("图片文件名正确")
#         else:
#             logger.info("图片找不到，请重新输入")
#             QMessageBox.information(
#                 self, "Information", self.tr("图片找不到，请重新输入!"))
#             return
#
#         cfg[0] = self.lineEit_1.text()
#         cfg[1] = self.lineEit_2.text()
#
#         self.accept()  # 对话框标准退出方式(确认)
#         # self.close()	#通用窗口退出方式

# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     demo = GUIMain()
#     # with open('my_black.qss') as file:
#     # 	str = file.readlines()
#     # 	str =''.join(str).strip('\n')
#     # demo.setStyleSheet(str)
#     demo.show()
#     sys.exit(app.exec_())
