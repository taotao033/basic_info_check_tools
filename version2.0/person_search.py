from PyQt5.QtWidgets import QApplication, QWidget, QTableWidget, QHeaderView, QTableWidgetItem, QVBoxLayout, \
    QHBoxLayout, QPushButton, QDesktopWidget, QLabel, QLineEdit, QAbstractItemView, \
    QItemDelegate, QAction, QFontDialog, QMessageBox
from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtGui import QIcon, QBrush, QColor
import pymongo
import time


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
        self.title_length = 31
        self.db_server_ip = "192.168.1.23"
        self.db_server_port = "27017"
        self.db_database_name = "earth_gis"
        self.db_col_name = "Information_ancient_base_temp1"
        self.search_results = {}
        self.labels_en2zh_base_info = {}
        self.setup_tab_labels()
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

    def setup_tab_labels(self):
        """
            表头schemas
        :return:
        """
        self.labels_en2zh_base_info = {
            "person_id": "人物id",
            "all_name": "姓名",
            "surname": "姓",
            "name": "名",
            "sub_name1": "字",
            "sub_name2": "号",
            "another_name": "别称",
            "common_name": "同等姓名指代",
            "gender": "性别",
            "age": "年龄",
            "nationality": "民族",
            "native_place": "籍贯",
            "longitude_latitude": "籍贯经纬度",
            "country1": "国家",
            "country2": "所处时代",
            "time_of_birth": "出生时间",
            "time_of_death": "去世时间",
            "place_of_death": "去世地点",
            "cause_of_death": "去世原因",
            "physical_features": "外貌特征",
            "characteristics": "性格特点",
            "preferences": "偏好",
            "occupation": "职业",
            "person_category_id": "类别id",
            "achievements": "成就",
            "person_weight_id": "权重id",
            "introduction": "简介",
            "up_time": "更新时间",
            "author": "表维护者",
            "effective_status": "删除状态",
            "check_status": "校验状态"
        }

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
        self.table.setColumnCount(len(self.labels_en2zh_base_info))
        # Todo 优化1 设置水平方向的表头标签
        self.table.setHorizontalHeaderLabels(list(self.labels_en2zh_base_info.values()))
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
