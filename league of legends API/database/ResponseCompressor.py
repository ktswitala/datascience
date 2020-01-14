
from ..common import *

class ResponseCompressor(object):
	def __init__(self):
		pass

	def compress(self, request, response):
		if request.response_type == "LeagueListDTO":
			return self.compress_LeagueList(request, response)
		elif request.response_type == "SummonerDTO":
			return response
		elif request.response_type == "MatchListDTO":
			return self.compress_MatchList(request, response)
		elif request.response_type == "MatchDTO":
			return self.compress_Match(request, response)
		elif request.response_type == "Set[LeaguePositionDTO]":
			return self.compress_SetOfLeaguePosition(request, response)
		else:
			raise Exception("cant compress {0}".format(request.response_type))

	def dict_to_list(self, d, keys):
		return [d[key] for key in keys]

	def compress_LeagueList(self, request, response):
		if 'leagueId' not in response:
			return response
		keys = ["summonerId","leaguePoints","rank","wins","losses"]
		new_entries = []
		for entry in response["entries"]:
			new_entries.append( self.dict_to_list(entry, keys) )
		response["entries"] = new_entries
		return response

	def compress_SetOfLeaguePosition(self, request, response):
		keys = ["queueType","leagueId"]
		new_response = []
		for entry in response:
			new_response.append( self.dict_to_list(entry, keys) )
		return new_response

	def compress_Match(self, request, response):
		match = {}
		match["compress_version"] = 1
		match["gameId"] = response["gameId"]
		match["season"] = response["seasonId"]
		match["queue"] = response["queueId"]
		match["gameVersion"] = response["gameVersion"]
		match["platformId"] = response["platformId"]
		match["gameDuration"] = response['gameDuration']
		match["gameCreation"] = response['gameCreation']
		match["participants"] = {}
		match["players"] = []
		for participant_data in response["participants"]:
			participant = []
			match["participants"][participant_data["participantId"]] = participant

			participant.append(participant_data["championId"])
			participant.append(participant_data["stats"]["win"] )
			participant.append(participant_data["timeline"]["lane"] )
			participant.append(participant_data["timeline"]["role"] )

		for participant in response["participantIdentities"]:
			if "player" in participant:
				player = participant["player"]
				if 'summonerId' not in player:
					continue
				match["players"].append( [participant["participantId"], player["summonerId"], player["accountId"]] )
		return match

	def compress_MatchList(self, request, response):
		keys = ["gameId", "timestamp", "queue"]
		new_matches = []
		for match_data in response["matches"]:
			new_matches.append( self.dict_to_list(match_data, keys))
		response["matches"] = new_matches
		return response
