import sys
from PyQt5.QtWidgets import QApplication, QWidget, QTableWidget, QHeaderView, QTableWidgetItem, QVBoxLayout, \
    QHBoxLayout, QPushButton, QDesktopWidget, QLabel, QLineEdit, QAbstractItemView, \
    QItemDelegate, QAction, QFontDialog, QMessageBox,  QComboBox
from PyQt5.QtGui import QIcon, QBrush, QColor, QFont
from PyQt5 import QtGui
from PyQt5.QtCore import pyqtSlot, Qt, pyqtBoundSignal
import pymongo
import json
import copy
from time import strftime, localtime
import re
import collections
from data_check import data_check
import time
from login import App_Login
from person_search import Person_Search
from rel_name_fuzzy_search import ExtendedComboBox


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
                 col_base_info_logs,
                 col_rel_info_logs,
                 col_event_info_logs,
                 search_engine):
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
        :param search_engine: 人物搜索引擎
        """
        super().__init__()
        self.title = 'EveryX历史数据信息校对助手'
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
        self.FLAG_3_tables_check_finished = False   # 3张表查看完毕时为True，否则点击下一页按钮触发警告
        self.find_one_base_info_in_temp1 = {}   # 临时存放查询的一个人物基本信息
        self.find_rel_info_in_temp1 = {}    # 临时存放查询的一个人物的所有关系
        self.find_event_info_in_temp1 = {}  # 临时存放查询的一个人物的所有生平
        self.person_id = ""     # 过程中的person_id
        self.person_id_prcessed_list = []  # 用于存储col_base_info_temp1中已经校对完的person_id
        self.person_id_prcessed_current_list = []  # 仅用于存储当次程序运行中校对完的person_id
        # self.my_order_dict = collections.OrderedDict()
        self.my_order_dict = {}     # 存放此次程序校对完成的所有基本信息表
        self.my_rel_info_order_dict = {}    # 存放此次程序校对完成的所有关系信息表
        self.my_event_info_order_dict = {}  # 存放此次程序校对完成的所有生平信息表

        self.labels_en2zh_base_info = {}    # 基本信息表表头
        self.labels_en2id_base_info = {}    # 表头id

        self.labels_en2zh_rel_info = {}  # 关系信息表表头
        self.labels_en2id_rel_info = {}

        self.labels_en2zh_event_info = {}  # 生平信息表表头
        self.labels_en2id_event_info = {}
        # self.title_length = 31  # 基本信息的长度
        self.table = QTableWidget()  # 展示基本信息表
        self.rel_table = QTableWidget()  # 展示关系表
        self.event_table = QTableWidget()  # 展示生平表

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
        self.col_base_info_logs_ = col_base_info_logs
        self.col_rel_info_logs_ = col_rel_info_logs
        self.col_event_info_logs_ = col_event_info_logs
        self.searcher = search_engine
        self.check_mode = "基本信息+关系+生平"

    def config_app_data_source_info(self, check_mode="基本信息+关系+生平"):
        self.check_mode = check_mode  # 校对模式选择
        self.client = pymongo.MongoClient([self.mongodb_ip_ + ":" + self.port_])

        """
            查询和存储基本信息表
        """
        self.information_ancient_base_temp1 = self.client[self.mongodb_name_][self.col_base_info_temp1_]
        self.information_ancient_base_temp2 = self.client[self.mongodb_name_][self.col_base_info_temp2_]
        self.information_ancient_base_log = self.client[self.mongodb_name_logs_][self.col_base_info_logs_]

        """
            查询和存储关系信息表
        """
        self.information_ancient_relation_temp1 = self.client[self.mongodb_name_][self.col_rel_info_temp1_]
        self.information_ancient_relation_temp2 = self.client[self.mongodb_name_][self.col_rel_info_temp2_]
        self.information_ancient_relation_log = self.client[self.mongodb_name_logs_][self.col_rel_info_logs_]
        self.Dictionary_person_category = self.client["dictionary_information"]["Dictionary_person_rel"]
        self.rel_name2id = {i["rel_name"]: i["rel_id"]
                            for i in list(self.Dictionary_person_category.find({}, {"rel_name": 1, "rel_id": 1}))}

        self.all_rel_list = list(self.rel_name2id.keys())

        """
            查询和存储生平信息表
        """
        self.information_ancient_event_temp1 = self.client[self.mongodb_name_][self.col_event_info_temp1_]
        self.information_ancient_event_temp2 = self.client[self.mongodb_name_][self.col_event_info_temp2_]
        self.information_ancient_event_log = self.client[self.mongodb_name_logs_][self.col_event_info_logs_]

        """
            配置搜索引擎地址
        """
        # self.client2 = pymongo.MongoClient(host="192.168.1.115",
        #                                    port=27017,
        #                                    username="anyread",
        #                                    password="helloworld")
        # self.information_ancient_base_gold = self.client2["earth_gis"]["Information_ancient_base"]

        self.client2 = pymongo.MongoClient(host="192.168.1.13",
                                           port=27017)
        self.information_ancient_base_gold = self.client2["person_basic_relathion_delete_post"]["nlp_extract_base_check_full"]

        self.setup_tab_labels()  # 设置表头
        self.labels_auth_config = json.load(open("labels_auth_config.json", "r", encoding="utf-8"))
        self.base_info_labels_auth_config = self.labels_auth_config["base_info_table"]
        self.rel_info_labels_auth_config = self.labels_auth_config["rel_info_table"]
        self.event_info_labels_auth_config = self.labels_auth_config["event_info_table"]

        # self.init_ui()

    def center(self, ):
        fg = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        fg.moveCenter(cp)
        self.move(fg.topLeft())
        pass

    def init_ui(self):
        # 在此处添加 窗口控件
        # self.setWindowTitle('添加关闭按钮')
        # self.setFont(QFont('微软雅黑', 20))
        # self.resize(400, 300)
        # self.setWindowIcon(QIcon('1.png'))

        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        # self.setWindowOpacity(0.9)  # 设置窗口透明度
        # self.setStyleSheet("background-image: url(./images/snow.jpg); background-attachment: fixed")

        # 居中窗口
        # qr = self.frameGeometry()
        # cp = QDesktopWidget().availableGeometry().center()
        # qr.moveCenter(cp)
        # self.move(qr.topLeft())
        self.center()

        self.query_base_info()
        self.create_base_info_table()
        self.show_base_info_in_table(self.find_one_base_info_in_temp1)

        # self.query_rel_info(self.person_id)
        # self.create_rel_info_table()

        # self.query_event_info(self.person_id)
        # self.create_event_info_table()

        # Add box layout, add table to box layout and add box layout to widget
        self.table_layout = QVBoxLayout()
        self.table_layout.addWidget(self.table)

        self.button_layout = QHBoxLayout()

        """
            切换为 基本信息/关系/生平 按钮
        """
        self.button1 = QPushButton('上一页', self)
        self.button1.setFixedSize(90, 30)
        self.button1.clicked.connect(self.button1_on_click)
        self.button_layout.addWidget(self.button1)
        self.button1.setEnabled(False)

        self.trans_tables_button = QPushButton('基本信息/关系/生平(F1)', self)
        self.trans_tables_button.setToolTip("点击切换(F1)")
        self.trans_tables_button.setShortcut('f1')  # 快捷切换
        self.trans_tables_button.setFixedSize(150, 30)
        self.trans_tables_button.clicked.connect(self.trans_tables_button_on_click)
        self.button_layout.addWidget(self.trans_tables_button)

        self.button2 = QPushButton('下一页(F2)', self)
        self.button2.setToolTip("点击后，自动保存当前数据(F2)")
        self.button2.setShortcut('f2')   # 快捷键
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
        self.labels_en2id_base_info = {k: idx for idx, k in enumerate(list(self.labels_en2zh_base_info.keys()))}

        self.labels_en2zh_rel_info = {
            "rel_infor_id": "关系信息标识id",
            "effective_status": "删除状态\n(1:有效 0:删除)",
            "person_1_name": "人物1姓名",
            "rel_name": "关系名称",
            "rel_direction": "关系方向id",
            "person_2_name": "人物2姓名",
            "rel_category_id": "关系类别id",
            "person_1_id": "人物1id",
            "rel_id": "关系id",
            "person_2_id": "人物2id",
            "up_time": "更新时间",
            "author": "表维护者"
        }
        self.labels_en2id_rel_info = {k: idx for idx, k in enumerate(list(self.labels_en2zh_rel_info.keys()))}

        self.labels_en2zh_event_info = {
            "person_id": "人物id",
            "up_time": "更新时间",
            "author": "表维护者",
            "effective_status": "删除状态",
            "event_id": "事件id",
            "event_weight": "事件权重",
            "longitude_latitude": "经纬度",
            "event_country": "国家",
            "all_name": "姓名",
            "event_order": "事件顺序",
            "time": "时间",
            "place": "地点",
            "abstract": "摘要",
            "content": "内容",
        }
        self.labels_en2id_event_info = {k: idx for idx, k in enumerate(list(self.labels_en2zh_event_info.keys()))}

    def query_base_info(self):
        self.find_one_base_info_in_temp1 = \
            self.information_ancient_base_temp1.find_one({"check_status": self.check_status_}, {"_id": 0, "new_add": 0})
        if self.find_one_base_info_in_temp1:

            self.person_id = self.find_one_base_info_in_temp1["person_id"]
            self.information_ancient_base_temp1.update_one({"person_id": self.person_id},
                                                           {"$set": {"check_status": "-1"}})
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

    def query_rel_info(self, person_1_id):
        self.find_rel_info_in_temp1 = \
            list(self.information_ancient_relation_temp1.find({"person_1_id": person_1_id}, {"_id": 0,
                                                                                             "check_status": 0}))
        if self.find_rel_info_in_temp1:
            self.information_ancient_relation_temp1.update_many({"person_1_id": person_1_id},
                                                                {"$set": {"check_status": "-1"}})
            print("初版库（AI）####" + self.col_rel_info_temp1_ + "####person_1_id: " + person_1_id + " "
                  + '\"' + "check_status" + '\"' + "更新为: -1")
        # else:   # 此人库中0条关系
        #     buttonReply = QMessageBox.question(self, 'Sorry!', "此人库中0条关系\n可跳过，请切换到生平",
        #                                        QMessageBox.Ok)
        #     if buttonReply == QMessageBox.Ok:
        #         print("person_1_id:" + person_1_id + ", 0条关系，跳过")
        return self.find_rel_info_in_temp1

    def query_event_info(self, person_id):
        self.find_event_info_in_temp1 = \
            list(self.information_ancient_event_temp1.find({"person_id": person_id}, {"_id": 0,
                                                                                      "check_status": 0
                                                                                      }))
        if self.find_event_info_in_temp1:
            self.information_ancient_event_temp1.update_many({"person_id": person_id},
                                                             {"$set": {"check_status": "-1"}})
            print("初版库（AI）####" + self.col_event_info_temp1_ + "####person_id: " + person_id + " "
                  + '\"' + "check_status" + '\"' + "更新为: -1")
        # else:   # 此人库中0条关系
        #     buttonReply = QMessageBox.question(self, 'Sorry!', "此人库中0条关系\n可跳过，请切换到生平",
        #                                        QMessageBox.Ok)
        #     if buttonReply == QMessageBox.Ok:
        #         print("person_1_id:" + person_1_id + ", 0条关系，跳过")
        return self.find_event_info_in_temp1

    def cell_no_edit(self):
        """
            针对基本信息表的
        :return:
        """
        # self.table.item(0, 1).setFlags(self.table.item(0, 1).flags() ^ Qt.ItemIsEditable)  # 设置person_id 对应的值不可被编辑
        # self.table.item(0, 1).setBackground(QtGui.QColor(220, 220, 220))  # 设置person_id 对应的值的底色
        # check_status_row = len(self.labels_en2zh_base_info) - 1
        # self.table.item(check_status_row, 1).setFlags(
        #     self.table.item(check_status_row, 1).flags() ^ Qt.ItemIsEditable)  # 设置check_status 对应的值不可被编辑
        # self.table.item(check_status_row, 1).setBackground(QtGui.QColor(220, 220, 220))  # 设置check_status 对应的值的底色
        #
        # author_row = len(self.labels_en2zh_base_info) - 3
        # self.table.item(author_row, 1).setFlags(
        #     self.table.item(author_row, 1).flags() ^ Qt.ItemIsEditable)  # 设置author 对应的值不可被编辑
        # self.table.item(author_row, 1).setBackground(QtGui.QColor(220, 220, 220))  # 设置author 对应的值的底色
        #
        # up_time_row = len(self.labels_en2zh_base_info) - 4
        # self.table.item(up_time_row, 1).setFlags(
        #     self.table.item(up_time_row, 1).flags() ^ Qt.ItemIsEditable)  # 设置up_time 对应的值不可被编辑
        # self.table.item(up_time_row, 1).setBackground(QtGui.QColor(220, 220, 220))  # 设置up_time 对应的值的底色

        """
            根据字段权限配置表配置字段编辑权限
            1:可编辑
            0:禁止编辑
        """
        for k, v in self.base_info_labels_auth_config.items():
            if not v:
                self.table.item(self.labels_en2id_base_info[k], 1).setFlags(
                    self.table.item(self.labels_en2id_base_info[k], 1).flags() ^ Qt.ItemIsEditable)  # 设置字段对应的值不可被编辑
                self.table.item(self.labels_en2id_base_info[k],
                                1).setBackground(QtGui.QColor(220, 220, 220))  # 设置字段对应的值的底色

    def create_base_info_table(self):
        """
            创建基本信息表格
        :return:
        """
        # Create table
        self.table = QTableWidget()  # 展示基本信息表
        self.table.setRowCount(len(self.labels_en2zh_base_info))
        self.table.setColumnCount(2)
        # Todo 优化1 设置垂直方向的表头标签
        vertical_header_labels = list(self.labels_en2zh_base_info.values())
        self.table.setVerticalHeaderLabels(vertical_header_labels)
        # TODO 优化 6 表格头的显示与隐藏
        # self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setVisible(False)

        self.table.setItemDelegateForColumn(0, EmptyDelegate(self))   # 设置第0列(english labels列)不可编辑
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)  # 第0列单元格长度随内容变化
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)  # 第一列填充至满屏
        # self.table.horizontalHeader().setSectionResizeMode(1, )
        # self.table.verticalHeader().setSectionResizeMode(22, QHeaderView.Stretch)  # 单元格伸展
        self.table.verticalHeader().setSectionResizeMode(26, QHeaderView.Stretch)  # 单元格伸展

    def show_base_info_in_table(self, data):
        """

        :param data: type:{}
        :return:
        """
        count_row = 0
        for k, v in data.items():

            if k == "effective_status":
                self.table.setItem(count_row, 0, QTableWidgetItem(str(k)))
                effective_status_combo = ExtendedComboBox()
                effective_status_combo.resize(100, 50)
                effective_status_combo.addItems(["0", "1"])  # 删除状态\n(1:有效 0:删除)
                effective_status_combo.setStyleSheet("QComboBox {background:#FFFFFF;color:#FF0000;font-size:16px}")
                effective_status_combo.setCurrentText(str(v))
                self.table.setCellWidget(count_row, 1, effective_status_combo)
            else:
                self.table.setItem(count_row, 0, QTableWidgetItem(str(k)))
                # self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)  # 禁止编辑
                self.table.setItem(count_row, 1, QTableWidgetItem(str(v)))
            count_row += 1
        # 禁止全局编辑
        # self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.cell_no_edit()

    def get_base_info_in_table(self):
        """
            获取当前人物表格中的基本信息
        :return:
        """
        labels_en2zh = {
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
        temp_dict = {}
        row = 0
        for k in list(labels_en2zh.keys()):
            if k == "check_status":
                temp_dict[k] = str(int(self.check_status_) + 1)
                continue
            elif k == "effective_status":
                temp_dict[k] = self.table.cellWidget(row, 1).currentText()
            else:
                temp_dict[k] = self.table.item(row, 1).text()
            row += 1
        return temp_dict

    def update_rel_id(self, row, col, text):
        """
            实现联动，根据选定rel_name实时更新rel_id
        :param row: 行
        :param col: 列
        :param text: 当前关系名称
        :return:
        """
        self.rel_table.setItem(row, col, QTableWidgetItem(self.rel_name2id[text]))
        print("row:" + str(row) + ", col:" + str(col) + ", rel_id 更新为:" + self.rel_name2id[text])

        # self.updateCombox(combo1)

        # def updateCombox(self, combo1):
        #     # text = combo1.currentText()
        #     combo1.blockSignals(True)
        #     # combo2.blockSignals(True)
        #     # combo1.clear()
        #     # combo2.clear()

    def create_rel_info_table(self,):
        """
            创建关系表格
        :return:
        """

        self.rel_table = QTableWidget()  # 展示关系表
        # Todo 优化1 设置水平方向的表头标签
        horizontal_header_labels = list(self.labels_en2zh_rel_info.values())
        self.rel_table.setColumnCount(len(self.labels_en2zh_rel_info))
        # print(horizontal_header_labels)
        self.rel_table.setHorizontalHeaderLabels(horizontal_header_labels)
        # TODO 优化 6 表格头的显示与隐藏
        # self.table.verticalHeader().setVisible(False)
        self.rel_table.horizontalHeader().setVisible(True)
        self.rel_table.setItemDelegateForRow(0, EmptyDelegate(self))  # 设置第0行(english labels行)不可编辑

        """
           根据字段权限配置表配置字段编辑权限
           1:可编辑
           0:禁止编辑
        """
        # self.rel_table.setItemDelegateForColumn(0, EmptyDelegate(self))  # 设置0列不可编辑
        for k, v in self.rel_info_labels_auth_config.items():
            if not v:
                col_idx = self.labels_en2id_rel_info[k]
                self.rel_table.setItemDelegateForColumn(col_idx,
                                                        EmptyDelegate(self))  # 设置第col_idx列不可编辑

        self.rel_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # 所有列自动填充满屏

        # self.show_rel_info_in_table(data_list)

    @staticmethod
    def encode_rel_direction(rel_dir_id):
        """
        1:"==>",
        2:"<==",
        3:"<==>"
        :return:
        """
        if rel_dir_id == "1":
            rel_dir_id = "==>"
        elif rel_dir_id == "2":
            rel_dir_id = "<=="
        else:
            rel_dir_id = "<==>"

        return rel_dir_id

    @staticmethod
    def decode_rel_direction(rel_dir):
        """
        "==>":1,
        "<==":2,
        "<==>":3
        :return:
        """
        if rel_dir == "==>":
            rel_dir = "1"
        elif rel_dir == "<==":
            rel_dir = "2"
        else:
            rel_dir = "3"

        return rel_dir

    def rel_table_double_clicked(self, index):
        table_row = index.row()
        table_column = index.column()
        current_item = self.rel_table.item(table_row, table_column)
        curr_text = current_item.text()
        # current_widget = self.rel_table.cellWidget(table_row, table_column)
        # print("Tips: rel_table_double_clicked !\n"
        #       + "rel_table_row:" + str(table_row) + ", "
        #       + "rel_table_column:" + str(table_column))

        if table_column == self.labels_en2id_rel_info["person_1_name"]:
            print("person_1_name: " + curr_text + " 被双击！")
            person_1_id = self.rel_table.item(table_row, self.labels_en2id_rel_info["person_1_id"]).text()
            print("person_1_id: " + person_1_id)
            result = \
                self.information_ancient_base_gold.find_one({"person_id": person_1_id}, {"_id": 0})
            if result:
                result_label2en = {self.labels_en2zh_base_info[k]: v for k, v in result.items()}  # key值汉化
                result_format = json.dumps(result_label2en, ensure_ascii=False, indent=4)

                QMessageBox.information(self, "Tips", result_format, QMessageBox.Ok)
            else:
                QMessageBox.question(self, "Warning", "Sorry!　该人物暂时不在信息库中",
                                     QMessageBox.Ok)

        if table_column == self.labels_en2id_rel_info["person_2_name"]:
            print("person_2_name: " + curr_text + " 被双击！")
            person_2_id = self.rel_table.item(table_row, self.labels_en2id_rel_info["person_2_id"]).text()
            print("person_2_id: " + person_2_id)
            result = \
                self.information_ancient_base_gold.find_one({"person_id": person_2_id}, {"_id": 0})
            if result:
                result_label2en = {self.labels_en2zh_base_info[k]: v for k, v in result.items()}  # key值汉化
                result_format = json.dumps(result_label2en, ensure_ascii=False, indent=4)
                QMessageBox.information(self, "Tips", result_format,
                                        QMessageBox.Ok)
            else:
                QMessageBox.question(self, "Warning", "Sorry!　该人物暂时不在信息库中",
                                     QMessageBox.Ok)

    def show_rel_info_in_table(self, data_list):
        """
        :param data_list: type:list [{}, {}]
        :return:
        """
        data_list_u = []
        if not data_list:  # 若此任务0条关系，则赋空值。
            # data_list_u.append({la: "" for la in list(labels_en2zh.keys())})
            self.rel_table.setRowCount(0)  # 行自增
            self.rel_table.setColumnCount(len(self.labels_en2zh_rel_info))
        else:
            """
                重置数据键值对顺序
            """
            for da in data_list:
                temp = {}
                for la in list(self.labels_en2zh_rel_info.keys()):
                    temp[la] = da[la]
                data_list_u.append(temp)

            # Create table
            self.rel_table.setRowCount(len(data_list_u) + 1)  # 行自增
            self.rel_table.setColumnCount(len(self.labels_en2zh_rel_info))

            for count_row, data in enumerate(data_list_u):
                count_col = 0
                for k, v in data.items():
                    if count_row == 0:
                        new_item0 = QTableWidgetItem(str(k))
                        # new_item0.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                        self.rel_table.setItem(0, count_col, new_item0)
                        if k == "rel_name":
                            # self.rel_name_combo.setStyleSheet("QComboBox{margin:0px};")
                            # rel_name_combo.resize(100, 40)
                            """
                                添加下拉选项框，可实现模糊查询
                            """
                            rel_name_combo_1 = ExtendedComboBox(self.rel_table)
                            rel_name_combo_1.addItems(self.all_rel_list)
                            rel_name_combo_1.setStyleSheet("QComboBox {background:#FFFFFF;"
                                                           "color:#FF0000;font-size:16px \"Times\"}")
                            rel_name_combo_1.setCurrentText(str(v))
                            # rel_name_combo_1.activated.connect(lambda:
                            #                                    self.update_rel_id(1,
                            #                                                       self.labels_en2id_rel_info["rel_id"],
                            #                                                       rel_name_combo_1.currentText()))
                            self.rel_table.setCellWidget(1, count_col, rel_name_combo_1)

                        elif k == "rel_direction":
                            rel_direction_combo = ExtendedComboBox()
                            rel_direction_combo.addItems(["==>", "<==", "<==>"])  # 关系方向
                            rel_direction_combo.setStyleSheet("QComboBox {background:#FFFFFF;"
                                                              "color:#FF0000;"
                                                              "font-size:16px}")
                            rel_direction_combo.setCurrentText(self.encode_rel_direction(str(v)))
                            self.rel_table.setCellWidget(1, count_col, rel_direction_combo)

                        elif k == "effective_status":
                            effective_status_combo = ExtendedComboBox()
                            effective_status_combo.addItems(["0", "1"])  # 删除状态\n(1:有效 0:删除)
                            effective_status_combo.setStyleSheet("QComboBox {background:#FFFFFF;"
                                                                 "color:#FF0000;font-size:16px}")
                            effective_status_combo.setCurrentText(str(v))
                            self.rel_table.setCellWidget(1, count_col, effective_status_combo)

                        elif k == "person_1_name" or k == "person_2_name":
                            new_item = QTableWidgetItem(str(v))
                            new_item.setFont(QFont('Times', 16))   # 设置字体（字体，字号）
                            new_item.setForeground(QBrush(QColor(0, 0, 255)))   # 设置字体为蓝色
                            # new_item.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                            self.rel_table.setItem(1, count_col, new_item)

                        else:
                            new_item = QTableWidgetItem(str(v))
                            # new_item.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                            self.rel_table.setItem(1, count_col, new_item)

                        """
                            填充不可编辑项的底色
                        """
                        if not self.rel_info_labels_auth_config[k]:
                            self.rel_table.item(count_row + 1, count_col
                                            ).setBackground(QtGui.QColor(220, 220, 220))  # 设置英文列头对应的底色

                    else:
                        if k == "rel_name":
                            rel_name_combo_2 = ExtendedComboBox(self.rel_table)
                            # rel_name_combo_2.setProperty("row", count_row + 1)
                            # rel_name_combo_2.setProperty("col", count_col)

                            rel_name_combo_2.addItems(self.all_rel_list)
                            rel_name_combo_2.setStyleSheet("QComboBox {background:#FFFFFF;"
                                                           "color:#FF0000;font-size:16px \"Times\"}")
                            rel_name_combo_2.setCurrentText(str(v))
                            # rel_name_combo_2.activated.connect(lambda: self.update_rel_id(count_row + 1,
                            #                                                       self.labels_en2id_rel_info["rel_id"],
                            #                                                       rel_name_combo_2.currentText()))
                            # rel_name_row = count_row + 1
                            # rel_id_col = self.labels_en2id_rel_info["rel_id"]
                            # rel_name_combo_2.currentIndexChanged.connect(
                            #     lambda: self.update_rel_id(rel_name_row, rel_id_col, rel_name_combo_2.currentText()))

                            self.rel_table.setCellWidget(count_row + 1, count_col, rel_name_combo_2)

                        elif k == "rel_direction":
                            rel_direction_combo2 = ExtendedComboBox()
                            rel_direction_combo2.addItems(["==>", "<==", "<==>"])
                            rel_direction_combo2.setStyleSheet("QComboBox {background:#FFFFFF;"
                                                               "color:#FF0000;"
                                                               "font-size:16px}")
                            rel_direction_combo2.setCurrentText(self.encode_rel_direction(str(v)))
                            self.rel_table.setCellWidget(count_row + 1, count_col, rel_direction_combo2)

                        elif k == "effective_status":
                            effective_status_combo2 = ExtendedComboBox()
                            effective_status_combo2.addItems(["0", "1"])  # 删除状态\n(1:有效 0:删除)
                            effective_status_combo2.setStyleSheet("QComboBox {background:#FFFFFF;"
                                                                  "color:#FF0000;font-size:16px}")
                            effective_status_combo2.setCurrentText(str(v))
                            self.rel_table.setCellWidget(count_row + 1, count_col, effective_status_combo2)

                        elif k == "person_1_name" or k == "person_2_name":
                            new_item = QTableWidgetItem(str(v))
                            new_item.setFont(QFont('Times', 16))   # 设置字体（字体，字号）
                            new_item.setForeground(QBrush(QColor(0, 0, 255)))   # 设置字体为蓝色
                            # new_item.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                            self.rel_table.setItem(count_row + 1, count_col, new_item)

                        else:
                            self.rel_table.setItem(count_row + 1, count_col, QTableWidgetItem(str(v)))

                        """
                            填充不可编辑项的底色
                        """
                        if not self.rel_info_labels_auth_config[k]:
                            self.rel_table.item(count_row + 1, count_col
                                                ).setBackground(QtGui.QColor(220, 220, 220))  # 设置对应的底色

                    count_col += 1

        self.rel_table.doubleClicked.connect(self.rel_table_double_clicked)

    def get_rel_info_in_table(self):
        """
            获取当前人物表格中的关系信息
        :return:
        """
        rel_row_count = self.rel_table.rowCount()
        if rel_row_count == 0:
            temp_list = []
        else:
            temp_list = []
            for row_idx in range(rel_row_count):
                if row_idx == 0:
                    continue
                temp = {}

                rel_id_raw = self.rel_table.item(row_idx, self.labels_en2id_rel_info["rel_id"]).text()
                rel_id_now = self.rel_name2id[self.rel_table.cellWidget(row_idx,
                                                                        self.labels_en2id_rel_info["rel_name"]
                                                                        ).currentText()]
                for col_idx in range(self.rel_table.columnCount()):
                    if col_idx == self.labels_en2id_rel_info["effective_status"] or \
                            col_idx == self.labels_en2id_rel_info["rel_name"]:    # 获取QComboBox中的信息

                        temp[self.rel_table.item(0, col_idx).text()] = \
                            self.rel_table.cellWidget(row_idx, col_idx).currentText()

                    elif col_idx == self.labels_en2id_rel_info["rel_direction"]:
                        """
                            解码和更新关系方向
                        """
                        temp[self.rel_table.item(0, col_idx).text()] = \
                            self.decode_rel_direction(self.rel_table.cellWidget(row_idx, col_idx).currentText())

                    elif col_idx == self.labels_en2id_rel_info["rel_id"] and rel_id_raw != rel_id_now:
                        """
                            更新关系id
                        """
                        temp[self.rel_table.item(0, col_idx).text()] = rel_id_now

                    else:
                        temp[self.rel_table.item(0, col_idx).text()] = self.rel_table.item(row_idx, col_idx).text()

                temp_list.append(temp)

        return temp_list

    def create_event_info_table(self,):
        """
            创建生平表格
        :return:
        """
        # Create table
        self.event_table = QTableWidget()  # 展示生平表
        self.event_table.setColumnCount(len(self.labels_en2zh_event_info))
        # Todo 优化1 设置水平方向的表头标签
        horizontal_header_labels = list(self.labels_en2zh_event_info.values())
        self.event_table.setHorizontalHeaderLabels(horizontal_header_labels)
        # TODO 优化 6 表格头的显示与隐藏
        # self.table.verticalHeader().setVisible(False)
        self.event_table.horizontalHeader().setVisible(True)

        self.event_table.setItemDelegateForRow(0, EmptyDelegate(self))  # 设置第0行(english labels行)不可编辑
        # self.event_table.setItemDelegateForColumn(0, EmptyDelegate(self))  # 设置第一列不可编辑
        """
           根据字段权限配置表配置字段编辑权限
           1:可编辑
           0:禁止编辑
        """
        for k, v in self.event_info_labels_auth_config.items():
            if not v:
                col_idx = self.labels_en2id_event_info[k]
                self.event_table.setItemDelegateForColumn(col_idx,
                                                          EmptyDelegate(self))  # 设置第col_idx列不可编辑

        self.event_table.horizontalHeader().setSectionResizeMode(self.labels_en2id_event_info["place"],
                                                                 QHeaderView.ResizeToContents)  # place列自适应内容
        self.event_table.horizontalHeader().setSectionResizeMode(self.labels_en2id_event_info["abstract"],
                                                                 QHeaderView.ResizeToContents)  # abstract列自适应内容
        self.event_table.horizontalHeader().setSectionResizeMode(self.labels_en2id_event_info["content"],
                                                                 QHeaderView.Stretch)  # content列自动填充满屏

    def show_event_info_in_table(self, data_list):
        """
        :param data_list: type:list [{}, {}]
        :return:
        """

        """
            重置数据键值对顺序
        """
        data_list_u = []
        if not data_list:  # 若此任务0条关系，则赋空值。
            # self.event_table = QTableWidget()  # 展示关系表
            self.event_table.setRowCount(0)  # 行自增
        else:
            self.event_table.setRowCount(len(data_list) + 1)  # 行自增

            for da in data_list:
                temp = {}
                for la in list(self.labels_en2zh_event_info.keys()):
                    temp[la] = da[la]
                data_list_u.append(temp)

            count_row = 0
            for data in data_list_u:
                count_col = 0
                for k, v in data.items():
                    if count_row == 0:
                        self.event_table.setItem(0, count_col, QTableWidgetItem(str(k)))
                        # self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)  # 禁止编辑
                        self.event_table.setRowHeight(1, 65)  # 设置行高为65
                        if k == "event_weight":
                            event_weight_combo = ExtendedComboBox()
                            event_weight_combo.addItems(["1", "2", "3", "4", "5"])  # event_weight
                            event_weight_combo.setCurrentText(str(v))
                            self.event_table.setCellWidget(1, count_col, event_weight_combo)

                        elif k == "effective_status":
                            effective_status_combo = ExtendedComboBox()
                            effective_status_combo.addItems(["0", "1"])  # 删除状态\n(1:有效 0:删除)
                            effective_status_combo.setCurrentText(str(v))
                            self.event_table.setCellWidget(1, count_col, effective_status_combo)
                        else:
                            self.event_table.setItem(1, count_col, QTableWidgetItem(str(v)))

                        """
                            填充不可编辑项的底色
                        """
                        if not self.event_info_labels_auth_config[k]:
                            self.event_table.item(count_row + 1, count_col
                                                ).setBackground(QtGui.QColor(220, 220, 220))  # 设置对应的底色
                    else:
                        self.event_table.setRowHeight(count_row + 1, 65)  # 设置行高为65
                        if k == "event_weight":
                            event_weight_combo = ExtendedComboBox()
                            event_weight_combo.addItems(["1", "2", "3", "4", "5"])  # event_weight
                            event_weight_combo.setCurrentText(str(v))
                            self.event_table.setCellWidget(count_row + 1, count_col, event_weight_combo)
                        elif k == "effective_status":
                            effective_status_combo = ExtendedComboBox()
                            effective_status_combo.addItems(["0", "1"])  # 删除状态\n(1:有效 0:删除)
                            effective_status_combo.setCurrentText(str(v))
                            self.event_table.setCellWidget(count_row + 1, count_col, effective_status_combo)
                        else:
                            self.event_table.setItem(count_row + 1, count_col, QTableWidgetItem(str(v)))

                        """
                            填充不可编辑项的底色
                        """
                        if not self.event_info_labels_auth_config[k]:
                            self.event_table.item(count_row + 1, count_col
                                                  ).setBackground(QtGui.QColor(220, 220, 220))  # 设置对应的底色
                    count_col += 1
                count_row += 1

    def get_event_info_in_table(self):
        """
            获取当前人物表格中的生平信息
        :return:
        """
        event_row_count = self.event_table.rowCount()
        if event_row_count == 0:
            temp_list = []
        else:
            temp_list = []
            for row_idx in range(event_row_count):
                if row_idx == 0:
                    continue
                temp = {}
                for col_idx in range(self.event_table.columnCount()):
                    if col_idx == self.labels_en2id_event_info["event_weight"] or \
                            col_idx == self.labels_en2id_event_info["effective_status"]:    # 获取QComboBox中的信息
                        temp[self.event_table.item(0, col_idx).text()] = \
                            self.event_table.cellWidget(row_idx, col_idx).currentText()
                        pass
                    else:
                        temp[self.event_table.item(0, col_idx).text()] = \
                            self.event_table.item(row_idx, col_idx).text()
                temp_list.append(temp)
        return temp_list

    @pyqtSlot()
    def button1_on_click(self):
        self.index = self.index - 1
        self.page_up_flag = True
        print('\"' + "上一页" + '\"' + "被点击")
        # self.table.clear()

        if self.index < 0:
            self.button1.setEnabled(False)
            buttonReply = QMessageBox.question(self, 'Warning', "已经回到首页！", QMessageBox.Ok)
            if buttonReply == QMessageBox.Ok:
                print("已经回到首页，点击OK继续校对")
                self.index = 0

        """
            show base_info
        """
        if self.person_id_prcessed_current_list:
            self.show_base_info_in_table(self.my_order_dict[self.person_id_prcessed_current_list[self.index]])

    @pyqtSlot()
    def button2_on_click(self):
        self.button1.setEnabled(True)
        print('\"' + "下一页" + '\"' + "被点击")
        # if not self.FLAG_3_tables_check_finished:
        #     reply_FLAG_3_tables_check_finished = QMessageBox.question(self, 'Warning',
        #                                                               "关系表和生平表还没有校验！", QMessageBox.Ok)
        #     if reply_FLAG_3_tables_check_finished == QMessageBox.Ok:
        #         print("reply_FLAG_3_tables_check_finished点击了Ok")
        # else:
        curr_tab_base_info = self.get_base_info_in_table()  # 获取当前表格中的基本信息
        self.person_id = str(curr_tab_base_info["person_id"])

        if self.page_up_flag:  # 当上一页被点击后执行
            self.auto_save_base_info()  # 自动检测并提示是否保存修改
            if self.FLAG_ALL_RIGHT:
                self.index += 1
                if self.index != len(self.person_id_prcessed_current_list):
                    self.show_base_info_in_table(self.my_order_dict[
                                                     self.person_id_prcessed_current_list[self.index]])
                else:
                    self.show_base_info_in_table(self.find_one_base_info_in_temp1)
                    self.page_up_flag = False
        else:
            if self.FLAG_3_tables_check_finished:
                curr_tab_rel_info = self.get_rel_info_in_table()  # 获取当前表格中的关系信息
                print("len(curr_tab_rel_info)" + str(len(curr_tab_rel_info)))
                curr_tab_event_info = self.get_event_info_in_table()  # 获取当前表格中的生平信息
                print("len(curr_tab_event_info)" + str(len(curr_tab_event_info)))
            else:
                curr_tab_rel_info = self.query_rel_info(self.person_id)  # 1库中获取
                curr_tab_event_info = self.query_event_info(self.person_id)  # 1库中获取
                print("self.FLAG_3_tables_check_finished == False")

            self.person_id_prcessed_list = \
                [str(x["person_id"]) for x in self.information_ancient_base_temp2.find({}, {"person_id": 1})]
            curr_tab_base_info_copy = copy.deepcopy(curr_tab_base_info)

            """
                数据格式、逻辑校验
            """

            self.FLAG_ALL_RIGHT = self.data_format_check(curr_tab_base_info_copy)

            if self.FLAG_ALL_RIGHT:
                if str(self.person_id) not in self.person_id_prcessed_list:
                    # print(json.dumps(temp_dict, ensure_ascii=False, indent=2))
                    curr_tab_base_info_copy["check_author"] = self.job_num_  # 加入工号
                    self.information_ancient_base_temp2.insert_one(curr_tab_base_info_copy)
                    print("中间库（历史组）######" + self.col_base_info_temp2_ + "######插入一条新数据####person_id: "
                          + self.person_id)
                    self.information_ancient_base_temp1.update_one({"person_id": self.person_id},
                                                                   {"$set": {"check_status":
                                                                             str(int(self.check_status_) + 1)}})
                    print("初版库（AI）####" + self.col_base_info_temp1_ + "####person_id: " + self.person_id + " "
                          + '\"' + "check_status" + '\"' + "更新为: " + str(int(self.check_status_) + 1))

                    print("保存（base_info）到self.my_order_dict")
                    self.my_order_dict[self.person_id] = curr_tab_base_info   # 存放基本信息

                    """
                        保存当前人物关系数据
                    """
                    if curr_tab_rel_info:   # 若为空，skip
                        self.information_ancient_relation_temp2.insert_many(curr_tab_rel_info)
                        print("中间库（历史组）######" + self.col_rel_info_temp2_ + "######插入一条新数据####person_id: "
                              + self.person_id)
                        self.information_ancient_relation_temp1.update_many({"person_1_id": self.person_id},
                                                                            {"$set":
                                                                            {"check_status":
                                                                             str(int(self.check_status_) + 1)}})

                        print("初版库（AI）####" + self.col_rel_info_temp1_ + "####person_id: " + self.person_id + " "
                              + '\"' + "check_status" + '\"' + "更新为: " + str(int(self.check_status_) + 1))
                    print("保存（rel_info）到self.my_event_info_order_dict")
                    self.my_rel_info_order_dict[self.person_id] = curr_tab_rel_info

                    """
                        保存当前人物生平数据
                    """
                    if curr_tab_event_info:  # 若为空，skip
                        self.information_ancient_event_temp2.insert_many(curr_tab_event_info)
                        print("中间库（历史组）######" + self.col_event_info_temp2_ + "######插入一条新数据####person_id: "
                              + self.person_id)
                        self.information_ancient_event_temp1.update_many({"person_1_id": self.person_id},
                                                                         {"$set": {"check_status": str(
                                                                                    int(self.check_status_) + 1)}})

                        print("初版库（AI）####" + self.col_event_info_temp1_ + "####person_id: " + self.person_id + " "
                              + '\"' + "check_status" + '\"' + "更新为: " + str(int(self.check_status_) + 1))
                    print("保存（event_info）到self.my_event_info_order_dict")
                    self.my_event_info_order_dict[self.person_id] = curr_tab_event_info

                    self.person_id_prcessed_current_list.append(self.person_id)
                    self.index += 1
                    self.query_base_info()
                    self.show_base_info_in_table(self.find_one_base_info_in_temp1)
                else:
                    # print('\"' + "person_id: " + str(curr_tab_base_info["person_id"]) + " "
                    #       + "已存在" + self.col_base_info_temp2_ + "中")
                    print('\"' + "person_id: " + str(self.person_id) + " "
                          + "已存在" + self.col_base_info_temp2_ + "中")
                    if str(curr_tab_base_info["person_id"]) not in self.my_order_dict:
                        print(str(curr_tab_base_info["person_id"]) + "不在self.my_order_dict中")
                    # 一般认为同一个人物不能同时被两个人同时编辑，# 默认不会被触发，若出现则self.auto_save_base_info()对库中信息覆盖
                    self.auto_save_base_info()  # 自动保存更新的信息
                    if self.FLAG_ALL_RIGHT:
                        self.query_base_info()
                        self.show_base_info_in_table(self.find_one_base_info_in_temp1)

            """
                一个人物结束后，初始化相关变量
            """
        self.FLAG_3_tables_check_finished = False

    @pyqtSlot()
    def button3_on_click(self):
        print('\"' + "退出" + '\"' + "被点击")
        # temp_dict = {}
        # count_row_temp = 0
        # for k, v in self.find_one_base_info_in_temp1.items():
        #     if k == "check_status":
        #         temp_dict[k] = str(int(self.check_status_) + 1)
        #         continue
        #     temp_dict[k] = self.table.item(count_row_temp, 1).text()
        #     count_row_temp += 1
        curr_tab_base_info = self.get_base_info_in_table()  # 获取当前表格中的基本信息
        self.person_id = str(curr_tab_base_info["person_id"])
        if self.FLAG_3_tables_check_finished:
            curr_tab_rel_info = self.get_rel_info_in_table()  # 获取当前表格中的关系信息
            curr_tab_event_info = self.get_event_info_in_table()  # 获取当前表格中的生平信息
        else:
            curr_tab_rel_info = self.query_rel_info(self.person_id)  # 1库中获取
            curr_tab_event_info = self.query_event_info(self.person_id)  # 1库中获取

        button_reply1 = QMessageBox.question(self, 'Warning', "是否保存当前数据?", QMessageBox.Yes, QMessageBox.No)
        if button_reply1 == QMessageBox.Yes:
            if self.page_up_flag:
                self.auto_save_base_info()
                if self.FLAG_ALL_RIGHT:
                    print("退出时，" + "中间库（历史组）######" + self.col_base_info_temp2_ +
                          "完成了一条数据的修改保存####person_id: " + self.table.item(0, 1).text())

            else:
                self.person_id_prcessed_list = \
                    [str(x["person_id"]) for x in self.information_ancient_base_temp2.find({}, {"person_id": 1})]
                curr_tab_base_info_copy = copy.deepcopy(curr_tab_base_info)

                """
                    数据格式、逻辑校验
                """

                self.FLAG_ALL_RIGHT = self.data_format_check(curr_tab_base_info_copy)

                if self.FLAG_ALL_RIGHT:
                    curr_tab_base_info_copy["check_author"] = self.job_num_  # 加入工号
                    if str(self.person_id) not in self.person_id_prcessed_list:
                        self.information_ancient_base_temp2.insert_one(curr_tab_base_info_copy)
                        print("中间库（历史组）######" + self.col_base_info_temp2_ + "######插入一条新数据####person_id: "
                              + self.person_id)
                        self.information_ancient_base_temp1.update_one({"person_id": self.person_id},
                                                                       {"$set": {"check_status":
                                                                                 str(int(self.check_status_) + 1)}})
                        print("初版库（AI）####" + self.col_base_info_temp1_ + "####person_id: " + self.person_id + " "
                              + '\"' + "check_status" + '\"' + "更新为: " + str(int(self.check_status_) + 1))

                        print("保存（base_info）到self.my_order_dict")
                        self.my_order_dict[self.person_id] = curr_tab_base_info  # 存放基本信息

                        """
                            保存当前人物关系数据
                        """
                        if curr_tab_rel_info:    # 若为空，skip
                            self.information_ancient_relation_temp2.insert_many(curr_tab_rel_info)
                            print("中间库（历史组）######" + self.col_rel_info_temp2_ + "######插入一条新数据####person_id: "
                                  + self.person_id)
                            self.information_ancient_relation_temp1.update_many({"person_1_id": self.person_id},
                                                                                {"$set":
                                                                                    {"check_status": str(
                                                                                        int(self.check_status_) + 1)}})

                            print("初版库（AI）####" + self.col_rel_info_temp1_ + "####person_id: " + self.person_id + " "
                                  + '\"' + "check_status" + '\"' + "更新为: " + str(int(self.check_status_) + 1))
                        print("保存（rel_info）到self.my_event_info_order_dict")
                        self.my_rel_info_order_dict[self.person_id] = curr_tab_rel_info

                        """
                            保存当前人物生平数据
                        """
                        if curr_tab_event_info:    # 若为空，skip
                            self.information_ancient_event_temp2.insert_many(curr_tab_event_info)
                            print("中间库（历史组）######" + self.col_event_info_temp2_ + "######插入一条新数据####person_id: "
                                  + self.person_id)
                            self.information_ancient_event_temp1.update_many({"person_1_id": self.person_id},
                                                                             {"$set": {"check_status": str(
                                                                                 int(self.check_status_) + 1)}})

                            print("初版库（AI）####" + self.col_event_info_temp1_ + "####person_id: " + self.person_id + " "
                                  + '\"' + "check_status" + '\"' + "更新为: " + str(int(self.check_status_) + 1))
                        print("保存（event_info）到self.my_event_info_order_dict")
                        self.my_event_info_order_dict[self.person_id] = curr_tab_event_info

                        self.person_id_prcessed_current_list.append(self.person_id)
                        self.index += 1
                    else:
                        print("更新（base_info）在self.my_order_dict")
                        self.my_order_dict[curr_tab_base_info[self.person_id]] = curr_tab_base_info
                        print("更新（rel_info）在self.my_event_info_order_dict")
                        self.my_rel_info_order_dict[self.person_id] = curr_tab_rel_info
                        print("更新（event_info）到self.my_event_info_order_dict")
                        self.my_event_info_order_dict[self.person_id] = curr_tab_event_info

        else:
            self.information_ancient_base_temp1.update_one({"person_id": self.person_id},
                                                           {"$set": {
                                                               "check_status": str(self.check_status_)}})
            print("退出时，没有保存当前数据，初版库（AI）####" + self.col_base_info_temp1_ +
                  "####person_id: " + self.person_id + " "
                  + '\"' + "check_status" + '\"' + "更新为: " + str(self.check_status_))

            self.information_ancient_relation_temp1.update_many({"person_id": self.person_id},
                                                                {"$set": {
                                                                   "check_status": str(self.check_status_)}})
            print("退出时，没有保存当前数据，初版库（AI）####" + self.col_rel_info_temp1_ +
                  "####person_id: " + self.person_id + " "
                  + '\"' + "check_status" + '\"' + "更新为: " + str(self.check_status_))

            self.information_ancient_event_temp1.update_many({"person_id": self.person_id},
                                                             {"$set": {
                                                              "check_status": str(self.check_status_)}})
            print("退出时，没有保存当前数据，初版库（AI）####" + self.col_event_info_temp1_ +
                  "####person_id: " + self.person_id + " "
                  + '\"' + "check_status" + '\"' + "更新为: " + str(self.check_status_))

        button_reply2 = QMessageBox.question(self, 'Warning', "确认退出?", QMessageBox.Yes, QMessageBox.No)
        if button_reply2 == QMessageBox.Yes:
            # print("Yeah")
            if button_reply1 == QMessageBox.Yes:
                print("保存了当前的数据，且退出！")
            elif button_reply1 == QMessageBox.No:
                print("没有保存当前数据，且退出！")
            """
                生成比对报告
            """
            self.close()
        else:
            if button_reply1 == QMessageBox.Yes:
                print("保存了当前的数据，且取消退出！")
            elif button_reply1 == QMessageBox.No:
                print("没有保存当前数据，且取消退出！")

    @pyqtSlot()
    def trans_tables_button_on_click(self):
        """
            点击切换为关系表/生平表/基本信息表
        :return:
        """
        current_person_id = self.table.item(0, 1).text()
        print("current_person_id: " + current_person_id)

        if self.check_mode == "基本信息+关系":    # 只在base_info和rel_info之间切换
            if self.FLAG_Current_Table == "base_info":
                print('\"' + "trans_tables_button" + '\"' + "按钮被点击")
                print("当前表：" + self.FLAG_Current_Table)
                print("保存临时回话（base_info）")

                self.my_order_dict[
                    current_person_id] = self.get_base_info_in_table()  # 获取当前基本信息表格中数据，更新self.my_order_dict

                self.create_rel_info_table()
                if current_person_id in self.my_rel_info_order_dict:
                    self.show_rel_info_in_table(self.my_rel_info_order_dict[current_person_id])
                    # print(json.dumps(self.my_rel_info_order_dict[current_person_id], ensure_ascii=False, indent=4))
                    # json.dump(self.my_rel_info_order_dict, rel_file, ensure_ascii=False, indent=4)
                    print("current_person_id:" + current_person_id + "存在self.my_rel_info_order_dict")
                else:
                    self.query_rel_info(current_person_id)
                    print("query 新人物关系")
                    rel_temp = self.find_rel_info_in_temp1
                    if rel_temp:
                        self.show_rel_info_in_table(rel_temp)
                    else:
                        self.show_rel_info_in_table([])
                """
                    此处self.table_layout.replaceWidget替换为关系表
                """
                self.table_layout.replaceWidget(self.table, self.rel_table)
                self.FLAG_Current_Table = "relation"
                print("切换为表：" + self.FLAG_Current_Table)
                self.button1.setEnabled(False)  # 锁死"上一页"按钮
                self.button2.setEnabled(False)  # 锁死"下一页"按钮
                self.button3.setEnabled(False)  # 锁死"退出"按钮

            elif self.FLAG_Current_Table == "relation":
                print('\"' + "trans_tables_button" + '\"' + "按钮被点击")
                print("当前表：" + self.FLAG_Current_Table)
                print("保存临时回话（rel_info）")
                self.my_rel_info_order_dict[current_person_id] = self.get_rel_info_in_table()
                # 获取当前关系信息表格中数据，更新self.my_rel_info_order_dict

                """
                    此处self.table_layout.replaceWidget替换为基本信息表
                """
                self.create_base_info_table()  # 创建一个新的base_info表，以便成功替换
                if current_person_id in self.my_order_dict:
                    self.show_base_info_in_table(self.my_order_dict[current_person_id])
                else:
                    print("Error! person_id:" + current_person_id + "不存在self.my_order_dict")

                self.table_layout.replaceWidget(self.rel_table, self.table)
                self.FLAG_Current_Table = "base_info"
                print("切换为表：" + self.FLAG_Current_Table)
                self.button1.setEnabled(True)  # 释放"上一页"按钮
                self.button2.setEnabled(True)  # 释放"下一页"按钮
                self.button3.setEnabled(True)  # 释放"退出"按钮
                self.FLAG_3_tables_check_finished = True  # 3表完成切换，即视为此人物校验完成，下一页按钮可安全点击，否则触发警告！

        elif self.check_mode == "基本信息+生平":
            if self.FLAG_Current_Table == "base_info":
                print('\"' + "trans_tables_button" + '\"' + "按钮被点击")
                print("当前表：" + self.FLAG_Current_Table)
                print("保存临时回话（base_info）")

                self.my_order_dict[current_person_id] = self.get_base_info_in_table()  # 获取当前基本信息表格中数据，更新self.my_order_dict

                self.create_event_info_table()
                if current_person_id in self.my_event_info_order_dict:
                    self.show_event_info_in_table(self.my_event_info_order_dict[current_person_id])
                    print("person_id:" + current_person_id + "存在self.my_event_info_order_dict")
                else:
                    self.query_event_info(current_person_id)
                    event_temp = self.find_event_info_in_temp1
                    if event_temp:
                        self.show_event_info_in_table(event_temp)
                    else:
                        self.show_event_info_in_table([])
                """
                    此处self.table_layout.replaceWidget替换为生平表
                """
                self.table_layout.replaceWidget(self.table, self.event_table)
                self.FLAG_Current_Table = "event"
                print("切换为表：" + self.FLAG_Current_Table)
                self.button1.setEnabled(False)
                self.button2.setEnabled(False)
                self.button3.setEnabled(False)  # 锁死"退出"按钮

            elif self.FLAG_Current_Table == "event":
                print('\"' + "trans_tables_button" + '\"' + "按钮被点击")
                print("当前表：" + self.FLAG_Current_Table)
                print("保存临时回话（event）")
                self.my_event_info_order_dict[current_person_id] = self.get_event_info_in_table()
                # 获取当前生平信息表格中数据，更新self.my_event_info_order_dict

                """
                    此处self.table_layout.replaceWidget替换为基本信息表
                """
                self.create_base_info_table()  # 创建一个新的base_info表，以便成功替换
                if current_person_id in self.my_order_dict:
                    self.show_base_info_in_table(self.my_order_dict[current_person_id])
                else:
                    print("Error! person_id:" + current_person_id + "不存在self.my_order_dict")

                self.table_layout.replaceWidget(self.event_table, self.table)
                self.FLAG_Current_Table = "base_info"
                print("切换为表：" + self.FLAG_Current_Table)
                self.button1.setEnabled(True)    # 释放"上一页"按钮
                self.button2.setEnabled(True)   # 释放"下一页"按钮
                self.button3.setEnabled(True)  # 释放"退出"按钮
                self.FLAG_3_tables_check_finished = True    # 3表完成切换，即视为此人物校验完成，下一页按钮可安全点击，否则触发警告！

        elif self.check_mode == "基本信息+关系+生平":
            if self.FLAG_Current_Table == "base_info":
                print('\"' + "trans_tables_button" + '\"' + "按钮被点击")
                print("当前表：" + self.FLAG_Current_Table)
                print("保存临时回话（base_info）")

                self.my_order_dict[current_person_id] = self.get_base_info_in_table()  # 获取当前基本信息表格中数据，更新self.my_order_dict

                self.create_rel_info_table()
                if current_person_id in self.my_rel_info_order_dict:
                    self.show_rel_info_in_table(self.my_rel_info_order_dict[current_person_id])
                    # print(json.dumps(self.my_rel_info_order_dict[current_person_id], ensure_ascii=False, indent=4))
                    # json.dump(self.my_rel_info_order_dict, rel_file, ensure_ascii=False, indent=4)
                    print("current_person_id:" + current_person_id + "存在self.my_rel_info_order_dict")
                else:
                    self.query_rel_info(current_person_id)
                    print("query 新人物关系")
                    rel_temp = self.find_rel_info_in_temp1
                    if rel_temp:
                        self.show_rel_info_in_table(rel_temp)
                    else:
                        self.show_rel_info_in_table([])
                """
                    此处self.table_layout.replaceWidget替换为关系表
                """
                self.table_layout.replaceWidget(self.table, self.rel_table)
                self.FLAG_Current_Table = "relation"
                print("切换为表：" + self.FLAG_Current_Table)
                self.button1.setEnabled(False)  # 锁死"上一页"按钮
                self.button2.setEnabled(False)  # 锁死"下一页"按钮
                self.button3.setEnabled(False)  # 锁死"退出"按钮

            elif self.FLAG_Current_Table == "relation":
                print('\"' + "trans_tables_button" + '\"' + "按钮被点击")
                print("当前表：" + self.FLAG_Current_Table)
                print("保存临时回话（rel_info）")
                self.my_rel_info_order_dict[current_person_id] = self.get_rel_info_in_table()
                # 获取当前关系信息表格中数据，更新self.my_rel_info_order_dict

                self.create_event_info_table()
                if current_person_id in self.my_event_info_order_dict:
                    self.show_event_info_in_table(self.my_event_info_order_dict[current_person_id])
                    print("person_id:" + current_person_id + "存在self.my_event_info_order_dict")
                else:
                    self.query_event_info(current_person_id)
                    event_temp = self.find_event_info_in_temp1
                    if event_temp:
                        self.show_event_info_in_table(event_temp)
                    else:
                        self.show_event_info_in_table([])
                """
                    此处self.table_layout.replaceWidget替换为生平表
                """
                self.table_layout.replaceWidget(self.rel_table, self.event_table)
                self.FLAG_Current_Table = "event"
                print("切换为表：" + self.FLAG_Current_Table)
                self.button1.setEnabled(False)
                self.button2.setEnabled(False)
                self.button3.setEnabled(False)  # 锁死"退出"按钮

            elif self.FLAG_Current_Table == "event":
                print('\"' + "trans_tables_button" + '\"' + "按钮被点击")
                print("当前表：" + self.FLAG_Current_Table)
                print("保存临时回话（event）")
                self.my_event_info_order_dict[current_person_id] = self.get_event_info_in_table()
                # 获取当前生平信息表格中数据，更新self.my_event_info_order_dict

                """
                    此处self.table_layout.replaceWidget替换为基本信息表
                """
                self.create_base_info_table()  # 创建一个新的base_info表，以便成功替换
                if current_person_id in self.my_order_dict:
                    self.show_base_info_in_table(self.my_order_dict[current_person_id])
                else:
                    print("Error! person_id:" + current_person_id + "不存在self.my_order_dict")

                self.table_layout.replaceWidget(self.event_table, self.table)
                self.FLAG_Current_Table = "base_info"
                print("切换为表：" + self.FLAG_Current_Table)
                self.button1.setEnabled(True)    # 释放"上一页"按钮
                self.button2.setEnabled(True)   # 释放"下一页"按钮
                self.button3.setEnabled(True)  # 释放"退出"按钮
                self.FLAG_3_tables_check_finished = True    # 3表完成切换，即视为此人物校验完成，下一页按钮可安全点击，否则触发警告！

    @pyqtSlot()
    def ser_person_info_button_on_click(self):
        print("点击了 自定义人物检索 按钮")

        self.searcher.show()
        # subprocess.call("python person_search.py", shell=True)

    def auto_save_base_info(self):
        """
            当内容发生改动后自动检测并提示用户是否覆盖
        :return:
        """
        curr_tab_base_info = self.get_base_info_in_table()
        person_id = curr_tab_base_info["person_id"]
        curr_tab_rel_info = self.get_rel_info_in_table()  # 获取当前表格中的关系信息
        curr_tab_event_info = self.get_event_info_in_table()  # 获取当前表格中的生平信息
        self.person_id_prcessed_list = [str(x["person_id"]) for x
                                        in self.information_ancient_base_temp2.find({}, {"person_id": 1})]
        curr_tab_base_info_copy = copy.deepcopy(curr_tab_base_info)
        # data_raw_flag = copy.deepcopy(self.my_order_dict[temp_dict_update["person_id"]])
        # data_raw_flag.pop("check_status")
        # temp_dict_update.pop("check_status")

        """
          数据格式、逻辑校验
        """

        self.FLAG_ALL_RIGHT = self.data_format_check(curr_tab_base_info)

        if self.FLAG_ALL_RIGHT:
            # if temp_dict_update != data_raw_flag:
            #     buttonReply_temp_b4 = QMessageBox.question(self, 'Waring', "确定修改？", QMessageBox.Yes, QMessageBox.No)
            #     if buttonReply_temp_b4 == QMessageBox.Yes:
                    # print(json.dumps(temp_dict_update, ensure_ascii=False, indent=2))
            if person_id in self.person_id_prcessed_list:
                self.information_ancient_base_temp2.update_one({"person_id": person_id},
                                                               {"$set": curr_tab_base_info})
                self.my_order_dict[person_id].update(curr_tab_base_info)
                # print(self.col_base_info_temp2_ + " " + "完成一条临时数据的修改！ " +
                #       "person_id: " + person_id)

                if curr_tab_rel_info:
                    self.my_rel_info_order_dict[person_id] = curr_tab_rel_info

                    for rel in curr_tab_rel_info:
                        rel_infor_id = rel["rel_infor_id"]
                        self.information_ancient_relation_temp2.update_one({"rel_infor_id": rel_infor_id},
                                                                           {"$set": rel})
                        # print(self.col_rel_info_temp2_ + " " + "完成一条临时数据的修改！ " +
                        #       "rel_infor_id: " + str(rel_infor_id))

                if curr_tab_event_info:
                    self.my_event_info_order_dict[person_id] = curr_tab_event_info

                    for event in curr_tab_event_info:
                        event_id = event["event_id"]
                        self.information_ancient_event_temp2.update_one({"event_id": event_id},
                                                                        {"$set": event})
                        print(self.col_event_info_temp2_ + " " + "完成一条临时数据的修改！ " +
                              "event_id: " + event_id)
            else:
                print("ERROR!" + " person_id: " + person_id + "不在"
                      + self.col_base_info_temp2_)

                # else:
                #     # self.close()
                #     print("已取消当前数据修改")

    def auto_save_rel_info(self):
        """
           当内容发生改动后自动检测并提示用户是否覆盖
       :return:
       """
        pass

    def auto_save_event_info(self):
        """
           当内容发生改动后自动检测并提示用户是否覆盖
       :return:
       """
        pass

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


if __name__ == '__main__':
    Job_num = ""
    Mongodb_ip = "192.168.1.23"
    Port = "27017"
    Mongodb_name = "earth_gis"
    Col_base_info_temp1 = "Information_ancient_base_temp1"
    Col_base_info_temp2 = "Information_ancient_base_temp2"
    Col_base_info_final = "Information_ancient_base"
    Col_rel_info_temp1 = "Information_ancient_relation_temp1"
    Col_rel_info_temp2 = "Information_ancient_relation_temp2"
    Col_rel_info_final = "Information_ancient_relation"
    Col_event_info_temp1 = "Information_ancient_event_temp1"
    Col_event_info_temp2 = "Information_ancient_event_temp2"
    Col_event_info_final = "Information_ancient_event"
    Check_status = "0"
    Mongodb_name_logs = "information_update_logs"
    Col_base_info_logs = "information_ancient_base_log"
    Col_rel_info_logs = "information_ancient_relation_log"
    Col_event_info_logs = "information_ancient_event_log"

    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon('icon.ico'))

    searcher = Person_Search()
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
                   col_base_info_logs=Col_base_info_logs,
                   col_rel_info_logs=Col_rel_info_logs,
                   col_event_info_logs=Col_event_info_logs,
                   search_engine=searcher)

    login_app = App_Login(job_num=Job_num, mongodb_ip=Mongodb_ip, port=Port,
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
                          col_base_info_logs=Col_base_info_logs,
                          col_rel_info_logs=Col_rel_info_logs,
                          col_event_info_logs=Col_event_info_logs,
                          main_win=main_app)

    sys.exit(app.exec_())

