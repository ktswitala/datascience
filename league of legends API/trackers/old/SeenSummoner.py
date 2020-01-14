
from ..common import *

class SeenSummoner(object):
	def add_summoners(self, summoner_uuids, t):
		if len(summoner_uuids) == 0:
			return
		summoner_seens = self.seen_summoner.get_dict(summoner_uuids)
		update = useful.filter_dict_values(lambda v: v is None, summoner_seens)
		for k in update.keys():
			update[k] = t
		self.seen_summoner.set_dict(update)

	def request_interest(self):
		return ["LeagueListDTO", "MatchDTO"]

	def updates(self, request, response):
		if request.response_type == "LeagueListDTO":
			summoner_uuids = [e[0] for e in response.json["entries"]]
			self.add_summoners(summoner_uuids, response.time)
		if request.response_type == "MatchDTO":
			summoner_uuids = [p[1] for p in response.json["players"]]
			self.add_summoners(summoner_uuids, response.time)
