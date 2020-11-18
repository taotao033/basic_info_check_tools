import pymongo
from tqdm import tqdm

client = pymongo.MongoClient(host="192.168.1.23", port=27017)
col_information_ancient_base = client["earth_gis"]["Information_ancient_base_temp1_raw"]
col_information_ancient_base2 = client["earth_gis"]["Information_ancient_base_temp1"]
col_information_ancient_event = client["earth_gis"]["Information_ancient_event_temp1_raw"]
col_information_ancient_event2 = client["earth_gis"]["Information_ancient_event_temp1"]
col_information_ancient_relation = client["earth_gis"]["Information_ancient_relation_temp1_raw"]
col_information_ancient_relation2 = client["earth_gis"]["Information_ancient_relation_temp1"]

col_information_ancient_base_out_list = []
for x in tqdm(list(col_information_ancient_base.find({}, {"_id": 0}))):
    temp = {}
    for k, v in x.items():
        temp[k] = str(v)
    col_information_ancient_base_out_list.append(temp)

col_information_ancient_base2.insert_many(col_information_ancient_base_out_list)

col_information_ancient_event_out_list = []
for x in tqdm(list(col_information_ancient_event.find({}, {"_id": 0}))):
    temp = {}
    for k, v in x.items():
        temp[k] = str(v)
    col_information_ancient_event_out_list.append(temp)

col_information_ancient_event2.insert_many(col_information_ancient_event_out_list)


col_information_ancient_relation_out_list = []
for x in tqdm(list(col_information_ancient_relation.find({}, {"_id": 0}))):
    temp = {}
    for k, v in x.items():
        temp[k] = str(v)
    col_information_ancient_relation_out_list.append(temp)

col_information_ancient_relation2.insert_many(col_information_ancient_relation_out_list)

