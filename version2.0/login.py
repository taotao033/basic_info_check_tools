from PyQt5.QtWidgets import QApplication, QWidget, QTableWidget, QHeaderView, QTableWidgetItem, QVBoxLayout, \
    QHBoxLayout, QPushButton, QDesktopWidget, QLabel, QLineEdit, QAbstractItemView, \
    QItemDelegate, QAction, QFontDialog, QMessageBox
from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtGui import QIcon
import pymongo
import time
import sys


class App_Login(QWidget):

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
                 col_base_info_logs,
                 col_rel_info_logs,
                 col_event_info_logs,
                 main_win):  # 登陆页
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
        :param col_base_info_logs: 基本信息（修改记录的）日志集合名
        :param col_rel_info_logs: 关系（修改记录的）日志集合名
        :param col_event_info_logs: 生平（修改记录的）日志集合名
        :param main_win: 主窗口
        """
        super().__init__()
        self.title = 'EveryX历史数据信息校对助手'
        self.left = 10
        self.top = 10
        self.width = 600
        self.height = 110

        self.job_num = job_num
        self.mongodb_ip = mongodb_ip
        self.port = port
        self.mongodb_name = mongodb_name
        self.col_base_info_temp1 = col_base_info_temp1  # 校对前-基本信息表
        self.col_base_info_temp2 = col_base_info_temp2  # 校对后-基本信息表
        self.col_base_info_final = col_base_info_final  # 最终库-基本信息表

        self.col_rel_info_temp1 = col_rel_info_temp1  # 校对前-关系表
        self.col_rel_info_temp2 = col_rel_info_temp2  # 校对后-关系表
        self.col_rel_info_final = col_rel_info_final  # 最终库-关系表

        self.col_event_info_temp1 = col_event_info_temp1  # 校对前-生平表
        self.col_event_info_temp2 = col_event_info_temp2  # 校对后-生平表
        self.col_event_info_final = col_event_info_final  # 最终库-生平表

        self.check_status = check_status

        self.mongodb_name_logs = mongodb_name_logs
        self.col_base_info_logs = col_base_info_logs
        self.col_rel_info_logs = col_rel_info_logs
        self.col_event_info_logs = col_event_info_logs
        self.main_win = main_win

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

        self.col_base_info_b_layout = QHBoxLayout()  # 水平
        self.db_col_base_info_label_b = QLabel('(基本信息)校对前集合名:', self)
        self.db_col_base_info_text_b = QLineEdit(self)
        self.db_col_base_info_text_b.setText(self.col_base_info_temp1)
        self.col_base_info_b_layout.addWidget(self.db_col_base_info_label_b)
        self.col_base_info_b_layout.addWidget(self.db_col_base_info_text_b)
        self.col_base_info_b_layout.setSpacing(10)  # 设置控件间距

        self.col_base_info_a_layout = QHBoxLayout()  # 水平
        self.db_col_base_info_label_a = QLabel('(基本信息)校对后集合名:', self)
        self.db_col_base_info_text_a = QLineEdit(self)
        self.db_col_base_info_text_a.setText(self.col_base_info_temp2)
        self.col_base_info_a_layout.addWidget(self.db_col_base_info_label_a)
        self.col_base_info_a_layout.addWidget(self.db_col_base_info_text_a)
        self.col_base_info_a_layout.setSpacing(19)  # 设置控件间距

        self.col_rel_info_b_layout = QHBoxLayout()  # 水平
        self.db_col_rel_info_label_b = QLabel('(人物关系)校对前集合名:', self)
        self.db_col_rel_info_text_b = QLineEdit(self)
        self.db_col_rel_info_text_b.setText(self.col_rel_info_temp1)
        self.col_rel_info_b_layout.addWidget(self.db_col_rel_info_label_b)
        self.col_rel_info_b_layout.addWidget(self.db_col_rel_info_text_b)
        self.col_rel_info_b_layout.setSpacing(10)  # 设置控件间距

        self.col_rel_info_a_layout = QHBoxLayout()  # 水平
        self.db_col_rel_info_label_a = QLabel('(人物关系)校对后集合名:', self)
        self.db_col_rel_info_text_a = QLineEdit(self)
        self.db_col_rel_info_text_a.setText(self.col_rel_info_temp2)
        self.col_rel_info_a_layout.addWidget(self.db_col_rel_info_label_a)
        self.col_rel_info_a_layout.addWidget(self.db_col_rel_info_text_a)
        self.col_rel_info_a_layout.setSpacing(19)  # 设置控件间距

        self.col_event_info_b_layout = QHBoxLayout()  # 水平
        self.db_col_event_info_label_b = QLabel('(人物生平)校对前集合名:', self)
        self.db_col_event_info_text_b = QLineEdit(self)
        self.db_col_event_info_text_b.setText(self.col_event_info_temp1)
        self.col_event_info_b_layout.addWidget(self.db_col_event_info_label_b)
        self.col_event_info_b_layout.addWidget(self.db_col_event_info_text_b)
        self.col_event_info_b_layout.setSpacing(10)  # 设置控件间距

        self.col_event_info_a_layout = QHBoxLayout()  # 水平
        self.db_col_event_info_label_a = QLabel('(人物生平)校对后集合名:', self)
        self.db_col_event_info_text_a = QLineEdit(self)
        self.db_col_event_info_text_a.setText(self.col_event_info_temp2)
        self.col_event_info_a_layout.addWidget(self.db_col_event_info_label_a)
        self.col_event_info_a_layout.addWidget(self.db_col_event_info_text_a)
        self.col_event_info_a_layout.setSpacing(19)  # 设置控件间距

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

        self.col_base_info_logs_layout = QHBoxLayout()  # 水平
        self.col_base_info_logs_label = QLabel('(基本信息)修改记录-集合名:', self)
        self.col_base_info_logs_text = QLineEdit(self)
        self.col_base_info_logs_text.setText(self.col_base_info_logs)
        self.col_base_info_logs_layout.addWidget(self.col_base_info_logs_label)
        self.col_base_info_logs_layout.addWidget(self.col_base_info_logs_text)
        self.col_base_info_logs_layout.setSpacing(19)  # 设置控件间距

        self.col_rel_info_logs_layout = QHBoxLayout()  # 水平
        self.col_rel_info_logs_label = QLabel('(人物关系)修改记录-集合名:', self)
        self.col_rel_info_logs_text = QLineEdit(self)
        self.col_rel_info_logs_text.setText(self.col_rel_info_logs)
        self.col_rel_info_logs_layout.addWidget(self.col_rel_info_logs_label)
        self.col_rel_info_logs_layout.addWidget(self.col_rel_info_logs_text)
        self.col_rel_info_logs_layout.setSpacing(19)  # 设置控件间距

        self.col_event_info_logs_layout = QHBoxLayout()  # 水平
        self.col_event_info_logs_label = QLabel('(人物生平)修改记录-集合名:', self)
        self.col_event_info_logs_text = QLineEdit(self)
        self.col_event_info_logs_text.setText(self.col_event_info_logs)
        self.col_event_info_logs_layout.addWidget(self.col_event_info_logs_label)
        self.col_event_info_logs_layout.addWidget(self.col_event_info_logs_text)
        self.col_event_info_logs_layout.setSpacing(19)  # 设置控件间距

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
        self.main_layout_login.addLayout(self.col_base_info_b_layout)
        self.main_layout_login.addLayout(self.col_base_info_a_layout)
        self.main_layout_login.addLayout(self.col_rel_info_b_layout)
        self.main_layout_login.addLayout(self.col_rel_info_a_layout)
        self.main_layout_login.addLayout(self.col_event_info_b_layout)
        self.main_layout_login.addLayout(self.col_event_info_a_layout)
        self.main_layout_login.addLayout(self.db_name_logs_layout)
        self.main_layout_login.addLayout(self.col_base_info_logs_layout)
        self.main_layout_login.addLayout(self.col_rel_info_logs_layout)
        self.main_layout_login.addLayout(self.col_event_info_logs_layout)
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
            self.db_col_base_info_label_b.setText("Col_Base_Info_Before:")
            self.db_col_base_info_label_a.setText("Col_Base_Info_After:")
            self.db_col_rel_info_label_b.setText("Col_Relation_Info_Before:")
            self.db_col_rel_info_label_a.setText("Col_Relation_Info_After:")
            self.db_col_event_info_label_b.setText("Col_Event_Info_Before:")
            self.db_col_event_info_label_a.setText("Col_Event_Info_After:")
            # self.check_status_label.setText("Check_Status:")
            self.db_name_logs_label.setText("DataBase_Name_Logs:")
            self.col_base_info_logs_label.setText("Col_Base_Info_Logs:")
            self.col_rel_info_logs_label.setText("Col_Relation_Info_Logs:")
            self.col_event_info_logs_label.setText("Col_Event_Info_Logs:")
            self.button_test.setText("Test")
            self.button_login.setText("Login")
        else:
            self.job_num_label.setText("工号:")
            self.job_num_text.setPlaceholderText("例如： AI-1011")
            self.db_server_ip_label.setText("数据库地址:")
            self.db_server_port_label.setText("端口号:")
            self.db_database_name_label.setText("数据库名:")
            self.db_col_base_info_label_b.setText("(基本信息)校对前集合名:")
            self.db_col_base_info_label_a.setText("(基本信息)校对后集合名:")
            self.db_col_rel_info_label_b.setText("(人物关系)校对前集合名:")
            self.db_col_rel_info_label_a.setText("(人物关系)校对后集合名:")
            self.db_col_rel_info_label_b.setText("(人物生平)校对前集合名:")
            self.db_col_rel_info_label_a.setText("(人物生平)校对后集合名:")
            # self.check_status_label.setText("校对前状态值:")
            self.db_name_logs_label.setText("存储修改记录-数据库名:")
            self.col_base_info_logs_label.setText("(基本信息)修改记录-集合名:")
            self.col_rel_info_logs_label.setText("(人物关系)修改记录-集合名:")
            self.col_event_info_logs_label.setText("(人物生平)修改记录-集合名:")
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

        self.col_base_info_temp1 = self.db_col_base_info_text_b.text()
        if not self.col_base_info_temp1:
            reply5_1 = QMessageBox.question(self, 'Warning', "(基本信息)校对前集合名(Col_Base_Info_Before)不能为空！请输入",
                                            QMessageBox.Ok)

        self.col_base_info_temp2 = self.db_col_base_info_text_a.text()
        if not self.col_base_info_temp2:
            reply6_1 = QMessageBox.question(self, 'Warning', "(基本信息)校对后集合名(Col_Base_Info_After)不能为空！请输入",
                                            QMessageBox.Ok)

        self.col_rel_info_temp1 = self.db_col_rel_info_text_b.text()
        if not self.col_rel_info_temp1:
            reply5_2 = QMessageBox.question(self, 'Warning', "(人物关系)校对前集合名(Col_Relation_Info_Before)不能为空！请输入",
                                            QMessageBox.Ok)

        self.col_rel_info_temp2 = self.db_col_rel_info_text_a.text()
        if not self.col_rel_info_temp2:
            reply6_2 = QMessageBox.question(self, 'Warning', "(人物关系)校对后集合名(Col_Relation_Info_After)不能为空！请输入",
                                            QMessageBox.Ok)

        self.col_event_info_temp1 = self.db_col_event_info_text_b.text()
        if not self.col_event_info_temp1:
            reply5_3 = QMessageBox.question(self, 'Warning', "(人物生平)校对前集合名(Col_Event_Info_Before)不能为空！请输入",
                                            QMessageBox.Ok)

        self.col_event_info_temp2 = self.db_col_event_info_text_a.text()
        if not self.col_event_info_temp2:
            reply6_3 = QMessageBox.question(self, 'Warning', "(人物生平)校对后集合名(Col_Event_Info_After)不能为空！请输入",
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
            if self.job_num and self.mongodb_ip and self.port and self.mongodb_name \
                    and self.col_base_info_temp1 and self.col_base_info_temp2 \
                    and self.col_rel_info_temp1 and self.col_rel_info_temp2 \
                    and self.col_event_info_temp1 and self.col_event_info_temp2 \
                    and self.check_status:
                """
                    给下一个页面传参
                """
                self.main_win.job_num_ = self.job_num
                self.main_win.mongodb_ip_ = self.mongodb_ip
                self.main_win.port_ = self.port
                self.main_win.mongodb_name_ = self.mongodb_name
                self.main_win.col_base_info_temp1_ = self.col_base_info_temp1
                self.main_win.col_base_info_temp2_ = self.col_base_info_temp2
                self.main_win.col_base_info_final_ = self.col_base_info_final
                self.main_win.mongodb_name_logs_ = self.mongodb_name_logs
                self.main_win.col_base_info_logs_ = self.col_base_info_logs
                self.main_win.check_status_ = self.check_status

                # main_app.connect_db()  # 连接数据库
                self.main_win.show()  # 显示主窗口

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


