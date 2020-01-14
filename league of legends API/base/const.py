
import os, simplejson

from .Endpoint import *

minute = 60
hour = minute*60
day = hour*24
week = day*7
year = day*365

queue_types = ["RANKED_SOLO_5x5","RANKED_FLEX_SR","RANKED_FLEX_TT"]
queue_type_to_id = {'RANKED_SOLO_5x5':420, 'RANKED_FLEX_SR':440, 'RANKED_FLEX_TT':470}
queue_id_to_label = {
	430:"5v5 Blind Pick games",
	460:"3v3 Blind Pick games", 400:"5v5 Draft Pick games",
	420:"5v5 Ranked Solo Games", 440:"5v5 Ranked Flex games", 470:"3v3 Ranked Flex games"
}

tier_types = ["IRON", "BRONZE", "SILVER", "GOLD", "PLATINUM", "DIAMOND", "MASTER","GRANDMASTER","CHALLENGER"]
divided_tiers = ["IRON", "BRONZE", "SILVER", "GOLD", "PLATINUM", "DIAMOND"]
undivided_tiers = ["MASTER","GRANDMASTER","CHALLENGER"]
divisions = ['IV', 'III', 'II', 'I']
positions = ["TOP", "MIDDLE", "BOTTOM", "JUNGLE", "UTILITY"]

def iterate_position_classes():
	queues = ['RANKED_SOLO_5x5']
	for queue in queues:
		for tier in divided_tiers:
			for div in divisions:
				for position in positions:
					yield queue, tier, div, position

regions = ["BR", "EUNE", "EUW", "JP", "KR", "LAN", "LAS", "NA", "OCE", "TR", "RU", "PBE"]
response_types = ["LeagueListDTO", "Set[LeaguePositionDTO]", "SummonerDTO", "MatchListDTO", "MatchDTO"]

endpoint_infos = {}
endpoint_infos["BR"] = {"platforms":["BR1"], "host":"br1.api.riotgames.com"}
endpoint_infos["EUNE"] = {"platforms":["EUN1"], "host":"eun1.api.riotgames.com"}
endpoint_infos["EUW"] = {"platforms":["EUW1"], "host":"euw1.api.riotgames.com"}
endpoint_infos["JP"] = {"platforms":["JP1"], "host":"jp1.api.riotgames.com"}
endpoint_infos["KR"] = {"platforms":["KR"], "host":"kr.api.riotgames.com"}
endpoint_infos["LAN"] = {"platforms":["LA1"], "host":"la1.api.riotgames.com"}
endpoint_infos["LAS"] = {"platforms":["LA2"], "host":"la2.api.riotgames.com"}
endpoint_infos["NA"] = {"platforms":["NA1","NA"], "host":"na1.api.riotgames.com"}
endpoint_infos["OCE"] = {"platforms":["OC1"], "host":"oc1.api.riotgames.com"}
endpoint_infos["TR"] = {"platforms":["TR1"], "host":"tr1.api.riotgames.com"}
endpoint_infos["RU"] = {"platforms":["RU"], "host":"ru.api.riotgames.com"}
endpoint_infos["PBE"] = {"platforms":["PBE1"], "host":"pbe1.api.riotgames.com"}
endpoints = {}

tier_label_to_num = {}
division_label_to_num = {}
for i, tier in enumerate(divided_tiers):
	tier_label_to_num[tier] = 400*i
for j, div in enumerate(divisions):
	division_label_to_num[div] = 100*j

def init_endpoint(region):
	endpoint = Endpoint()
	endpoint_info = endpoint_infos[region]
	endpoint.region = region
	endpoint.host = endpoint_info["host"]
	endpoint.platforms = endpoint_info["platforms"]
	return endpoint

def score_rank(tier, division, lp):
	if tier in undivided_tiers:
		return int(2400 + lp)
	elif tier in divided_tiers:
		return int(tier_label_to_num[tier] + division_label_to_num[division] + lp)
	else:
		raise Exception("cannot score")

def score_position():
	pass

def get_position_score():
	pass

def get_queue_rank(queue):
	if '420' in queue:
		return queue['420']
	elif '440' in queue:
		return queue['440']
	elif '470' in queue:
		return queue['470']
	else:
		return None

def load_champs():
	dir = os.path.dirname(__file__)
	f = open(os.path.join(dir, "champion.json"), "rb")
	champs = simplejson.load(f)
	f.close()
	return champs

champ_id_to_name = {}
champ_ids = []
for champ_name, data in load_champs()["data"].items():
	champ_ids.append(int(data["key"]))
	champ_id_to_name[int(data["key"])] = champ_name
