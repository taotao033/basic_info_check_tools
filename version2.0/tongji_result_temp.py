import pymongo
import json
import os

today_date = "20201128"
result_report_dir = "test_result"
file_list = os.listdir(result_report_dir)

client = pymongo.MongoClient(host="192.168.1.23", port=27017)
col_nlp_extract_base_check_person1 = client["earth_gis"]["Information_ancient_base_temp1"]
col_pro_6_3_id_mapping_before = client["earth_gis"]["Information_ancient_relation_temp1"]

col_history_proofreading_base = client["earth_gis"]["Information_ancient_base_temp2"]
col_history_proofreading_rel = client["earth_gis"]["Information_ancient_relation_temp2"]

base_list = list(col_history_proofreading_base.find())

"""
    关系库，校对前后人物关系数一致性验证
"""
rel_before_list = list(col_pro_6_3_id_mapping_before.find())
person_id2count_raw = {}    # 校验前，每个人物对应关系数量
for x in rel_before_list:
    if x["person_1_id"] not in person_id2count_raw:
        person_id2count_raw[x["person_1_id"]] = 1
    else:
        person_id2count_raw[x["person_1_id"]] += 1

rel_list = list(col_history_proofreading_rel.find())
person_id2count = {}    # 每个人物对应关系数量
for x in rel_list:
    if x["person_1_id"] not in person_id2count:
        person_id2count[x["person_1_id"]] = 1
    else:
        person_id2count[x["person_1_id"]] += 1

for per_id, count in person_id2count.items():
    count_raw = person_id2count_raw[per_id]
    if count != count_raw:
        print("person_id:" + per_id + ", 库前库后关系数不一致！" + " " + "库前:" + str(count_raw) + ", 库后:" + str(count))

for p_id in person_id2count_raw.keys():
    if p_id not in person_id2count:
        print("person_1_id:" + p_id + "对应关系未入校验后库")
"""
    校对结果统计
"""
print("校对结果统计")
tongji_check_results = {"基本信息": {"总数": len(list(col_nlp_extract_base_check_person1.find())),
                                 "累计校对": len(base_list)},
                        "关系": {"总数": len(list(col_pro_6_3_id_mapping_before.find())),
                               "累计校对": len(rel_list)}}

for x in base_list:
    if x["check_author"] not in tongji_check_results:
        tongji_check_results[x["check_author"]] = {"基本信息完成数": 1}
    else:
        tongji_check_results[x["check_author"]]["基本信息完成数"] += 1

    if x["person_id"] in person_id2count:

        if "关系完成数" not in tongji_check_results[x["check_author"]]:
            tongji_check_results[x["check_author"]]["关系完成数"] = person_id2count[x["person_id"]]
        else:
            tongji_check_results[x["check_author"]]["关系完成数"] += person_id2count[x["person_id"]]


if not file_list:   # 第一次保存结果
    """
        调整输出格式
    """
    print("第一次保存结果")
    tongji_check_results_today = {}
    for k, v in tongji_check_results.items():
        if k == "基本信息" or k == "关系":
            tongji_check_results_today[k] = v
        else:
            tongji_check_results_today[k] = {"基本信息": {"累计校对": v["基本信息完成数"], "今日校对": v["基本信息完成数"]},
                                             "关系": {"累计校对": v["关系完成数"], "今日校对": v["关系完成数"]}
                                             }

else:   # 累计结果计算    今日完成量 = 累计完成数 - 前一日完成数
    tongji_check_results_yesterday = \
        json.load(open(result_report_dir + "/" + str(int(today_date) - 1) + ".json", "r", encoding="utf-8"))

    tongji_check_results["基本信息"]["今日校对"] = \
        tongji_check_results["基本信息"]["累计校对"] - tongji_check_results_yesterday["基本信息"]["累计校对"]
    tongji_check_results["关系"]["今日校对"] = \
        tongji_check_results["关系"]["累计校对"] - tongji_check_results_yesterday["关系"]["累计校对"]

    tongji_check_results_today = {"基本信息": tongji_check_results["基本信息"],
                                  "关系": tongji_check_results["关系"]}

    for k, v in tongji_check_results.items():
        if k == "基本信息" or k == "关系":
            continue
        tongji_check_results_today[k] = {"基本信息": {"累计校对": v["基本信息完成数"], "今日校对": v["基本信息完成数"] -
                                                  tongji_check_results_yesterday[k]["基本信息"]["累计校对"]},
                                         "关系": {"累计校对": v["关系完成数"], "今日校对": v["关系完成数"] -
                                                tongji_check_results_yesterday[k]["关系"]["累计校对"]}
                                         }

json.dump(tongji_check_results_today, open(result_report_dir + "/" + today_date + ".json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=4)








