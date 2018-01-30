from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from utils.config import *
from utils.logger_router import LoggerRouter

logger = LoggerRouter().getLogger(__name__)
# from settings import GUI_CONF
from utils.config import Configure

GUI_CONF = Configure().deserialize('gui')
cfg = Config()
import gui.framework


class SetupPage(QDialog):
    datasource = -1
    _portrait_set = pyqtSignal(QPixmap)

    def __init__(self, config_info, main_window):
        super(SetupPage, self).__init__()
        self.main_window = main_window
        self.config_info = config_info
        self._portrait_set.connect(main_window.update_portrait)
        self.usr_conf = Configure(mode=Configure.USER)
        self.default_conf = Configure(mode=Configure.DEFAULT)

        self.hbox = QHBoxLayout(self)
        self.groupBox = QGroupBox(self)
        self.horizontalLayout = QHBoxLayout(self.groupBox)
        self.tabWidget01 = QTabWidget(self)
        self.tab_1 = QWidget()
        self.tab_2 = QWidget()
        self.videopathLineEdit = QLineEdit(self.tab_1)
        self.pushButton_openfile_video = QPushButton(self.tab_1)
        self.tabWidget02 = QTabWidget(self)
        self.tab_3 = QWidget()
        self.targetImgLineEdit = QLineEdit(self.tab_3)
        self.pushButton_openfile_image = QPushButton(self.tab_3)
        self.tabWidget03 = QTabWidget(self)
        self.tab_4 = QWidget()
        self.lineEit_3 = QLineEdit(self.tab_4)
        self.pushButton_connect_host = QPushButton(self.tab_4)
        self.label_host_connect_status = QLabel(self.tabWidget03)
        self.pushButton_config_Cancel = QPushButton(self.groupBox)
        self.pushButton_config_Ok = QPushButton(self.groupBox)

        self.init_ui()
        self.load_user_cfg()

    def init_ui(self):
        self.setWindowTitle('设置')
        self.setGeometry(100, 200, 480, 390)
        self.setMinimumSize(QtCore.QSize(480, 390))
        self.setMaximumSize(QtCore.QSize(480, 390))

        self.groupBox.setMinimumSize(QtCore.QSize(480, 390))
        self.groupBox.setMaximumSize(QtCore.QSize(480, 390))
        self.groupBox.setObjectName("groupBox")
        self.groupBox.setStyleSheet("#groupBox{background-color: #444444}")

        self.horizontalLayout.setObjectName("horizontalLayout")
        # ---------------------------------------------------------------------
        self.tabWidget01.setGeometry(QtCore.QRect(20, 30, 450, 80))
        self.tabWidget01.setMinimumSize(QtCore.QSize(450, 80))
        self.tabWidget01.setMaximumSize(QtCore.QSize(450, 80))
        self.tabWidget01.setObjectName("tabWidget01")

        self.tab_1.setObjectName("tab_1")
        self.tabWidget01.addTab(self.tab_1, "视频文件")

        self.tab_2.setObjectName("tab_2")
        self.tabWidget01.addTab(self.tab_2, "摄像机")
        self.tab_2.setGeometry(0, 0, 440, 50)

        # logger.info(self.tab_2.width(), self.tab_2.height())

        self.m_pButtonGroup = QButtonGroup(self.tab_2)

        self.videoCapture_select_01 = QRadioButton(self.tab_2)
        self.videoCapture_select_02 = QRadioButton(self.tab_2)
        self.videoCapture_select_03 = QRadioButton(self.tab_2)
        self.videoCapture_select_01.setText("摄像机[ 0 ]")
        self.videoCapture_select_02.setText("摄像机[ 1 ]")
        self.videoCapture_select_03.setText("摄像机[ 2 ]")
        self.videoCapture_select_01.setGeometry(0, 5, 90, 50)
        self.videoCapture_select_02.setGeometry(120, 5, 90, 50)
        self.videoCapture_select_03.setGeometry(240, 5, 90, 50)
        # 设置互斥
        self.m_pButtonGroup = QButtonGroup(self.tab_2)
        self.m_pButtonGroup.setExclusive(True)
        self.m_pButtonGroup.addButton(self.videoCapture_select_01)
        self.m_pButtonGroup.addButton(self.videoCapture_select_02)
        self.m_pButtonGroup.addButton(self.videoCapture_select_03)
        self.videoCapture_select_01.setChecked(True)

        self.videoCapture_select_n = QComboBox(self.tab_2)
        self.videoCapture_select_n.setGeometry(380, 15, 40, 26)

        self.m_pButtonGroup.buttonClicked.connect(self.radio_btn_onclicked)
        x2 = self.videoCapture_select_n.count()
        logger.info(x2)

        z1 = self.videoCapture_select_n.currentText()
        z2 = self.videoCapture_select_n.currentIndex()
        x4 = '%d' % 5

        logger.info(type(x4))
        logger.info(type(z1))
        # logger.info(z1, z2)
        for num in range(0, 9):
            self.videoCapture_select_n.addItem('%d' % num)

        self.videoCapture_select_n.currentIndexChanged.connect(self.comoboxItem_is_select)

        self.videopathLineEdit.setGeometry(10, 14, 350, 30)
        self.videopathLineEdit.setMinimumSize(350, 30)
        self.videopathLineEdit.setMaximumSize(350, 30)

        self.pushButton_openfile_video.setGeometry(
            QtCore.QRect(370, 14, 70, 30))
        self.pushButton_openfile_video.setObjectName("openfile_video")
        self.pushButton_openfile_video.setText("打开文件")
        self.pushButton_openfile_video.clicked.connect(self.openfile_video_dialog)
        # ---------------------------------------------------------------------
        self.tabWidget02.setGeometry(QtCore.QRect(20, 130, 450, 80))
        self.tabWidget02.setMinimumSize(QtCore.QSize(450, 80))
        self.tabWidget02.setMaximumSize(QtCore.QSize(450, 80))
        self.tabWidget02.setObjectName("tabWidget02")

        self.tab_3.setObjectName("tab_3")
        self.tabWidget02.addTab(self.tab_3, "图片文件")

        self.targetImgLineEdit.setGeometry(10, 14, 350, 30)
        self.targetImgLineEdit.setMinimumSize(350, 30)
        self.targetImgLineEdit.setMaximumSize(350, 30)

        self.pushButton_openfile_image.setGeometry(
            QtCore.QRect(370, 14, 70, 30))
        self.pushButton_openfile_image.setObjectName("openfile_image")
        self.pushButton_openfile_image.setText("打开文件")
        self.pushButton_openfile_image.clicked.connect(self.openfile_image_dialog)
        # ---------------------------------------------------------------------
        self.tabWidget03.setGeometry(QtCore.QRect(20, 230, 450, 100))
        self.tabWidget03.setMinimumSize(QtCore.QSize(450, 100))
        self.tabWidget03.setMaximumSize(QtCore.QSize(450, 100))
        self.tabWidget03.setObjectName("tabWidget03")

        self.tab_4.setObjectName("tab_4")
        self.tabWidget03.addTab(self.tab_4, "主机地址设置")

        self.lineEit_3.setGeometry(10, 14, 350, 30)
        self.lineEit_3.setMinimumSize(350, 30)
        self.lineEit_3.setMaximumSize(350, 30)

        self.pushButton_connect_host.setGeometry(QtCore.QRect(370, 14, 70, 30))
        self.pushButton_connect_host.setObjectName("openfile_image")
        self.pushButton_connect_host.setText("连接测试")
        self.pushButton_connect_host.clicked.connect(self.host_connect_test)

        self.label_host_connect_status.setGeometry(12, 65, 200, 30)
        self.label_host_connect_status.setText("主机连接状态：")
        # ---------------------------------------------------------------------

        self.pushButton_config_Cancel.setGeometry(280, 345, 70, 30)
        self.pushButton_config_Cancel.setText("取消")
        self.pushButton_config_Cancel.clicked.connect(self.btn_config_cancel)

        self.pushButton_config_Ok.setGeometry(380, 345, 70, 30)
        self.pushButton_config_Ok.setText("确定")
        self.pushButton_config_Ok.clicked.connect(self.btn_config_ok)
        # self.pushButton_config_Ok.clicked.connect(self.btn_config_cancel)
        # ---------------------------------------------------------------------

        qss = "black.qss"  # sys.path[0] 主脚本所在绝对路径

        with open(qss) as file:
            str_qss = file.readlines()
            str_qss = ''.join(str_qss).strip('\n')
        self.setStyleSheet(str_qss)

    def pop_msg(self, msg, ok_act=None, cancel_act=None):
        ok = QPushButton()
        cacel = QPushButton()

        msg = QMessageBox(QMessageBox.Warning, u"错误提示", msg)

        msg.addButton(ok, QMessageBox.ActionRole)
        msg.addButton(cacel, QMessageBox.RejectRole)
        ok.setText(u'确定')
        cacel.setText(u'取消')
        return msg.exec()
        #
        # if msg.exec_() == QMessageBox.RejectRole:
        #     pass

    def load_user_cfg(self):
        bg_img_path = os.path.join(sys.path[0], self.usr_conf['recognizer']['target_img'])
        ok, msg = check_file(bg_img_path)
        if ok:
            self.background_img = QtGui.QPixmap(bg_img_path)
            if self.background_img:
                self.background_img = self.background_img.scaled(290, 290, Qt.KeepAspectRatio)
        else:
            self.pop_msg(msg)
            self.background_img = QtGui.QPixmap(
                os.path.join(
                    sys.path[0],
                    self.default_conf['recognizer']['target_img']
                )
            ).scaled(290, 290, Qt.KeepAspectRatio)
        self._portrait_set.emit(self.background_img)
        prev_src = self.usr_conf['producer']['datasource']
        try:
            prev_src = int(prev_src)
            self.select_comboxItem(prev_src)
        except ValueError:
            self.videopathLineEdit.setText(prev_src)
        self.targetImgLineEdit.setText(bg_img_path)

    def radio_btn_onclicked(self, button):

        self.m_pButtonGroup.setExclusive(True)  # 设置互斥
        radio_btn_text = button.text()
        logger.info("radio_btn_text = " + radio_btn_text)

        if radio_btn_text == "摄像机[ 0 ]":
            self.datasource = 0

        if radio_btn_text == "摄像机[ 1 ]":
            self.datasource = 1

        if radio_btn_text == "摄像机[ 2 ]":
            self.datasource = 2

        logger.info("self.capture_number = " + str(self.datasource))
        self.videoCapture_select_n.setCurrentIndex(self.datasource)

        logger.info("self.capture_number =" + str(self.datasource))
        pass

    def comoboxItem_is_select(self):
        self.datasource = self.videoCapture_select_n.currentIndex()
        self.select_comboxItem(self.datasource)
        logger.info("摄像机改变%d" % self.datasource)

    def select_comboxItem(self, num):
        if num == -1 or num > 3:
            # self.m_pButtonGroup 怎么设所有radiobuttom状态为 未选择
            self.m_pButtonGroup.setExclusive(False)  # 取消互斥
            self.videoCapture_select_01.setChecked(False)
            self.videoCapture_select_02.setChecked(False)
            self.videoCapture_select_03.setChecked(False)
        else:
            if num == 0:
                self.videoCapture_select_01.setChecked(True)
            elif num == 1:
                self.videoCapture_select_02.setChecked(True)
            elif num == 2:
                self.videoCapture_select_03.setChecked(True)

    def openfile_video_dialog(self):
        # 打开文件路径
        # 设置文件扩展名过滤,注意用双分号间隔
        video_name, img_type = QFileDialog.getOpenFileName(self, "打开视频", "",
                                                           " *.mp4;*.avi;*.flv;*.mkv;;All Files (*)")
        if video_name:
            logger.info(video_name)
            self.videopathLineEdit.setText(video_name)
            # file = open(video_name,'r')
            # data = file.read()
            # self.textEdit.setText(data)

    def openfile_image_dialog(self):
        # 打开文件路径
        # 设置文件扩展名过滤,注意用双分号间隔
        img_name, img_type = QFileDialog.getOpenFileName(self, "打开图片", "",
                                                         " *.jpg; *.png; *.jpeg; *.bmp;;All Files (*)")
        if img_name:
            # logger.info(img_name)
            # logger.info(img_type)
            self.targetImgLineEdit.setText(img_name)
            # file = open(img_name,'r')
            # data = file.read()
            # self.textEdit.setText(data)

    def host_connect_test(self):
        logger.info("主机连接中。。。。 稍后")

    def btn_config_cancel(self):
        self.reject()  # 对话框标准退出方式(取消)
        # self.close()	#通用窗口退出方式

    def set_video_source(self, src):
        try:
            int(src)  # 如果src是个整数表示是摄像头源
        except ValueError:  # 否则是文件路径
            ok, info = check_file(src)  # check_file抛出异常会被上级接收
            if ok:
                self.usr_conf['producer']['datasource'] = src
                return True
            else:
                self.pop_msg(info)
                return False
        self.usr_conf['producer']['datasource'] = str(src)
        return True

    def set_target_img(self, src):
        ok, info = check_file(src)  # check_file抛出异常会被上级接收
        if ok:
            self.usr_conf['recognizer']['target_img'] = src
            return True
        else:
            self.pop_msg(info)
            return False

    def btn_config_ok(self):
        # TODO: 配置是否正确的检查应该和后续的提示操作分开,而不是一起放在一个btn_config_Ok()函数里。
        # TODO: 这样check()返回的布尔值才可以给别处复用。并且配置检查的结果要给一个类属性 valid_setting 赋布尔值

        # if self.datasource!=-1:
        #     self.set_video_source(self.datasource)
        # else:
        #     self.set_video_source(self.videopathLineEdit.text())
        #
        # # my_path = self.videopathLineEdit.text()
        # # logger.info("视频文件名： " + my_path)
        # # check_ok, check_info = check_file(my_path)
        # # if check_ok:
        # #     # logger.info("视频文件名正确")
        # #     self.config_info[0] = check_info
        # # else:
        # #     QMessageBox.information(
        # #         self, "Information", self.tr("视频" + check_info + "，请重新输入!"))
        # #     return
        #
        # self.set_target_img(self.targetImgLineEdit.text())


        if self.set_video_source(
                self.datasource if self.datasource != -1 else self.videopathLineEdit.text()) and self.set_target_img(
            self.targetImgLineEdit.text()):
            self.usr_conf.write()
            self.load_user_cfg()
            self.accept()
            # else:
            #     self.reject()

            # my_path = self.lineEit_2.text()
            # check_ok, check_info = check_file(my_path)
            # # logger.info("图片文件名： " + my_path)
            # if check_ok:
            #     # logger.info("图片文件名正确")
            #     self.config_info[1] = self.lineEit_2.text()
            # else:
            #     logger.info("图片找不到，请重新输入")
            #     QMessageBox.information(
            #         self, "Information", self.tr("图片" + check_info + "，请重新输入!"))
            #     return

            # 将配置信息写入配置文件
            # file_path = self.config_info[0]
            # parent_path = os.path.dirname(file_path)
            # file_name = os.path.split(file_path)[-1]
            # cfg.set_user_conf("Path", "video_path", parent_path)
            # cfg.set_user_conf("Path", "video_file_name", file_name)
            #
            # file_path = self.config_info[1]
            # parent_path = os.path.dirname(file_path)
            # file_name = os.path.split(file_path)[-1]
            # cfg.set_user_conf("Path", "img_path", parent_path)
            # cfg.set_user_conf("Path", "img_file_name", file_name)

            # 对话框标准退出方式(确认)
            # self.close() #通用窗口退出方式
