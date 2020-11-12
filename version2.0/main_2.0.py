import sys
from PyQt5.QtWidgets import QApplication, QWidget, QTableWidget, QHeaderView, QTableWidgetItem, QVBoxLayout, \
    QHBoxLayout, QPushButton, QDesktopWidget, QLabel, QLineEdit, QAbstractItemView, \
    QItemDelegate, QAction, QFontDialog, QMessageBox
from PyQt5.QtGui import QIcon, QBrush, QColor
from PyQt5 import QtGui
from PyQt5.QtCore import pyqtSlot, Qt
import pymongo
import json
import copy
from time import strftime, localtime
import re
import collections
from data_check import data_check
import time


class App_login(QWidget):

    def __init__(self, job_num, mongodb_ip, port, mongodb_name,
                 col_base_info_temp1,
                 col_base_info_temp2,
                 col_base_info_final,
                 col_rel_info_temp1,
                 col_rel_info_temp2,
                 col_rel_info_final,
                 col_event_info_temp1,
                 col_event_info_temp2,
                 col_event_info_final,
                 check_status,
                 mongodb_name_logs,
                 col_logs):  # 登陆页
        """
        :param job_num : 工号
        :param mongodb_ip: 服务器ip
        :param port: 端口号
        :param mongodb_name: 数据库名
        :param col_base_info_temp1: base_info校对前集合名
        :param col_base_info_temp2: base_info校对后集合名
        :param col_base_info_final: base_info最终集合名
        :param col_rel_info_temp1: rel_info校对前集合名
        :param col_rel_info_temp2: rel_info校对后集合名
        :param col_rel_info_final: rel_info最终集合名
        :param col_event_info_temp1: event_info校对前集合名
        :param col_event_info_temp2: event_info校对后集合名
        :param col_event_info_final: event_info最终集合名
        :param check_status: 校验状态   0:未校对   1:已校对
        :param mongodb_name_logs: 存储（修改记录的）日志数据库名
        :param col_logs: （修改记录的）日志集合名
        """
        super().__init__()
        self.title = '基本信息校对助手'
        self.left = 10
        self.top = 10
        self.width = 600
        self.height = 110

        self.job_num = job_num
        self.mongodb_ip = mongodb_ip
        self.port = port
        self.mongodb_name = mongodb_name
        self.col_base_info_temp1 = col_base_info_temp1  # 校对前
        self.col_temp2 = col_base_info_temp2  # 校对后
        self.col_final = col_base_info_final  # 最终库
        self.mongodb_name_logs = mongodb_name_logs
        self.col_logs = col_logs
        self.check_status = check_status

        self.init_UI_login()

    def center(self, ):
        fg = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        fg.moveCenter(cp)
        # self.move(fg.topLeft())
        self.move(630, 300)
        pass

    def init_UI_login(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        # 居中窗口
        self.center()
        # qr = self.frameGeometry()
        # cp = QDesktopWidget().availableGeometry().center()
        # qr.moveCenter(cp)
        # self.move(qr.topLeft())

        self.job_num_layout = QHBoxLayout()  # 水平
        self.job_num_label = QLabel('工号:', self)
        self.job_num_text = QLineEdit(self)
        self.job_num_text.setPlaceholderText("例如： AI-1011")
        self.job_num_layout.addWidget(self.job_num_label)
        self.job_num_layout.addWidget(self.job_num_text)
        self.job_num_layout.setSpacing(10)  # 设置控件间距

        self.server_ip_layout = QHBoxLayout()  # 水平
        self.db_server_ip_label = QLabel('数据库地址:', self)
        self.db_server_ip_text = QLineEdit(self)
        self.db_server_ip_text.setText(self.mongodb_ip)
        # self.db_server_ip_text.setPlaceholderText("例如： 192.168.1.23")  # 设置隐藏文字
        self.server_ip_layout.addWidget(self.db_server_ip_label)
        self.server_ip_layout.addWidget(self.db_server_ip_text)
        self.server_ip_layout.setSpacing(10)  # 设置控件间距

        self.server_port_layout = QHBoxLayout()  # 水平
        self.db_server_port_label = QLabel('端口号:', self)
        self.db_server_port_text = QLineEdit(self)
        self.db_server_port_text.setText(self.port)  # 默认端口
        # self.server_port_layout.addWidget(self.db_server_port_label)
        # self.server_port_layout.addWidget(self.db_server_port_text)
        # self.server_port_layout.setSpacing(18)  # 设置控件间距

        self.server_ip_layout.addWidget(self.db_server_port_label)  # IP和PORT 放在一行
        self.server_ip_layout.addWidget(self.db_server_port_text)

        self.database_name_layout = QHBoxLayout()  # 水平
        self.db_database_name_label = QLabel('数据库名:', self)
        self.db_database_name_text = QLineEdit(self)
        self.db_database_name_text.setText(self.mongodb_name)
        self.database_name_layout.addWidget(self.db_database_name_label)
        self.database_name_layout.addWidget(self.db_database_name_text)
        self.database_name_layout.setSpacing(10)  # 设置控件间距

        self.col_name_b_layout = QHBoxLayout()  # 水平
        self.db_col_name_label_b = QLabel('校对前集合名:', self)
        self.db_col_name_text_b = QLineEdit(self)
        self.db_col_name_text_b.setText(self.col_base_info_temp1)
        self.col_name_b_layout.addWidget(self.db_col_name_label_b)
        self.col_name_b_layout.addWidget(self.db_col_name_text_b)
        self.col_name_b_layout.setSpacing(10)  # 设置控件间距

        self.col_name_a_layout = QHBoxLayout()  # 水平
        self.db_col_name_label_a = QLabel('校对后集合名:', self)
        self.db_col_name_text_a = QLineEdit(self)
        self.db_col_name_text_a.setText(self.col_temp2)
        self.col_name_a_layout.addWidget(self.db_col_name_label_a)
        self.col_name_a_layout.addWidget(self.db_col_name_text_a)
        self.col_name_a_layout.setSpacing(19)  # 设置控件间距

        # self.check_status_layout = QHBoxLayout()  # 水平
        # self.check_status_label = QLabel('校对前状态值:', self)
        # self.check_status_text = QLineEdit(self)
        # self.check_status_text.setToolTip("0：未校对\n1：已校对\n输入慎重！不明白请问管理员")
        # self.check_status_text.setText(self.db_col_name_after)  # 设置初始值
        # self.check_status_text.setPlaceholderText(self.check_status)  # 设置隐藏文字
        # self.check_status_layout.addWidget(self.check_status_label)
        # self.check_status_layout.addWidget(self.check_status_text)
        # self.check_status_layout.setSpacing(19)  # 设置控件间距

        self.db_name_logs_layout = QHBoxLayout()  # 水平
        self.db_name_logs_label = QLabel('存储修改记录-数据库名:', self)
        self.db_name_logs_text = QLineEdit(self)
        self.db_name_logs_text.setText(self.mongodb_name_logs)
        self.db_name_logs_layout.addWidget(self.db_name_logs_label)
        self.db_name_logs_layout.addWidget(self.db_name_logs_text)
        self.db_name_logs_layout.setSpacing(19)  # 设置控件间距

        self.col_logs_layout = QHBoxLayout()  # 水平
        self.col_logs_label = QLabel('存储修改记录-集合名:', self)
        self.col_logs_text = QLineEdit(self)
        self.col_logs_text.setText(self.col_logs)
        self.col_logs_layout.addWidget(self.col_logs_label)
        self.col_logs_layout.addWidget(self.col_logs_text)
        self.col_logs_layout.setSpacing(19)  # 设置控件间距


        self.button_zh2en = QPushButton('中文/English', self)
        self.button_zh2en.setFixedSize(80, 30)
        self.button_zh2en.clicked.connect(self.button_zh2en_on_click)

        self.button_test = QPushButton('测试', self)
        self.button_test.setFixedSize(70, 30)
        self.button_test.clicked.connect(self.button_test_on_click)

        self.button_login = QPushButton('登陆', self)
        self.button_login.setShortcut('Return')   # Enter 快捷登陆
        self.button_login.setFixedSize(70, 30)
        self.button_login.clicked.connect(self.button_login_on_click)

        self.bottom_layout = QHBoxLayout()  # 水平
        self.bottom_layout.addWidget(self.button_zh2en)
        self.bottom_layout.addWidget(self.button_test)
        self.bottom_layout.addWidget(self.button_login)

        self.main_layout_login = QVBoxLayout()  # 垂直
        self.main_layout_login.addLayout(self.job_num_layout)
        # self.main_layout_login.addLayout(self.check_status_layout)
        self.main_layout_login.addLayout(self.server_ip_layout)
        # self.main_layout_login.addLayout(self.server_port_layout)
        self.main_layout_login.addLayout(self.database_name_layout)
        self.main_layout_login.addLayout(self.col_name_b_layout)
        self.main_layout_login.addLayout(self.col_name_a_layout)
        self.main_layout_login.addLayout(self.db_name_logs_layout)
        self.main_layout_login.addLayout(self.col_logs_layout)
        self.main_layout_login.addLayout(self.bottom_layout)
        self.setLayout(self.main_layout_login)
        self.show()

    @pyqtSlot()
    def button_zh2en_on_click(self):
        print("中文/English 按钮被点击")
        if self.job_num_label.text() == "工号:":
            self.job_num_label.setText("Job_ID:")
            self.job_num_text.setPlaceholderText("examples： AI-1011")
            self.db_server_ip_label.setText("MongoDB_IP:")
            self.db_server_port_label.setText("Port:")
            self.db_database_name_label.setText("DataBase_Name:")
            self.db_col_name_label_b.setText("Col_Name_Before:")
            self.db_col_name_label_a.setText("Col_Name_After:")
            self.check_status_label.setText("Check_Status:")
            self.db_name_logs_label.setText("DataBase_Name_Logs:")
            self.col_logs_label.setText("Col_Logs:")
            self.button_test.setText("Test")
            self.button_login.setText("Login")
        else:
            self.job_num_label.setText("工号:")
            self.job_num_text.setPlaceholderText("例如： AI-1011")
            self.db_server_ip_label.setText("数据库地址:")
            self.db_server_port_label.setText("端口号:")
            self.db_database_name_label.setText("数据库名:")
            self.db_col_name_label_b.setText("校对前集合名:")
            self.db_col_name_label_a.setText("校对后集合名:")
            self.check_status_label.setText("校对前状态值:")
            self.db_name_logs_label.setText("存储修改记录-数据库名:")
            self.col_logs_label.setText("存储修改记录-集合名:")
            self.button_test.setText("测试")
            self.button_login.setText("登录")

    @pyqtSlot()
    def button_test_on_click(self):
        print("测试 按钮被点击")
        connect_result = self.test_mongodb_connect(self.db_server_ip_text.text(), self.db_server_port_text.text())
        if connect_result:
            print("连接成功！")
            reply_succeeded = QMessageBox.question(self, 'Tips', "连接成功！可以登录\n"
                                                                 "Enjoy your work!",
                                                         QMessageBox.Ok)
        else:
            print("连接失败！请重试")
            reply_error = QMessageBox.question(self, 'Tips', "连接失败！\n请检查IP地址和端口号，重新尝试！",
                                                     QMessageBox.Ok)


    @pyqtSlot()
    def button_login_on_click(self):

        print("登录 按钮被点击")
        self.job_num = self.job_num_text.text()
        if not self.job_num:
            reply1 = QMessageBox.question(self, 'Warning', "工号不能为空！请输入",
                                                QMessageBox.Ok)

        self.mongodb_ip = self.db_server_ip_text.text()
        if not self.mongodb_ip:
            reply2 = QMessageBox.question(self, 'Warning', "Mongo数据库IP不能为空！请输入",
                                          QMessageBox.Ok)

        self.port = self.db_server_port_text.text()
        if not self.port:
            reply3 = QMessageBox.question(self, 'Warning', "端口号(PORT)不能为空！请输入",
                                          QMessageBox.Ok)

        self.mongodb_name = self.db_database_name_text.text()
        if not self.mongodb_name:
            reply4 = QMessageBox.question(self, 'Warning', "数据库名(DB_Name)不能为空！请输入",
                                          QMessageBox.Ok)

        self.col_base_info_temp1 = self.db_col_name_text_b.text()
        if not self.col_base_info_temp1:
            reply5 = QMessageBox.question(self, 'Warning', "校对前集合名(Col_Name_Before)不能为空！请输入",
                                          QMessageBox.Ok)

        self.col_temp2 = self.db_col_name_text_a.text()
        if not self.col_temp2:
            reply6 = QMessageBox.question(self, 'Warning', "校对后集合名(Col_Name_After)不能为空！请输入",
                                          QMessageBox.Ok)

        # self.check_status = self.check_status_text.text()
        # if not self.check_status:
        #     reply7 = QMessageBox.question(self, 'Warning', "校对前状态值(Check_Status)不能为空！请输入\n"
        #                                                    "0：未校对\n1：已校对\n输入慎重！不明白请问管理员",
        #                                   QMessageBox.Ok)
        """
            登陆前，强制做连通测试
        """
        connect_result = self.test_mongodb_connect(self.db_server_ip_text.text(), self.db_server_port_text.text())
        if connect_result:
            print("连接成功！ 进入主界面...")
            if self.job_num and self.mongodb_ip and self.port and self.mongodb_name and self.col_base_info_temp1 \
                    and self.col_temp2 and self.check_status:

                """
                    给下一个页面传参
                """
                main_app.job_num_ = self.job_num
                main_app.mongodb_ip_ = self.mongodb_ip
                main_app.port_ = self.port
                main_app.mongodb_name_ = self.mongodb_name
                main_app.col_base_info_temp1_ = self.col_base_info_temp1
                main_app.col_temp2_ = self.col_temp2
                main_app.col_final_ = self.col_final
                main_app.mongodb_name_logs_ = self.mongodb_name_logs
                main_app.col_logs_ = self.col_logs
                main_app.check_status_ = self.check_status

                # main_app.connect_db()  # 连接数据库
                main_app.show()  # 显示主窗口

                self.close()  # 关闭登录窗口

        else:
            print("连接失败！请重试")
            reply_error = QMessageBox.question(self, 'Tips', "连接失败！\n请检查IP地址和端口号，重新尝试！",
                                               QMessageBox.Ok)

    def test_mongodb_connect(self, ip, port):
        """
            测试mongodb服务是否开启
        :return:
        """
        # epoch time before API call
        start = time.time()

        try:

            # attempt to create a client instance of PyMongo driver

            client = pymongo.MongoClient(host=[ip + ":" + port], serverSelectionTimeoutMS=2000)

            # call the server_info() to verify that client instance is valid

            server_info = client.server_info()  # will throw an exception
            # print(json.dumps(server_info, ensure_ascii=False, indent=2))
            print("connection succeeded！ elapsed： " + str(time.time() - start))
            return True

        except:

            print("")
            print("connection error! elapsed： " + str(time.time() - start))
            return False

        # print the time that has elapsed



class EmptyDelegate(QItemDelegate):
    def __init__(self, parent):
        super(EmptyDelegate, self).__init__(parent)

    def createEditor(self, QWidget, QStyleOptionViewItem, QModelIndex):
        return None


class App(QWidget):  # 继承自 QWidget类
    def __init__(self, job_num, mongodb_ip, port, mongodb_name,
                 col_base_info_temp1,
                 col_base_info_temp2,
                 col_base_info_final,
                 col_rel_info_temp1,
                 col_rel_info_temp2,
                 col_rel_info_final,
                 col_event_info_temp1,
                 col_event_info_temp2,
                 col_event_info_final,
                 check_status,
                 mongodb_name_logs,
                 col_logs):
        """
        :param job_num : 工号
        :param mongodb_ip: 服务器ip
        :param port: 端口号
        :param mongodb_name: 数据库名
        :param col_base_info_temp1: base_info校对前集合名
        :param col_base_info_temp2: base_info校对后集合名
        :param col_base_info_final: base_info最终集合名
        :param col_rel_info_temp1: rel_info校对前集合名
        :param col_rel_info_temp2: rel_info校对后集合名
        :param col_rel_info_final: rel_info最终集合名
        :param col_event_info_temp1: event_info校对前集合名
        :param col_event_info_temp2: event_info校对后集合名
        :param col_event_info_final: event_info最终集合名
        :param check_status: 校验状态
        :param mongodb_name_logs: 存储（修改记录的）日志数据库名
        :param col_logs: （修改记录的）日志集合名
        """
        super().__init__()
        self.title = '基本信息校对助手'
        desktop = QApplication.desktop()
        print("屏幕宽:" + str(desktop.width()))
        print("屏幕高:" + str(desktop.height()))
        self.left = 0
        self.top = 0
        self.width = desktop.width()
        self.height = desktop.height()
        self.index = 0
        self.init_flag = False
        self.page_up_flag = False  # 标记是否点击的上一页
        self.FLAG_ALL_RIGHT = False  # 数据格式、内容错误标记
        self.FLAG_Current_Table = "base_info"  # 基本信息/关系/生平 3表切换标记
        self.find_one_base_info_in_temp1 = {}
        self.find_one_rel_info_in_temp1 = {}
        self.person_id = ""
        self.person_id_prcessed_list = []  # 用于存储col_base_info_temp1中已经校对完的person_id
        self.person_id_prcessed_current_list = []  # 仅用于存储当次程序运行中校对完的person_id
        # self.my_order_dict = collections.OrderedDict()
        self.my_order_dict = {}
        self.title_length = 28
        self.check_after_result_dict = {}

        """
            初始化配置信息
        """
        self.job_num_ = job_num
        self.mongodb_ip_ = mongodb_ip
        self.port_ = port
        self.mongodb_name_ = mongodb_name
        self.col_base_info_temp1_ = col_base_info_temp1
        self.col_base_info_temp2_ = col_base_info_temp2
        self.col_base_final_ = col_base_info_final

        self.col_rel_info_temp1_ = col_rel_info_temp1
        self.col_rel_info_temp2_ = col_rel_info_temp2
        self.col_rel_final_ = col_rel_info_final

        self.col_event_info_temp1_ = col_event_info_temp1
        self.col_event_info_temp2_ = col_event_info_temp2
        self.col_event_final_ = col_event_info_final

        self.check_status_ = check_status
        self.mongodb_name_logs_ = mongodb_name_logs
        self.col_logs_ = col_logs

        self.client = pymongo.MongoClient([self.mongodb_ip_ + ":" + self.port_])
        """
            查询和存储基本信息表
        """
        self.information_ancient_base_temp1 = self.client[self.mongodb_name_][self.col_base_info_temp1_]
        self.information_ancient_base_temp2 = self.client[self.mongodb_name_][self.col_base_info_temp2_]
        self.information_ancient_base_log = self.client[self.mongodb_name_logs_][self.col_logs_]

        """
            查询和存储关系信息表
        """
        self.information_ancient_relation_temp1 = self.client[self.mongodb_name_][self.col_rel_info_temp1_]
        self.information_ancient_relation_temp2 = self.client[self.mongodb_name_][self.col_rel_info_temp2_]
        self.information_ancient_relation_log = self.client[self.mongodb_name_logs_][]

        """
            查询和存储生平信息表
        """
        self.information_ancient_event_temp1 = self.client[self.mongodb_name_][self.col_event_info_temp1_]
        self.information_ancient_event_temp2 = self.client[self.mongodb_name_][self.col_event_info_temp2_]
        self.information_ancient_event_log = self.client[self.mongodb_name_logs_][]
        """
            初始化数据库
        """
        self.initUI_main()

    def center(self, ):
        fg = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        fg.moveCenter(cp)
        self.move(fg.topLeft())
        pass

    def initUI_main(self):
        # 在此处添加 窗口控件
        # self.setWindowTitle('添加关闭按钮')
        # self.setFont(QFont('微软雅黑', 20))
        # self.resize(400, 300)
        # self.setWindowIcon(QIcon('1.png'))

        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        # 居中窗口
        # qr = self.frameGeometry()
        # cp = QDesktopWidget().availableGeometry().center()
        # qr.moveCenter(cp)
        # self.move(qr.topLeft())
        self.center()

        self.query_base_info()
        self.create_base_info_table(self.find_one_base_info_in_temp1)

        # Add box layout, add table to box layout and add box layout to widget
        self.table_layout = QVBoxLayout()
        self.table_layout.addWidget(self.table)

        self.button_layout = QHBoxLayout()

        """
            切换为 基本信息/关系/生平 按钮
        """
        self.trans_tables_button = QPushButton('基本信息/关系/生平', self)
        self.trans_tables_button.setToolTip("点击切换")
        self.trans_tables_button.setFixedSize(150, 30)
        self.trans_tables_button.clicked.connect(self.trans_tables_button_on_click)
        self.button_layout.addWidget(self.trans_tables_button)

        self.button1 = QPushButton('上一页', self)
        self.button1.setFixedSize(90, 30)
        self.button1.clicked.connect(self.button1_on_click)
        self.button_layout.addWidget(self.button1)
        self.button1.setEnabled(False)

        self.button2 = QPushButton('下一页', self)
        self.button2.setToolTip("点击后，自动保存当前数据")
        self.button2.setFixedSize(90, 30)
        self.button_layout.addWidget(self.button2)
        self.button2.clicked.connect(self.button2_on_click)

        """
            自定义人物检索按钮
        """
        self.ser_person_info_button = QPushButton('人物检索', self)
        self.ser_person_info_button.setToolTip("根据检索条件，查找人物信息")
        self.ser_person_info_button.setFixedSize(90, 30)
        self.ser_person_info_button.clicked.connect(self.ser_person_info_button_on_click)
        self.button_layout.addWidget(self.ser_person_info_button)

        self.button3 = QPushButton('退出', self)
        self.button3.setFixedSize(70, 30)
        self.button_layout.addWidget(self.button3)
        self.button3.clicked.connect(self.button3_on_click)

        # self.exitButton = QAction(QIcon('exit24.png'), 'Exit', self)
        # self.exitButton.setShortcut('Ctrl+Q')
        # self.exitButton.setStatusTip('Exit application')
        # self.exitButton.triggered.connect(self.close)

        self.main_layout = QVBoxLayout()
        self.main_layout.addLayout(self.table_layout)
        self.main_layout.addLayout(self.button_layout)
        self.setLayout(self.main_layout)
        # self.show()
        self.init_flag = True

    def query_base_info(self):
        self.find_one_base_info_in_temp1 = \
            self.information_ancient_base_temp1.find_one({"check_status": self.check_status_},
                                                         {"_id": 0, "check_author": 0})
        if self.find_one_base_info_in_temp1:
            self.person_id = self.find_one_base_info_in_temp1["person_id"]
            self.information_ancient_base_temp1.update_one({"person_id": self.person_id}, {"$set": {"check_status": "-1"}})
            print("初版库（AI）####" + self.col_base_info_temp1_ + "####person_id: " + self.person_id + " "
                  + '\"' + "check_status" + '\"' + "更新为: -1")
        else:
            print("Congratulations! 初版库（AI）####" + self.col_base_info_temp1_ + "#######数据校对完毕。您辛苦了！")
            buttonReply = QMessageBox.question(self, 'Congratulations', "数据校对完毕。您辛苦了！\n请退出",
                                               QMessageBox.Ok)

            if buttonReply == QMessageBox.Ok:
                print("数据校对完毕，已退出。")
                # self.close()
                sys.exit()

    def query_rel_info(self):
        self.find_one_rel_info_in_temp1 = \
            self.information_ancient_base_temp1.find_one({"check_status": self.check_status_},
                                                         {"_id": 0, "check_author": 0})
        if self.find_one_rel_info_in_temp1:
            self.person_id = self.find_one_rel_info_in_temp1["person_id"]
            self.information_ancient_base_temp1.update_one({"person_id": self.person_id}, {"$set": {"check_status": "-1"}})
            print("初版库（AI）####" + self.col_base_info_temp1_ + "####person_id: " + self.person_id + " "
                  + '\"' + "check_status" + '\"' + "更新为: -1")
        else:
            print("Congratulations! 初版库（AI）####" + self.col_base_info_temp1_ + "#######数据校对完毕。您辛苦了！")
            buttonReply = QMessageBox.question(self, 'Congratulations', "数据校对完毕。您辛苦了！\n请退出",
                                               QMessageBox.Ok)

            if buttonReply == QMessageBox.Ok:
                print("数据校对完毕，已退出。")
                # self.close()
                sys.exit()

    def cell_no_edit(self):
        self.table.item(0, 1).setFlags(self.table.item(0, 1).flags() ^ Qt.ItemIsEditable)  # 设置person_id 对应的值不可被编辑
        self.table.item(0, 1).setBackground(QtGui.QColor(220, 220, 220))  # 设置person_id 对应的值的底色
        check_status_row = self.title_length - 1
        self.table.item(check_status_row, 1).setFlags(
            self.table.item(check_status_row, 1).flags() ^ Qt.ItemIsEditable)  # 设置person_id 对应的值不可被编辑
        self.table.item(self.title_length - 1, 1).setBackground(QtGui.QColor(220, 220, 220))  # 设置check_status 对应的值的底色

    def create_base_info_table(self, data):
        """
            创建基本信息表格
        :param data:
        :return:
        """
        # Create table
        self.table = QTableWidget()
        self.table.setRowCount(self.title_length)
        self.table.setColumnCount(2)
        # Todo 优化1 设置垂直方向的表头标签
        self.table.setVerticalHeaderLabels(['人物id', '姓名', '姓', '名', '性别', '民族', '字', '号', '别称', '年龄',
                                            '籍贯', '国家', '所处时代', '出生时间', '去世时间', '去世地点', '去世原因',
                                            '外貌特征', '性格特点', '偏好', '职业', '成就', '简介', '权重id', '类别id',
                                            '同等姓名指代', '籍贯经纬度', '校验状态'])
        # TODO 优化 6 表格头的显示与隐藏
        # self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setVisible(False)

        self.table.setItemDelegateForColumn(0, EmptyDelegate(self))   # 设置第一列不可编辑
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)  # 单元格长度随内容变化
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)  # 第一列填充至满屏
        # self.table.horizontalHeader().setSectionResizeMode(1, )
        self.table.verticalHeader().setSectionResizeMode(22, QHeaderView.Stretch)  # 单元格伸展

        count_row = 0
        for k, v in data.items():
            self.table.setItem(count_row, 0, QTableWidgetItem(str(k)))
            # self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)  # 禁止编辑
            self.table.setItem(count_row, 1, QTableWidgetItem(str(v)))
            count_row += 1
        # 禁止全局编辑
        # self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.cell_no_edit()

    def create_rel_info_table(self, data):
        """
            创建关系表格
        :param data:
        :return:
        """
        # Create table
        self.rel_table = QTableWidget()
        self.rel_table.setRowCount(len(data) + 1)   # 行自增
        self.rel_table.setColumnCount(9)
        # Todo 优化1 设置水平方向的表头标签
        self.rel_table.setHorizontalHeaderLabels(['人物1id', '人物1姓名', '关系id', '关系名称', '人物2id', '人物2姓名',
                                                 '关系类别id', '关系方向id', '校验状态'])
        # TODO 优化 6 表格头的显示与隐藏
        # self.table.verticalHeader().setVisible(False)
        self.rel_table.horizontalHeader().setVisible(True)

        self.rel_table.setItemDelegateForColumn(0, EmptyDelegate(self))   # 设置第一列不可编辑
        self.rel_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # 所有列自动填充满屏

        count_col = 0
        for k, v in data.items():
            self.rel_table.setItem(0, count_col, QTableWidgetItem(str(k)))
            # self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)  # 禁止编辑
            self.rel_table.setItem(1, count_col, QTableWidgetItem(str(v)))
            count_col += 1
        # 禁止全局编辑
        # self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        # self.cell_no_edit()

    def create_life_event_info_table(self, data):
        """
            创建生平表格
        :param data:
        :return:
        """
        # Create table
        self.life_event_table = QTableWidget()
        self.life_event_table.setRowCount(len(data) + 1)    # 行自增
        self.life_event_table.setColumnCount(12)
        # Todo 优化1 设置水平方向的表头标签
        self.life_event_table.setHorizontalHeaderLabels(['事件id', '人物id', '事件顺序', '姓名',
                                                         '时间', '地点', '摘要', '内容', '事件权重',
                                                         '经纬度', '国家', '校验状态'])
        # TODO 优化 6 表格头的显示与隐藏
        # self.table.verticalHeader().setVisible(False)
        self.life_event_table.horizontalHeader().setVisible(True)

        self.life_event_table.setItemDelegateForColumn(0, EmptyDelegate(self))   # 设置第一列不可编辑
        self.life_event_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # 所有列自动填充满屏

        count_col = 0
        for k, v in data.items():
            self.life_event_table.setItem(0, count_col, QTableWidgetItem(str(k)))
            # self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)  # 禁止编辑
            self.life_event_table.setItem(1, count_col, QTableWidgetItem(str(v)))
            count_col += 1
        # 禁止全局编辑
        # self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        # self.cell_no_edit()

    @pyqtSlot()
    def trans_tables_button_on_click(self):
        """
            点击切换为关系表
        :return:
        """
        if self.FLAG_Current_Table == "base_info":
            current_person_id = self.table.item(0, 1).text()
            print("current_person_id: " + str(current_person_id))
            print('\"' + "trans_tables_button" + '\"' + "按钮被点击")
            print("当前表：" + self.FLAG_Current_Table)
            temp = {"person_1_id": "32714701100435",
                    "person_1_name": "朱熹",
                    "rel_id": "134",
                    "rel_name": "同年",
                    "person_2_id": "20000000000001",
                    "person_2_name": "吴彦夔",
                    "rel_category_id": "3",
                    "rel_direction": "3",
                    "check_status": "-1"}
            self.create_rel_info_table(temp)
            """
                此处self.table_layout.replaceWidget替换为关系表
            """
            self.table_layout.replaceWidget(self.table, self.rel_table)
            self.FLAG_Current_Table = "relation"
            print("切换为表：" + self.FLAG_Current_Table)

        elif self.FLAG_Current_Table == "relation":
            print('\"' + "trans_tables_button" + '\"' + "按钮被点击")
            print("当前表：" + self.FLAG_Current_Table)
            """
                此处self.table_layout.replaceWidget替换为生平表
            """
            temp_life_e = {"event_id": "32714714500295_0",
                           "person_id": "32714714500295",
                           "event_order": 0,
                           "name": "柏拉图",
                           "time": "-427-00-00",
                           "space": "雅典/希腊雅典",
                           "abstract": "出生",
                           "content": "柏拉图（Plato，Πλατών，公元前427年—公元前347年），是古希腊伟大的哲学家，也是整个西方文化中最伟大的哲学家和思想家之一。柏拉图生于一个较为富裕的雅典奴隶主贵族家庭，宣称是古雅典国王的后代，他的父亲是阿里斯通(Ariston)、母亲是伯里提俄涅(Perictione)，他在家中排行老四。他也是当时雅典知名的政治家克里提亚(Critias)的侄子，不过两人之间的关系也仍有争议。",
                           "event_weight": 5,
                           "longitude_latitude": "23.727539,37.98381",
                           "event_country": "希腊",
                           "check_status": "-1"}
            self.create_life_event_info_table(temp_life_e)
            self.table_layout.replaceWidget(self.rel_table, self.life_event_table)
            self.FLAG_Current_Table = "life_event"
            print("切换为表：" + self.FLAG_Current_Table)

        elif self.FLAG_Current_Table == "life_event":
            print('\"' + "trans_tables_button" + '\"' + "按钮被点击")
            print("当前表：" + self.FLAG_Current_Table)
            """
                此处self.table_layout.replaceWidget替换为基本信息表
            """
            self.create_base_info_table(self.find_one_base_info_in_temp1)
            self.table_layout.replaceWidget(self.life_event_table, self.table)
            self.FLAG_Current_Table = "base_info"
            print("切换为表：" + self.FLAG_Current_Table)

        # rel_checker.show()

    @pyqtSlot()
    def trans2life_event_button_on_click(self):
        """
            点击切换为生平表
        :return:
        """
        print('\"' + "生平" + '\"' + "按钮被点击")
        life_event_checker.show()

    @pyqtSlot()
    def button1_on_click(self):
        self.index = self.index - 1
        self.page_up_flag = True
        print('\"' + "上一页" + '\"' + "被点击")
        # self.table.clear()

        if self.index < 0:
            self.button1.setEnabled(False)
            # buttonReply = QMessageBox.question(self, 'Warning!', "已经回到首页,是否继续校对？", QMessageBox.Ok,
            #                                    QMessageBox.No)
            # if buttonReply == QMessageBox.Ok:
            #     print("继续校对")
            #     count_row_ = 0
            #     self.index = 0
            #     if self.person_id_prcessed_current_list:
            #         for k, v in self.my_order_dict[self.person_id_prcessed_current_list[self.index]].items():
            #             self.table.setItem(count_row_, 0, QTableWidgetItem(str(k)))
            #             # self.table.setEditTriggers(count_row_, 0, QAbstractItemView.NoEditTriggers)  # 禁止编辑
            #             self.table.setItem(count_row_, 1, QTableWidgetItem(str(v)))
            #             count_row_ += 1
            #
            #     self.cell_no_edit()
            #
            # else:
            #     buttonReply2 = QMessageBox.question(self, 'Warning!', "确认退出？", QMessageBox.Ok, QMessageBox.No)
            #     if buttonReply2 == QMessageBox.Ok:
            #         self.close()
            #         print("退出")

            buttonReply = QMessageBox.question(self, 'Warning', "已经回到首页！", QMessageBox.Ok)
            if buttonReply == QMessageBox.Ok:
                print("已经回到首页，点击OK继续校对")
                count_row_ = 0
                self.index = 0
                if self.person_id_prcessed_current_list:
                    for k, v in self.my_order_dict[self.person_id_prcessed_current_list[self.index]].items():
                        self.table.setItem(count_row_, 0, QTableWidgetItem(str(k)))
                        # self.table.setEditTriggers(count_row_, 0, QAbstractItemView.NoEditTriggers)  # 禁止编辑
                        self.table.setItem(count_row_, 1, QTableWidgetItem(str(v)))
                        count_row_ += 1
                self.cell_no_edit()

        else:
            count_row_ = 0
            for k, v in self.my_order_dict[self.person_id_prcessed_current_list[self.index]].items():
                self.table.setItem(count_row_, 0, QTableWidgetItem(str(k)))
                # self.table.setEditTriggers(count_row_, 0, QAbstractItemView.NoEditTriggers)  # 禁止编辑
                self.table.setItem(count_row_, 1, QTableWidgetItem(str(v)))
                count_row_ += 1
            self.cell_no_edit()


    @pyqtSlot()
    def button2_on_click(self):
        self.button1.setEnabled(True)
        print('\"' + "下一页" + '\"' + "被点击")
        if self.page_up_flag:  # 当上一页被点击后执行
            self.auto_save()  # 自动检测并提示是否保存修改
            if self.FLAG_ALL_RIGHT:
                self.index += 1
                if self.index != len(self.person_id_prcessed_current_list):
                    count_row_ = 0
                    for k, v in self.my_order_dict[self.person_id_prcessed_current_list[self.index]].items():
                        self.table.setItem(count_row_, 0, QTableWidgetItem(str(k)))
                        self.table.setItem(count_row_, 1, QTableWidgetItem(str(v)))
                        count_row_ += 1
                    self.cell_no_edit()
                else:
                    count_row_ = 0
                    for k, v in self.find_one_base_info_in_temp1.items():
                        self.table.setItem(count_row_, 0, QTableWidgetItem(str(k)))
                        self.table.setItem(count_row_, 1, QTableWidgetItem(str(v)))
                        count_row_ += 1
                    self.page_up_flag = False
                    self.cell_no_edit()

        else:
            temp_dict = {}
            count_row_temp = 0
            # print('\"' + "下一页" + '\"' + "被点击")
            # print(self.table.item(0, 0).text())  # 获取某一项的内容
            for k, v in self.find_one_base_info_in_temp1.items():
                if k == "check_status":
                    temp_dict[k] = str(int(self.check_status_) + 1)
                    continue
                temp_dict[k] = self.table.item(count_row_temp, 1).text()
                count_row_temp += 1

            self.person_id_prcessed_list = \
                [str(x["person_id"]) for x in self.information_ancient_base_temp2.find({}, {"person_id": 1})]
            temp_dict_copy = copy.deepcopy(temp_dict)

            """
                数据格式、逻辑校验
            """

            self.FLAG_ALL_RIGHT = self.data_format_check(temp_dict_copy)

            if self.FLAG_ALL_RIGHT:
                if str(self.person_id) not in self.person_id_prcessed_list:
                    # print(json.dumps(temp_dict, ensure_ascii=False, indent=2))
                    temp_dict_copy["check_author"] = self.job_num_  # 加入工号
                    self.information_ancient_base_temp2.insert_one(temp_dict_copy)
                    print("中间库（历史组）######" + self.col_temp2_ + "######插入一条新数据####person_id: "
                          + self.person_id)
                    self.information_ancient_base_temp1.update_one({"person_id": self.person_id},
                                                                   {"$set": {"check_status":
                                                                             str(int(self.check_status_) + 1)}})
                    print("初版库（AI）####" + self.col_base_info_temp1_ + "####person_id: " + self.person_id + " "
                          + '\"' + "check_status" + '\"' + "更新为: " + str(int(self.check_status_) + 1))
                    self.my_order_dict[self.person_id] = temp_dict
                    # self.person_id_prcessed_list.append(self.person_id)
                    self.person_id_prcessed_current_list.append(self.person_id)
                    self.index += 1

                    # self.table.clear()
                    self.query_base_info()
                    count_row_ = 0
                    for k, v in self.find_one_base_info_in_temp1.items():
                        self.table.setItem(count_row_, 0, QTableWidgetItem(str(k)))
                        self.table.setItem(count_row_, 1, QTableWidgetItem(str(v)))
                        count_row_ += 1
                    self.cell_no_edit()
                else:
                    print('\"' + "person_id: " + str(temp_dict["person_id"]) + " "
                          + "已存在" + self.col_temp2_ + "中")
                    self.auto_save()
                    if self.FLAG_ALL_RIGHT:
                        self.query_base_info()
                        count_row_ = 0
                        for k, v in self.find_one_base_info_in_temp1.items():
                            self.table.setItem(count_row_, 0, QTableWidgetItem(str(k)))
                            self.table.setItem(count_row_, 1, QTableWidgetItem(str(v)))
                            count_row_ += 1
                        self.cell_no_edit()

                    # self.information_ancient_base_temp2.update_one({"person_id": temp_dict_copy["person_id"]},
                    #                                                {"$set": temp_dict_copy})
                    # print("中间库（历史组）######" + self.config_dict["col_temp2"] + "######覆盖一条新数据####person_id: "
                    #       + self.person_id)



                    # buttonReply2 = QMessageBox.question(self, 'Hello, world!', "该条数据库已校对，是否覆盖？", QMessageBox.Ok, QMessageBox.No)
                    # if buttonReply2 == QMessageBox.Ok:
                    #     basic_information_table_temp.update_one({}, {"$set": temp_dict})
                    #     print("该条数据库已校对，完成覆盖")

    @pyqtSlot()
    def button3_on_click(self):
        print('\"' + "退出" + '\"' + "被点击")
        temp_dict = {}
        count_row_temp = 0
        for k, v in self.find_one_base_info_in_temp1.items():
            if k == "check_status":
                temp_dict[k] = str(int(self.check_status_) + 1)
                continue
            temp_dict[k] = self.table.item(count_row_temp, 1).text()
            count_row_temp += 1

        buttonReply1 = QMessageBox.question(self, 'Warning', "是否保存当前数据?", QMessageBox.Yes, QMessageBox.No)
        if buttonReply1 == QMessageBox.Yes:
            if self.page_up_flag:
                self.auto_save()
                if self.FLAG_ALL_RIGHT:
                    print("退出时，" + "中间库（历史组）######" + self.col_temp2_ +
                          "完成了一条数据的修改保存####person_id: " + self.table.item(0, 1).text())
            else:
                temp_dict_copy = copy.deepcopy(temp_dict)
                """
                    数据格式、逻辑校验
                """
                self.FLAG_ALL_RIGHT = self.data_format_check(temp_dict_copy)
                if self.FLAG_ALL_RIGHT:
                    temp_dict_copy["check_author"] = self.job_num_  # 加入工号
                    self.information_ancient_base_temp2.insert_one(temp_dict_copy)

                    print("退出时，中间库（历史组）######" + self.col_temp2_ + "######插入一条新数据####person_id: "
                          + temp_dict["person_id"])
                    if temp_dict["person_id"] not in self.person_id_prcessed_current_list:
                        self.information_ancient_base_temp1.update_one({"person_id": self.person_id},
                                                                       {"$set": {"check_status":
                                                                                 str(int(self.check_status_) + 1)}})
                        print("退出时，初版库（AI）####" + self.col_base_info_temp1_ + "####person_id: " + temp_dict["person_id"] + " "
                              + '\"' + "check_status" + '\"' + "更新为: " + str(int(self.check_status_) + 1))

                        self.my_order_dict[temp_dict["person_id"]] = temp_dict
                        self.person_id_prcessed_current_list.append(temp_dict["person_id"])
                        self.index += 1
                    else:
                        self.my_order_dict[temp_dict["person_id"]] = temp_dict
        else:
            self.information_ancient_base_temp1.update_one({"person_id": self.person_id},
                                                           {"$set": {
                                                               "check_status": str(self.check_status_)}})
            print("退出时，没有保存当前数据，初版库（AI）####" + self.col_base_info_temp1_ +
                  "####person_id: " + temp_dict["person_id"] + " "
                  + '\"' + "check_status" + '\"' + "更新为: " + str(self.check_status_))

        buttonReply2 = QMessageBox.question(self, 'Warning', "确认退出?", QMessageBox.Yes, QMessageBox.No)
        if buttonReply2 == QMessageBox.Yes:
            # print("Yeah")
            if buttonReply1 == QMessageBox.Yes:
                print("保存了当前的数据， 且退出！")
            elif buttonReply1 == QMessageBox.No:
                print("没有保存当前数据， 且退出！")
            """
                生成比对报告
            """
            self.close()
        else:
            if buttonReply1 == QMessageBox.Yes:
                print("保存了当前的数据， 且取消退出！")
            elif buttonReply1 == QMessageBox.No:
                print("没有保存当前数据， 且取消退出！")

    @pyqtSlot()
    def ser_person_info_button_on_click(self):
        print("点击了 自定义人物检索 按钮")
        searcher.show()
        # subprocess.call("python person_search.py", shell=True)

    def auto_save(self):  # 当内容发生改动后自动检测并提示用户是否覆盖
        temp_dict_update = {}
        count_row = 0
        for i in range(self.title_length):
            temp_dict_update[self.table.item(i, 0).text()] = self.table.item(i, 1).text()
            i += 1

        self.person_id_prcessed_list = [str(x["person_id"]) for x
                                        in self.information_ancient_base_temp2.find({}, {"person_id": 1})]
        data_raw_flag = copy.deepcopy(self.my_order_dict[temp_dict_update["person_id"]])
        data_raw_flag.pop("check_status")
        temp_dict_update.pop("check_status")

        """
          数据格式、逻辑校验
        """

        self.FLAG_ALL_RIGHT = self.data_format_check(temp_dict_update)

        if self.FLAG_ALL_RIGHT:
            if temp_dict_update != data_raw_flag:
                buttonReply_temp_b4 = QMessageBox.question(self, 'Waring', "确定修改？", QMessageBox.Yes, QMessageBox.No)
                if buttonReply_temp_b4 == QMessageBox.Yes:
                    print(json.dumps(temp_dict_update, ensure_ascii=False, indent=2))
                    if temp_dict_update["person_id"] in self.person_id_prcessed_list:
                        self.information_ancient_base_temp2.update_one({"person_id": temp_dict_update["person_id"]},
                                                                       {"$set": temp_dict_update})
                        self.my_order_dict[temp_dict_update["person_id"]].update(temp_dict_update)
                        print(self.col_temp2_ + " " + "完成一条临时数据的修改！ " +
                              "person_id: " + temp_dict_update["person_id"])
                    else:
                        print("ERROR!" + " person_id: " + temp_dict_update["person_id"] + "不在" + self.col_temp2_)
                else:
                    # self.close()
                    print("已取消当前数据修改")

    def data_format_check(self, temp_dict):
        """
          数据格式、逻辑校验
        """

        data_checker = data_check(temp_dict)
        flag_is_digital_weight_id = data_checker.is_digital_weight_id()
        flag_is_digital_category_id = data_checker.is_digital_category_id()
        flag_is_digital_age = data_checker.is_digital_age()
        flag_format_birth_date = data_checker.format_check_birth_date()
        flag_format_death_date = data_checker.format_check_death_date()
        flag_value_birth_year, flag_value_birth_month, flag_value_birth_day = \
            data_checker.check_birthday_year_month_day()
        flag_value_death_year, flag_value_death_month, flag_value_death_day = \
            data_checker.check_death_year_month_day()

        flag_introduction_noexist = data_checker.value_check_introduction()
        flag_all_name_noexist = data_checker.value_check_all_name()

        flag_age_greater_than_100 = False
        flag_age_less_than_0 = False
        flag_age_greater_than_0_and_less_than_10 = False
        flag_age_diff_greater_than_2 = False
        flag_age_noexist = False

        if flag_all_name_noexist:
            reply0 = QMessageBox.question(self, 'Warning', "姓名-不能为空！请检查。", QMessageBox.Ok)
            if reply0 == QMessageBox.Ok:
                print("reply0点击了Ok")

        if flag_is_digital_weight_id:
            reply1 = QMessageBox.question(self, 'Warning', "权重id-不是数字，请检查！", QMessageBox.Ok)
            if reply1 == QMessageBox.Ok:
                print("reply1点击了Ok")

        if flag_is_digital_category_id:
            reply2 = QMessageBox.question(self, 'Warning', "类别id-不是数字，请检查！", QMessageBox.Ok)
            if reply2 == QMessageBox.Ok:
                print("reply2点击了Ok")

        if flag_is_digital_age:
            reply3 = QMessageBox.question(self, 'Warning', "年龄-不是数字，请检查！", QMessageBox.Ok)
            if reply3 == QMessageBox.Ok:
                print("reply3点击了Ok")

        if flag_format_birth_date:
            reply4 = QMessageBox.question(self, 'Warning', "出生时间-格式错误，请检查！", QMessageBox.Ok)
            if reply4 == QMessageBox.Ok:
                print("reply4点击了Ok")
        else:
            if flag_value_birth_year:
                reply4_1 = QMessageBox.question(self, 'Warning', "出生时间-年份错误，不能为0xx，请检查！", QMessageBox.Ok)
                if reply4_1 == QMessageBox.Ok:
                    print("reply4_1点击了Ok")

            if flag_value_birth_month:
                reply4_2 = QMessageBox.question(self, 'Warning', "出生时间-月份错误，超出了范围，请检查！", QMessageBox.Ok)
                if reply4_2 == QMessageBox.Ok:
                    print("reply4_2点击了Ok")

            if flag_value_birth_day:
                reply4_3 = QMessageBox.question(self, 'Warning', "出生时间-日错误，超出了范围，请检查！", QMessageBox.Ok)
                if reply4_3 == QMessageBox.Ok:
                    print("reply4_3点击了Ok")

        if flag_format_death_date:
            reply5 = QMessageBox.question(self, 'Warning', "去世时间-格式错误，请检查！", QMessageBox.Ok)
            if reply5 == QMessageBox.Ok:
                print("reply5点击了Ok")
        else:
            if flag_value_death_year:
                reply5_1 = QMessageBox.question(self, 'Warning', "去世时间-年份错误，不能为0xx，请检查！", QMessageBox.Ok)
                if reply5_1 == QMessageBox.Ok:
                    print("reply5_1点击了Ok")

            if flag_value_death_month:
                reply5_2 = QMessageBox.question(self, 'Warning', "去世时间-月份错误，超出了范围，请检查！", QMessageBox.Ok)
                if reply5_2 == QMessageBox.Ok:
                    print("reply5_2点击了Ok")

            if flag_value_death_day:
                reply5_3 = QMessageBox.question(self, 'Warning', "去世时间-日错误，超出了范围，请检查！", QMessageBox.Ok)
                if reply5_3 == QMessageBox.Ok:
                    print("reply5_3点击了Ok")

        if not flag_is_digital_age and not flag_format_birth_date and not flag_format_death_date \
                and not flag_value_birth_year and not flag_value_birth_month and not flag_value_birth_day \
                and not flag_value_death_year and not flag_value_death_month and not flag_value_death_day:

            flag_age_greater_than_100, flag_age_less_than_0, flag_age_greater_than_0_and_less_than_10, \
            flag_age_diff_greater_than_2, flag_age_noexist = data_checker.value_check_birthday_death_date()

            if flag_age_less_than_0:
                reply6 = QMessageBox.question(self, 'Warning', "出生、去世时间-不符合逻辑，\n顺序错误，请检查！", QMessageBox.Ok)
                if reply6 == QMessageBox.Ok:
                    print("reply6点击了Ok")

            if flag_age_noexist:
                reply7 = QMessageBox.question(self, 'Warning', "有出生、去世时间，\n年龄不能为空！请补上", QMessageBox.Ok)
                if reply7 == QMessageBox.Ok:
                    print("reply7点击了Ok")

            if flag_age_greater_than_100:
                reply8 = QMessageBox.question(self, 'Warning', "由出生、去世时间得出\n年龄大于100岁，确定吗？",
                                              QMessageBox.Yes, QMessageBox.No)
                if reply8 == QMessageBox.Yes:
                    print("reply8点击了Yes")
                    flag_age_greater_than_100 = False
                else:
                    print("reply8点击了No")

            if flag_age_greater_than_0_and_less_than_10:
                reply9 = QMessageBox.question(self, 'Warning', "年龄小于10岁，确定吗？", QMessageBox.Yes, QMessageBox.No)
                if reply9 == QMessageBox.Yes:
                    print("reply9点击了Yes")
                    flag_age_greater_than_0_and_less_than_10 = False
                else:
                    print("reply9点击了No")

            if flag_age_diff_greater_than_2:
                reply10 = QMessageBox.question(self, 'Warning', "出生时间、去世时间计算出的年龄与实际给出的"
                                                                "\nage字段值相差大于2的，确定吗？",
                                               QMessageBox.Yes, QMessageBox.No)
                if reply10 == QMessageBox.Yes:
                    print("reply9点击了Yes")
                    flag_age_diff_greater_than_2 = False
                else:
                    print("reply10点击了No")

        if flag_introduction_noexist:
            reply11 = QMessageBox.question(self, 'Warning', "简介是空！确定吗？", QMessageBox.Yes, QMessageBox.No)
            if reply11 == QMessageBox.Yes:
                print("reply11点击了Yes")
                flag_introduction_noexist = False
            else:
                print("reply11点击了No")

        if not flag_is_digital_weight_id and not flag_is_digital_category_id and not flag_is_digital_age \
           and not flag_format_birth_date and not flag_format_death_date \
           and not flag_value_birth_year and not flag_value_birth_month and not flag_value_birth_day \
           and not flag_value_death_year and not flag_value_death_month and not flag_value_death_day \
           and not flag_age_greater_than_100 and not flag_age_less_than_0 \
           and not flag_age_greater_than_0_and_less_than_10 and not flag_age_diff_greater_than_2 \
           and not flag_age_noexist and not flag_all_name_noexist and not flag_introduction_noexist:
            return True
        else:
            return False


class Relation_Check(QWidget):
    def __init__(self):
        super().__init__()
        self.title = '人物关系'
        desktop = QApplication.desktop()
        print("屏幕宽:" + str(desktop.width()))
        print("屏幕高:" + str(desktop.height()))
        self.left = 50
        self.top = 50
        self.width = desktop.width() - 150
        self.height = desktop.height() - 100
        self.person_id = ""
        self.all_name = ""
        self.common_name = ""
        self.ser_input_content = ""
        self.title_length = 28
        self.db_server_ip = "192.168.1.23"
        self.db_server_port = "27017"
        self.db_database_name = "information"
        self.db_col_name = "information_ancient_base_temp1"
        self.search_results = {}
        self.init_Relation_UI()

    def init_Relation_UI(self,):
        print("init_Relation_UI被调用")
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)


class Life_Event_Check(QWidget):
    def __init__(self):
        super().__init__()
        self.title = '人物生平'
        desktop = QApplication.desktop()
        print("屏幕宽:" + str(desktop.width()))
        print("屏幕高:" + str(desktop.height()))
        self.left = 50
        self.top = 50
        self.width = desktop.width() - 150
        self.height = desktop.height() - 100
        self.person_id = ""
        self.all_name = ""
        self.common_name = ""
        self.ser_input_content = ""
        self.title_length = 28
        self.db_server_ip = "192.168.1.23"
        self.db_server_port = "27017"
        self.db_database_name = "information"
        self.db_col_name = "information_ancient_base_temp1"
        self.search_results = {}
        self.init_Life_Event_UI()

    def init_Life_Event_UI(self,):
        print("init_Life_Event_UI被调用")
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)


class Person_Search(QWidget):  # 继承自 QWidget类
    def __init__(self):
        super().__init__()
        self.title = '人物基本信息搜索'
        desktop = QApplication.desktop()
        print("屏幕宽:" + str(desktop.width()))
        print("屏幕高:" + str(desktop.height()))
        self.left = 50
        self.top = 50
        self.width = desktop.width() - 150
        self.height = desktop.height() - 100
        self.person_id = ""
        self.all_name = ""
        self.common_name = ""
        self.ser_input_content = ""
        self.title_length = 28
        self.db_server_ip = "192.168.1.23"
        self.db_server_port = "27017"
        self.db_database_name = "information"
        self.db_col_name = "information_ancient_base_temp1"
        self.search_results = {}
        self.init_search_UI()
        # self.config_dict = {"mongodb_ip": "192.168.1.23", "mongodb_name": "information",
        #                     "col_temp1": "information_ancient_base_temp1"}

    def init_search_UI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.db_server_ip_label = QLabel('Mongo数据库IP:', self)
        self.db_server_ip_text = QLineEdit(self)
        self.db_server_ip_text.setText(self.db_server_ip)
        # self.db_server_ip_text.setPlaceholderText("例如： 192.168.1.23")  # 设置隐藏文字

        self.db_server_port_label = QLabel('端口号(PORT):', self)
        self.db_server_port_text = QLineEdit(self)
        self.db_server_port_text.setText(self.db_server_port)  # 默认端口

        self.db_database_name_label = QLabel('数据库名(DataBase_Name):', self)
        self.db_database_name_text = QLineEdit(self)
        self.db_database_name_text.setText(self.db_database_name)

        self.db_col_name_label = QLabel('集合名(Collection_Name):', self)
        self.db_col_name_text = QLineEdit(self)
        self.db_col_name_text.setText(self.db_col_name)

        self.ipconfig_layout = QHBoxLayout()
        self.ipconfig_layout.addWidget(self.db_server_ip_label)
        self.ipconfig_layout.addWidget(self.db_server_ip_text)
        self.ipconfig_layout.addWidget(self.db_server_port_label)
        self.ipconfig_layout.addWidget(self.db_server_port_text)
        self.ipconfig_layout.addWidget(self.db_database_name_label)
        self.ipconfig_layout.addWidget(self.db_database_name_text)
        self.ipconfig_layout.addWidget(self.db_col_name_label)
        self.ipconfig_layout.addWidget(self.db_col_name_text)

        """
            分项搜索框设置
        """
        # self.person_id_label = QLabel('人物id:', self)
        # self.person_id_text = QLineEdit(self)
        # self.person_id_text.setPlaceholderText("例如： 32714701100321")
        #
        # self.all_name_label = QLabel('姓名:', self)
        # self.all_name_text = QLineEdit(self)
        # self.all_name_text.setPlaceholderText("例如： 嬴政")
        #
        # self.common_name_label = QLabel('同等姓名指代:', self)
        # self.common_name_text = QLineEdit(self)
        # self.common_name_text.setPlaceholderText("例如： 秦王嬴政 或 秦始皇")

        self.search_button = QPushButton('搜索', self)
        self.search_button.setShortcut('Return')  #shortcut key   # 设置快捷键为Enter键
        # self.search_button.resize(50, 50)  # width, height

        # self.search_button.setIcon(QIcon(QPixmap("./images/python.png")))

        self.search_button.clicked.connect(self.search_button_on_click)

        # self.search_layout1.addWidget(self.person_id_label)
        # self.search_layout1.addWidget(self.person_id_text)
        # self.search_layout1.addWidget(self.all_name_label)
        # self.search_layout1.addWidget(self.all_name_text)
        # self.search_layout1.addWidget(self.common_name_label)
        # self.search_layout1.addWidget(self.common_name_text)

        """
            融合搜索框设置
        """
        # self.search_input_label = QLabel('搜索内容：', self)
        self.search_input_text = QLineEdit(self)
        # self.search_input_text.setFixedSize(550, 30)  # width, height
        # self.search_input_text.resize(550, 60)
        self.search_input_text.setStyleSheet("border: 1.5px solid blue;")  # 设置边框颜色
        self.search_input_text.setPlaceholderText("例如： 32714701100321 或 嬴政 或 秦王嬴政 或 秦始皇")

        self.search_layout1 = QHBoxLayout()
        self.search_layout1.setContentsMargins(550, 10, 550, 10)  # left=10, top=10, right=10, bottom=10
        self.search_layout1.addWidget(self.search_input_text)
        self.search_layout1.setSpacing(15)  # 组件间间距
        self.search_layout1.addWidget(self.search_button)

        self.data_model = {
                "person_id": "",
                "all_name": "",
                "surname": "",
                "name": "",
                "gender": "",
                "nationality": "",
                "sub_name1": "",
                "sub_name2": "",
                "another_name": "",
                "age": "",
                "native_place": "",
                "country1": "",
                "country2": "",
                "time_of_birth": "",
                "time_of_death": "",
                "place_of_death": "",
                "cause_of_death": "",
                "physical_features": "",
                "characteristics": "",
                "Preferences": "",
                "Occupation": "",
                "Achievements": "",
                "introduction": "",
                "person_weight_id": "",
                "person_category_id": "",
                "common_name": "",
                "longitude_latitude": "",
                "check_status": ""
                }

        # self.table_layout = QVBoxLayout()
        self.search_main_layout = QVBoxLayout()
        self.search_main_layout.addLayout(self.ipconfig_layout)
        self.search_main_layout.addLayout(self.search_layout1)
        # self.search_main_layout.addWidget(self.ser_result_textbox)

        self.create_search_person_table(self.data_model)

        self.search_main_layout.addWidget(self.table)
        self.setLayout(self.search_main_layout)

        # self.show()

    def show_search_result_on_table(self, ser_results):

        # print("\033[1;31m 字体颜色：红色\033[0m")
        # if len(ser_results) != 0:
            # search_results_one = ser_results[0]
        count_row = 1  # 留给英文labels
        self.table.setRowCount(len(ser_results) + 1)
        for i in ser_results:
            search_results_one_sorted = {}
            for k, v in self.data_model.items():
                search_results_one_sorted[k] = i[k]

            count_col = 0
            for k, v in search_results_one_sorted.items():
                if self.ser_input_content in v:
                    # ser_input_content_color = "\033[1;31m" + self.ser_input_content + "\033[0m"
                    # v_split = v.split(self.ser_input_content)
                    # print(ser_input_content_color)
                    # v = ser_input_content_color.join(v_split)
                    # print(v)
                    # newItem.setBackgroundColor(QColor(0,60,10))
                    newitem = QTableWidgetItem(v)
                    newitem.setForeground(QBrush(QColor(255, 0, 0)))
                    self.table.setItem(count_row, count_col, newitem)
                    # v_add_color = ""
                    # for i in v_split:
                    #     v_add_color += i + self.ser_input_content
                # self.table.setItem(0, count_col, QTableWidgetItem(str(k)))
                # self.table.setEditTriggers(count_row_, 0, QAbstractItemView.NoEditTriggers)  # 禁止编辑
                else:
                    newitem = QTableWidgetItem(v)
                    self.table.setItem(count_row, count_col, newitem)
                count_col += 1
              # 新插入一行
            count_row += 1
        # else:
        #     QMessageBox.question(self, 'Tips', "Sorry!没有检索到任何信息！\n请更换检索条件重新尝试", QMessageBox.Ok)

    def test_mongodb_connect(self, ip, port):
        """
            测试mongodb服务是否开启
        :return:
        """
        # epoch time before API call
        start = time.time()

        try:

            # attempt to create a client instance of PyMongo driver

            client = pymongo.MongoClient(host=[ip + ":" + port], serverSelectionTimeoutMS=2000)

            # call the server_info() to verify that client instance is valid

            server_info = client.server_info()  # will throw an exception
            # print(json.dumps(server_info, ensure_ascii=False, indent=2))
            print("connection succeeded！ elapsed： " + str(time.time() - start))
            return True

        except:

            print("")
            print("connection error! elapsed： " + str(time.time() - start))
            return False

        # print the time that has elapsed

    @pyqtSlot()
    def search_button_on_click(self):

        print("点击了 搜索 按钮")
        """
            获取用户输入的配置信息
        """
        self.db_server_ip = self.db_server_ip_text.text()
        self.db_server_port = self.db_server_port_text.text()
        self.db_database_name = self.db_database_name_text.text()
        self.db_col_name = self.db_col_name_text.text()

        # self.person_id = self.person_id_text.text()
        # self.all_name = self.all_name_text.text()
        # self.common_name = self.common_name_text.text()

        """
            连通测试
        """
        test_result = self.test_mongodb_connect(self.db_server_ip, self.db_server_port)
        if test_result:

            client = pymongo.MongoClient(self.db_server_ip, int(self.db_server_port))
            my_col = client[self.db_database_name][self.db_col_name]

            # if self.person_id:
            #     self.search_results = list(my_col.find({"person_id": self.person_id}, {"_id": 0}))
            #     self.show_search_result_on_table(self.search_results)
            #     return 0
            #
            # if self.all_name:
            #     # self.search_results = list(my_col.find({"all_name": '/' + self.all_name + '/'}, {"_id": 0}))
            #     self.search_results = list(my_col.find({"all_name": {'$regex': self.all_name}}, {"_id": 0}))  # 包含某字段的模糊查询
            #     self.show_search_result_on_table(self.search_results)
            #     return 0
            #
            # if self.common_name:
            #     # self.search_results = list(my_col.find({"common_name": self.common_name}, {"_id": 0}))
            #     self.search_results = list(my_col.find({"common_name": {'$regex': self.common_name}}, {"_id": 0}))  # 包含某字段的模糊查询
            #     self.show_search_result_on_table(self.search_results)
            #     return 0
            #
            # if not self.person_id and not self.all_name and not self.common_name:
            #     reply = QMessageBox.question(self, 'Warning', "输入有误，请检查！\n至少输入一个检索条件", QMessageBox.Ok)
            #     if reply == QMessageBox.Ok:
            #         print("输入有误 点击了 Ok")


            """
                优化搜索，合并分项搜索框，融合为一个搜索
            """
            self.ser_input_content = self.search_input_text.text()
            if self.ser_input_content:
                self.search_results = list(my_col.find({"person_id": self.ser_input_content}, {"_id": 0}))
                if len(self.search_results) != 0:
                    self.show_search_result_on_table(self.search_results)
                    return 0
                else:
                    self.search_results = list(my_col.find({"all_name": {'$regex': self.ser_input_content}}, {"_id": 0}))
                    if len(self.search_results) != 0:
                        self.show_search_result_on_table(self.search_results)
                        return 0
                    else:
                        self.search_results = \
                            list(my_col.find({"common_name": {'$regex': self.ser_input_content}}, {"_id": 0}))
                        if len(self.search_results) != 0:
                            self.show_search_result_on_table(self.search_results)
                            return 0
                        else:
                            self.search_results = \
                                list(my_col.find({"another_name": {'$regex': self.ser_input_content}}, {"_id": 0}))
                            if len(self.search_results) != 0:
                                self.show_search_result_on_table(self.search_results)
                                return 0
                            else:
                                QMessageBox.question(self, 'Tips', "Sorry! 没有检索到任何信息！\n请更换检索条件重新尝试", QMessageBox.Ok)
                                print("没有搜索到任何信息 点击了 Ok")
            else:
                reply = QMessageBox.question(self, 'Warning', "输入有误，请检查！\n至少输入一个检索条件", QMessageBox.Ok)
                if reply == QMessageBox.Ok:
                    print("没输入有误，请检查！至少输入一个检索条件 点击了 Ok")
        else:
            QMessageBox.question(self, 'Warning', "Sorry! 服务器链接失败，请检查！", QMessageBox.Ok)

    def create_search_person_table(self, data):

        # Create table  多列，每行显示一条数据，根据返回结果设定
        self.table = QTableWidget()
        self.table.setRowCount(1)  # 初始设为2， 每加一条数据行加1
        self.table.setColumnCount(self.title_length)
        # Todo 优化1 设置水平方向的表头标签
        self.table.setHorizontalHeaderLabels(['人物id', '姓名', '姓', '名', '性别', '民族', '字', '号', '别称', '年龄',
                                              '籍贯', '国家', '所处时代', '出生时间', '去世时间', '去世地点', '去世原因',
                                              '外貌特征', '性格特点', '偏好', '职业', '成就', '简介', '权重id', '类别id',
                                              '同等姓名指代', '籍贯经纬度', '校验状态'])
        # TODO 优化 6 表格头的显示与隐藏
        # self.table.verticalHeader().setVisible(False)
        # self.table.horizontalHeader().setVisible(False)

        # self.table.setItemDelegateForColumn(0, EmptyDelegate(self))   # 设置第一列不可编辑
        # self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)  # 单元格长度随内容变化
        # self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        # self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        # self.table.horizontalHeader().setSectionResizeMode(1, )
        # self.table.horizontalHeader().setSectionResizeMode(22, QHeaderView.Stretch)  # 单元格伸展

        """
            设置滚动条样式
        """
        self.table.horizontalScrollBar().setStyleSheet("QScrollBar:horizontal{"
                                                       "background:#FFFFFF;"
                                                       "padding-top:3px;"
                                                       "padding-bottom:3px;"
                                                       "padding-left:20px;"
                                                       "padding-right:20px;}"
                                                       "QScrollBar::handle:horizontal{"
                                                       "background:#dbdbdb;"
                                                       "border-radius:6px;"
                                                       "min-width:80px;}"
                                                       "QScrollBar::handle:horizontal:hover{"
                                                       "background:#d0d0d0;}"
                                                       "QScrollBar::add-line:horizontal{"
                                                       "background:url(:) center no-repeat;}"
                                                       "QScrollBar::sub-line:horizontal{"
                                                       "background:url(:) center no-repeat;}")
        # self.table.verticalScrollBar().setStyleSheet()

        count_col = 0
        for k, v in data.items():
            self.table.setItem(0, count_col, QTableWidgetItem(str(k)))
            # self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)  # 禁止编辑
            # self.table.setItem(1, count_col, QTableWidgetItem(str(v)))
            count_col += 1




if __name__ == '__main__':
    Job_num = ""
    Mongodb_ip = "192.168.1.23"
    Port = "27017"
    Mongodb_name = "information"
    Col_base_info_temp1 = "information_ancient_base_temp1"
    Col_base_info_temp2 = "information_ancient_base_temp2"
    Col_base_info_final = "information_ancient_base"
    Col_rel_info_temp1 = "information_ancient_relation_temp1"
    Col_rel_info_temp2 = "information_ancient_relation_temp2"
    Col_rel_info_final = "information_ancient_relation"
    Col_event_info_temp1 = "information_ancient_event_temp1"
    Col_event_info_temp2 = "information_ancient_event_temp2"
    Col_event_info_final = "information_ancient_event"
    Check_status = "0"
    Mongodb_name_logs = "information_update_logs"
    Col_logs = "information_ancient_base_log"

    app = QApplication(sys.argv)
    login_app = App_login(job_num=Job_num, mongodb_ip=Mongodb_ip, port=Port,
                          mongodb_name=Mongodb_name,
                          col_base_info_temp1=Col_base_info_temp1,
                          col_base_info_temp2=Col_base_info_temp2,
                          col_base_info_final=Col_base_info_final,
                          col_rel_info_temp1=Col_rel_info_temp1,
                          col_rel_info_temp2=Col_rel_info_temp2,
                          col_rel_info_final=Col_rel_info_final,
                          col_event_info_temp1=Col_event_info_temp1,
                          col_event_info_temp2=Col_event_info_temp2,
                          col_event_info_final=Col_event_info_final,
                          check_status=Check_status,
                          mongodb_name_logs=Mongodb_name_logs,
                          col_logs=Col_logs)

    main_app = App(job_num=Job_num, mongodb_ip=Mongodb_ip, port=Port,
                   mongodb_name=Mongodb_name,
                   col_base_info_temp1=Col_base_info_temp1,
                   col_base_info_temp2=Col_base_info_temp2,
                   col_base_info_final=Col_base_info_final,
                   col_rel_info_temp1=Col_rel_info_temp1,
                   col_rel_info_temp2=Col_rel_info_temp2,
                   col_rel_info_final=Col_rel_info_final,
                   col_event_info_temp1=Col_event_info_temp1,
                   col_event_info_temp2=Col_event_info_temp2,
                   col_event_info_final=Col_event_info_final,
                   check_status=Check_status,
                   mongodb_name_logs=Mongodb_name_logs,
                   col_logs=Col_logs)

    searcher = Person_Search()
    rel_checker = Relation_Check()
    life_event_checker = Life_Event_Check()

    sys.exit(app.exec_())
