
from ..common import *

class DatabaseBuilder(object):
	def __init__(self):
		pass

	def save(self):
		return {}

	def load(self, state):
		pass
		
	def update(self, endpoint, request_info, update):
		if request_info['response_type'] == "LeagueListDTO":
			self.add_LeagueList(endpoint, update)
		elif request_info['response_type'] == "SummonerDTO":
			self.add_Summoner(endpoint, update)
		elif request_info['response_type'] == "MatchListDTO":
			self.add_MatchList(endpoint, update)
		elif request_info['response_type'] == "MatchDTO":
			self.add_Match(endpoint, update)
		elif request_info['response_type'] == "Set[LeaguePositionDTO]":
			self.add_SetOfLeaguePosition(endpoint, update)
		else:
			raise Exception("cannot process {0}".format(update))

	def add_LeagueList(self, endpoint, update):
		json = update['response']['json']

		summoner_uuids = [s["summonerId"] for s in json["entries"]]
		q = endpoint.summoners.query().match_group('summonerUUID', summoner_uuids).project(includes=['summonerUUID','games'])
		summoners = useful.MongoAgg.to_dict(q, 'summonerUUID')
		updates = []
		for entry in json["entries"]:
			if entry['summonerId'] not in summoners:
				summoner = endpoint.summoners.default_summoner(entry["summonerId"])
			else:
				summoner = summoners[entry['summonerId']]
			games = entry["wins"] + entry["losses"]
			time_interval = (update['response']['time'] - endpoint.season_start_s)
			endpoint.summoners.update_games(summoner, json['queue'], 'ALL', games, time_interval)
			updates.append(endpoint.summoners.mc.update_set(summoner))
		endpoint.summoners.mc.bulk_write(updates)

	def add_Summoner(self, endpoint, update):
		json = update['response']['json']
		summoner = endpoint.summoners.query(summonerUUID=json["id"]).one()
		if summoner is None:
			summoner = endpoint.summoners.mc.default_doc(json["id"])
		summoner["accountUUID"] = json["accountId"]
		endpoint.summoners.mc.bulk_write([endpoint.summoners.mc.update_set(summoner)])

	def add_MatchList(self, endpoint, update):
		json = update['response']['json']

		accountUUID = update['request']['args']['account_uuid']
		summoner = endpoint.summoners.query(accountUUID=accountUUID).project(includes=['summonerUUID']).one()
		summoner['last_matchlist_check'] = update['response']['time']
		endpoint.summoners.mc.bulk_write([endpoint.summoners.mc.update_set(summoner)])

		match_uuids = [m["gameId"] for m in json["matches"]]
		q = endpoint.matches.query().match_group('matchUUID', match_uuids).project(includes=['matchUUID'])
		matches = useful.MongoAgg.to_dict(q, 'matchUUID')
		updates = []
		for entry in json["matches"]:
			if entry['gameId'] not in matches:
				match = endpoint.matches.default_match(entry["gameId"])
				match["timestamp"] = entry["timestamp"]
				match["queue"] = entry["queue"]
				updates.append(endpoint.matches.mc.update_set(match))
		endpoint.matches.mc.bulk_write(updates)

	def add_Match(self, endpoint, update):
		json = update['response']['json']
		match = endpoint.matches.query(matchUUID=json["gameId"]).one()
		match["latest_request"] = update['uuid']
		endpoint.matches.mc.bulk_write([endpoint.matches.mc.update_set(match)])

		players = [p["player"] for p in json["participantIdentities"] if 'player' in p]
		summoner_uuids = [p['summonerId'] for p in players if 'summonerId' in p]
		q = endpoint.summoners.query().match_group('summonerUUID', summoner_uuids).project(includes=['summonerUUID', 'accountUUID'])
		summoners = useful.MongoAgg.to_dict(q, 'summonerUUID')
		updates = []
		for player in players:
			if 'summonerId' not in player:
				continue
			if player['summonerId'] not in summoners:
				summoner = endpoint.summoners.default_summoner(player["summonerId"])
			else:
				summoner = summoners[player['summonerId']]
			#if "accountUUID" not in summoner:
			summoner["accountUUID"] = player['currentAccountId']
			updates.append( endpoint.summoners.mc.update_set(summoner))
		endpoint.summoners.mc.bulk_write(updates)

	def add_SetOfLeaguePosition(self, endpoint, update):
		json = update['response']['json']

		data_by_uuid = {p['summonerId']:p for p in json}
		summoner_uuids = list(data_by_uuid.keys())
		q = endpoint.summoners.query().match_group('summonerUUID', summoner_uuids).project(includes=['summonerUUID','games'])
		summoners = useful.MongoAgg.to_dict(q, 'summonerUUID')
		updates = []

		for summoner_uuid, summoner_data in data_by_uuid.items():
			if summoner_uuid not in summoners:
				summoner = endpoint.summoners.default_summoner(summoner_uuid)
			else:
				summoner = summoners[summoner_uuid]
			games = summoner_data['wins'] + summoner_data['losses']
			time_interval = (update['response']['time'] - endpoint.season_start_s)
			endpoint.summoners.update_games(summoner, summoner_data['queueType'], summoner_data['position'], games, time_interval)
			updates.append( endpoint.summoners.mc.update_set(summoner))
		endpoint.summoners.mc.bulk_write(updates)
