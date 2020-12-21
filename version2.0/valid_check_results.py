import pymongo

client = pymongo.MongoClient(host="192.168.1.106", port=27017)
col_nlp_extract_base_check_person1 = client["earth_gis_temp"]["nlp_extract_base_check_person1"]

col_history_proofreading_base = client["earth_gis_temp"]["history_proofreading_base_copy"]


# id_list = []
# for x in col_history_proofreading_base.find():
#     if x["person_id"] not in id_list:
#         id_list.append(x["person_id"])
#
#     else:
#         print("重复 " + x["person_id"])
#
# for x in col_nlp_extract_base_check_person1.find():
#     if x["person_id"] not in id_list:
#         print(x["person_id"])

col_pro_6_3_id_mapping_before = client["earth_gis_temp"]["pro_6_3_id_mapping_before"]

person_id2count1 = {}
rel_before_list = list(col_pro_6_3_id_mapping_before.find())
for x in rel_before_list:
    if x["person_1_id"] not in person_id2count1:
        person_id2count1[x["person_1_id"]] = 1
    else:
        person_id2count1[x["person_1_id"]] += 1


col_history_proofreading_rel = client["earth_gis_temp"]["history_proofreading_rel"]

person_id2count2 = {}
rel_before_list2 = list(col_history_proofreading_rel.find())
for x in rel_before_list2:
    if x["person_1_id"] not in person_id2count2:
        person_id2count2[x["person_1_id"]] = 1
    else:
        person_id2count2[x["person_1_id"]] += 1

if len(person_id2count1) != len(person_id2count2):
    print("关系库人数，校验前后不一致")

for k, v in person_id2count1.items():
    if k in person_id2count2:
        if v != person_id2count2[k]:
            print("person_1_id:" + k + "校验前后，关系数不一致")
    else:
        print("person_1_id:" + k + "不在校验后库中")