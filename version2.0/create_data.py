import pymongo


client = pymongo.MongoClient(host="192.168.1.106", port=27017)
nlp_extract_base_check_full = client["earth_gis_temp_1"]["nlp_extract_base_check_full"]
nlp_extract_base_check_person1 = client["earth_gis_temp_1"]["nlp_extract_base_check_person1"]

client2 = pymongo.MongoClient(host="192.168.1.18", port=27017)
fusion_3url_basic_information = client2["enlarge_data_2020-11-25"]["fusion_3url_basic_information"]


pro_6_3_id_mapping_before = client["earth_gis_temp_1"]["pro_6_3_id_mapping_before"]

person_id2base_info_full = {}
for x in nlp_extract_base_check_full.find({}, {"_id": 0}):
    person_id2base_info_full[x["person_id"]] = x

person_id2base_info_3k = {}
for x in fusion_3url_basic_information.find({}, {"_id": 0}):
    person_id2base_info_3k[x["person_id"]] = x

for x in pro_6_3_id_mapping_before.find({}, {"person_1_id": 1}):
    if x["person_1_id"] not in person_id2base_info_3k:
        person_id2base_info_3k[x["person_1_id"]] = person_id2base_info_full[x["person_1_id"]]
        print(x["person_1_id"] + "不在enlarge_data_2020-11-25.fusion_3url_basic_information中")

out_list = []

for k, v in person_id2base_info_3k.items():
    out_list.append(v)

nlp_extract_base_check_person1.insert_many(out_list)

