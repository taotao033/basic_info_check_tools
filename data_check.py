import re


class data_check:
    """
    文本格式、类型检查
    """

    def __init__(self, data_dict_):
        self.data_dict = data_dict_
        self.flag_format_birth_date = False
        self.flag_format_death_date = False
        self.flag_value_birth_year = False  # 出生时间的年份限制
        self.flag_value_birth_month = False  # 出生时间的月份限制
        self.flag_value_birth_day = False   # 出生时间的日限制
        self.flag_value_death_year = False  # 去世时间的年份限制
        self.flag_value_death_month = False  # 去世时间的月份限制
        self.flag_value_death_day = False   # 去世时间的日限制
        self.flag_format_person_weight_id = False
        self.flag_format_person_category_id = False
        self.flag_age_greater_than_100 = False  # 年龄大于100的标记
        self.flag_age_less_than_0 = False  # 年龄小于0的标记，即出生、死亡日期不符合逻辑
        self.flag_age_greater_than_0_and_less_than_10 = False  # 年龄在0到10之间
        self.flag_age_diff_greater_than_2 = False  # 根据死亡时间与出生时间得出的年龄与实际给出的age字段值相差大于2的
        self.flag_age_noexist = False  # 有出生和死亡时间但age为空

        self.flag_is_digital_age = False  # 数字类型检测
        self.flag_is_digital_weight_id = False
        self.flag_is_digital_category_id = False

        self.flag_introduction_noexist = False  # 简介空值检测
        self.flag_all_name_noexist = False  # 姓名空值检测

        self.time_of_birth = self.data_dict["time_of_birth"]
        self.time_of_death = self.data_dict["time_of_death"]
        self.introduction = self.data_dict["introduction"]
        self.all_name = self.data_dict["all_name"]

    def is_digital_age(self, ):
        """
        :param age: 数字检测
        :return:
        """
        if self.data_dict["age"]:
            age = str(self.data_dict["age"])
            # if age.startswith("-"):
            #     self.flag_is_digital_age = True
            # else:
            age_sub = re.sub(r'\d', "", age)  # \d匹配任意数字，将其替换为空
            if age_sub:
                self.flag_is_digital_age = True

        return self.flag_is_digital_age

    def is_digital_weight_id(self, weight_id="1"):
        """
        :param weight_id: 数字检测
        :return:
        """
        weight_id = str(self.data_dict["person_weight_id"])
        weight_id_sub = re.sub(r'\d', "", weight_id)  # \d匹配任意数字，将其替换为空
        if weight_id_sub:
            self.flag_is_digital_weight_id = True
        return self.flag_is_digital_weight_id

    def is_digital_category_id(self, category_id="2"):
        """
        :param category_id: 数字检测
        :return:
        """
        category_id = str(self.data_dict["person_category_id"])
        category_id_sub = re.sub(r'\d', "", category_id)  # \d匹配任意数字，将其替换为空
        if category_id_sub:
            self.flag_is_digital_category_id = True
        return self.flag_is_digital_category_id

    def format_check_birth_date(self):
        """
            出生日期格式检查
        :return:
        """
        if self.time_of_birth:
            time_of_birth = self.time_of_birth.replace("-", "")
            time_of_birth_sub = re.sub(r'\d', "", time_of_birth)  # \d匹配任意数字，将其替换为空
            if time_of_birth_sub:
                self.flag_format_birth_date = True
                print("出生日期时间格式错误")
            else:
                find_split_list = re.findall("-", self.time_of_birth)
                if len(find_split_list) != 2 and len(find_split_list) != 3:
                    self.flag_format_birth_date = True
                    print("出生日期时间格式错误")
                else:
                    date_split = self.time_of_birth.split("-")
                    date_len = len(date_split)
                    if date_len == 4:
                        year = date_split[1]
                        mon = date_split[2]
                        day = date_split[3]
                        if len(mon) != 2 or len(day) != 2 or len(year) == 0:
                            print("出生日期时间格式错误")
                            self.flag_format_birth_date = True
                    elif date_len == 3:
                        year = date_split[0]
                        mon = date_split[1]
                        day = date_split[2]
                        if len(mon) != 2 or len(day) != 2 or len(year) == 0:
                            print("出生日期时间格式错误")
                            self.flag_format_birth_date = True
                    else:
                        print("出生日期时间格式错误")
                        self.flag_format_birth_date = True

        return self.flag_format_birth_date

    def format_check_death_date(self):
        """
            死亡日期格式检查
        :return:
        """
        if self.time_of_death:
            time_of_death = self.time_of_death.replace("-", "")
            time_of_death_sub = re.sub(r'\d', "", time_of_death)  # \d匹配任意数字，将其替换为空
            if time_of_death_sub:
                self.flag_format_death_date = True
                print("死亡日期时间格式错误")
            else:
                find_split_list = re.findall("-", self.time_of_death)
                if len(find_split_list) != 2 and len(find_split_list) != 3:
                    self.flag_format_death_date = True
                    print("死亡日期时间格式错误")
                else:
                    date_split = self.time_of_death.split("-")
                    date_len = len(date_split)
                    if date_len == 4:
                        year = date_split[1]
                        mon = date_split[2]
                        day = date_split[3]
                        if len(mon) != 2 or len(day) != 2 or len(year) == 0:
                            print("死亡日期时间格式错误")
                            self.flag_format_death_date = True
                    elif date_len == 3:
                        year = date_split[0]
                        mon = date_split[1]
                        day = date_split[2]
                        if len(mon) != 2 or len(day) != 2 or len(year) == 0:
                            print("死亡日期时间格式错误")
                            self.flag_format_death_date = True
                    else:
                        print("死亡日期时间格式错误")
                        self.flag_format_death_date = True
        return self.flag_format_death_date

    def check_birthday_year_month_day(self):
        """
        1、限制：日<=31、月<=12、年!=0xx
        一年有12个月，其中1月、3月、5月、7月、8月、10月、12月为31天；
        4月、6月、9月、11月为30天；
        2月为28天(闰年为29天)。
        2、月份是00时，日必是00
        :return:
        """
        if self.time_of_birth:
            time_of_birth_split = self.time_of_birth.split("-")
            # if str(self.time_of_birth).startswith("-"):  # 公元前 出生
            year = time_of_birth_split[-3]
            month = time_of_birth_split[-2]
            day = time_of_birth_split[-1]

            if year.startswith("0"):
                self.flag_value_birth_year = True
                print("出生时间-年份错误！不能为0xx")
            if month == "00":
                if day != "00":
                    self.flag_value_birth_day = True
                    print("出生时间-日错误！请改为00")
            else:
                if not str(month).startswith("0") and int(month) > 12:
                    print("出生时间-月份错误！大于12了")
                    self.flag_value_birth_month = True

                if day != "00":
                    if month == "01":
                        if not str(day).startswith("0") and int(day) > 31:
                            self.flag_value_birth_day = True
                            print("出生时间-日错误！大于31了")
                    elif month == "02":
                        if not str(day).startswith("0") and int(day) > 29:  # 粗限制2月份天数，暂时不做闰年判断限制2月天数
                            self.flag_value_birth_day = True
                            print("出生时间-日错误！大于29了")
                    elif month == "03":
                        if not str(day).startswith("0") and int(day) > 31:
                            self.flag_value_birth_day = True
                            print("出生时间-日错误！大于31了")
                    elif month == "04":
                        if not str(day).startswith("0") and int(day) > 30:
                            self.flag_value_birth_day = True
                            print("出生时间-日错误！大于30了")
                    elif month == "05":
                        if not str(day).startswith("0") and int(day) > 31:
                            self.flag_value_birth_day = True
                            print("出生时间-日错误！大于31了")
                    elif month == "06":
                        if not str(day).startswith("0") and int(day) > 30:
                            self.flag_value_birth_day = True
                            print("出生时间-日错误！大于30了")
                    elif month == "07":
                        if not str(day).startswith("0") and int(day) > 31:
                            self.flag_value_birth_day = True
                            print("出生时间-日错误！大于31了")
                    elif month == "08":
                        if not str(day).startswith("0") and int(day) > 31:
                            self.flag_value_birth_day = True
                            print("出生时间-日错误！大于31了")
                    elif month == "09":
                        if not str(day).startswith("0") and int(day) > 30:
                            self.flag_value_birth_day = True
                            print("出生时间-日错误！大于30了")
                    elif month == "10":
                        if not str(day).startswith("0") and int(day) > 31:
                            self.flag_value_birth_day = True
                            print("出生时间-日错误！大于31了")
                    elif month == "11":
                        if not str(day).startswith("0") and int(day) > 30:
                            self.flag_value_birth_day = True
                            print("出生时间-日错误！大于30了")
                    elif month == "12":
                        if not str(day).startswith("0") and int(day) > 31:
                            self.flag_value_birth_day = True
                            print("出生时间-日错误！大于31了")
                    else:
                        print("出生时间-月份格式错误，不在设定 00-12 范围！")
                        self.flag_value_birth_month = True
        return self.flag_value_birth_year, self.flag_value_birth_month, self.flag_value_birth_day

    def check_death_year_month_day(self):
        """
        1、限制：日<=31、月<=12、年!=0xx
        一年有12个月，其中1月、3月、5月、7月、8月、10月、12月为31天；
        4月、6月、9月、11月为30天；
        2月为28天(闰年为29天)。
        2、月份是00时，日必是00
        :return:
        """
        if self.time_of_death:
            time_of_death_split = self.time_of_death.split("-")
            # if str(self.time_of_death).startswith("-"):  # 公元前 出生
            year = time_of_death_split[-3]
            month = time_of_death_split[-2]
            day = time_of_death_split[-1]
            if year.startswith("0"):
                self.flag_value_death_year = True
                print("死亡时间-年份错误！不能为0xx")
            if month == "00":
                if day != "00":
                    self.flag_value_death_day = True
                    print("死亡时间-日错误！请改为00")
            else:
                if not str(month).startswith("0") and int(month) > 12:
                    print("死亡时间-月份错误！大于12了")
                    self.flag_value_death_month = True

                if day != "00":
                    if month == "01":
                        if not str(day).startswith("0") and int(day) > 31:
                            self.flag_value_death_day = True
                            print("死亡时间-日错误！大于31了")
                    elif month == "02":
                        if not str(day).startswith("0") and int(day) > 29:  # 粗限制2月份天数，暂时不做闰年判断限制2月天数
                            self.flag_value_death_day = True
                            print("死亡时间-日错误！大于29了")
                    elif month == "03":
                        if not str(day).startswith("0") and int(day) > 31:
                            self.flag_value_death_day = True
                            print("死亡时间-日错误！大于31了")
                    elif month == "04":
                        if not str(day).startswith("0") and int(day) > 30:
                            self.flag_value_death_day = True
                            print("死亡时间-日错误！大于30了")
                    elif month == "05":
                        if not str(day).startswith("0") and int(day) > 31:
                            self.flag_value_death_day = True
                            print("死亡时间-日错误！大于31了")
                    elif month == "06":
                        if not str(day).startswith("0") and int(day) > 30:
                            self.flag_value_death_day = True
                            print("死亡时间-日错误！大于30了")
                    elif month == "07":
                        if not str(day).startswith("0") and int(day) > 31:
                            self.flag_value_death_day = True
                            print("死亡时间-日错误！大于31了")
                    elif month == "08":
                        if not str(day).startswith("0") and int(day) > 31:
                            self.flag_value_death_day = True
                            print("死亡时间-日错误！大于31了")
                    elif month == "09":
                        if not str(day).startswith("0") and int(day) > 30:
                            self.flag_value_death_day = True
                            print("死亡时间-日错误！大于30了")
                    elif month == "10":
                        if not str(day).startswith("0") and int(day) > 31:
                            self.flag_value_death_day = True
                            print("死亡时间-日错误！大于31了")
                    elif month == "11":
                        if not str(day).startswith("0") and int(day) > 30:
                            self.flag_value_death_day = True
                            print("死亡时间-日错误！大于30了")
                    elif month == "12":
                        if not str(day).startswith("0") and int(day) > 31:
                            self.flag_value_death_day = True
                            print("死亡时间-日错误！大于31了")
                    else:
                        print("死亡时间-月份格式错误，不在设定 00-12 范围！")
                        self.flag_value_death_month = True
        return self.flag_value_death_year, self.flag_value_death_month, self.flag_value_death_day

    def value_check_birthday_death_date(self):

        """
            Type_error:
            1、出生时间在死亡时间之后；
            2、死亡时间与出生时间相差>100岁；
            3、根据死亡时间与出生时间得出的年龄与实际给出的age字段值相差大于2的；
            4、有出生和死亡时间但age为空的;
            5、年龄age<10;
        """

        if self.time_of_birth and self.time_of_death:
            if str(self.time_of_death).startswith("-"):  # 公元前 去世
                time_of_death_ = self.time_of_death[1:-1]
                year_death = time_of_death_.split("-")[0]
                time_of_birth_ = self.time_of_birth[1:-1]
                year_birth = time_of_birth_.split("-")[0]
                age = int(year_birth) - int(year_death)
            else:  # 公元后 去世
                if str(self.time_of_birth).startswith("-"):  # 公元前 出生
                    time_of_birth_ = self.time_of_birth[1:-1]
                    year_birth = time_of_birth_.split("-")[0]
                    year_death = self.time_of_death.split("-")[0]
                    age = int(year_birth) + int(year_death)
                else:  # 公元后 出生
                    year_birth = self.time_of_birth.split("-")[0]
                    year_death = self.time_of_death.split("-")[0]
                    age = int(year_death) - int(year_birth)
            if int(age) > 100:
                self.flag_age_greater_than_100 = True
                # print(age)
            elif int(age) <= 0:
                self.flag_age_less_than_0 = True
            elif int(age) > 0 and int(age) <= 10:
                self.flag_age_greater_than_0_and_less_than_10 = True

            # 计算年龄差值
            if self.data_dict["age"]:
                age_diff = abs(int(age) - int(self.data_dict["age"]))
                if age_diff > 2:
                    print("basic_info_error_根据死亡与出生时间计算年龄与现存age字段值相差大于2")
                    self.flag_age_diff_greater_than_2 = True
            else:
                print("ERROR！ 有出生和死亡时间但age为空")
                self.flag_age_noexist = True

        return self.flag_age_greater_than_100, self.flag_age_less_than_0, \
               self.flag_age_greater_than_0_and_less_than_10, \
               self.flag_age_diff_greater_than_2, self.flag_age_noexist

    def value_check_introduction(self):
        """
        限制：简介不能为空！
        :return:
        """

        if not self.introduction:
            self.flag_introduction_noexist = True
            return self.flag_introduction_noexist

    def value_check_all_name(self):
        """
        限制：姓名不能为空！
        :return:
        """

        if not self.all_name:
            self.flag_all_name_noexist = True
            return self.flag_all_name_noexist

    def is_leap_year(self, year):
        """
        闰年判断
        :param year:
        :return:
        """
        # year = int(input("输入一个年份: "))
        if (year % 4) == 0:
            if (year % 100) == 0:
                if (year % 400) == 0:
                    print("{0} 是闰年".format(year))  # 整百年能被400整除的是闰年
                    return True
                else:
                    print("{0} 不是闰年".format(year))
                    return False
            else:
                print("{0} 是闰年".format(year))  # 非整百年能被4整除的为闰年
                return True
        else:
            print("{0} 不是闰年".format(year))
            return False
