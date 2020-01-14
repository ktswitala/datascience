
from ..common import *

class MatchRating(object):
	def request_interest(self):
		return ["MatchDTO"]

	def updates(self, request, response):
		if request.response_type == "MatchDTO":
			summoner_uuids = [p[1] for p in response.json["players"]]
			player_positions = self.player_position.get_dict(summoner_uuids, filter_none=True).values()
			scores = [const.get_position_score(position) for position in player_positions]
			if len(scores) == 0:
				return
			tier_avg = sum(scores) / len(scores)
			self.match_rating.set(response.json["gameId"], tier_avg)
