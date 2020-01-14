
from ..common import *

class MatchRatingsByPlayerRating(object):
	def __init__(self):
		self.by_ratings = collections.defaultdict(lambda: collections.defaultdict(lambda: 0))

	def request_interest(self):
		return ["MatchDTO"]

	def updates(self, request, response):
		if request.response_type == "MatchDTO":
			summoner_uuids = [p[1] for p in response.json["players"]]
			qpositions = self.player_position.get_dict(summoner_uuids, filter_none=True)
			match_rating = self.match_rating.get(response.json["gameId"])
			if match_rating is None:
				return
			match_rating = round(match_rating / 10)
			for qposition in qpositions.values():
				player_rating = const.get_position_score(qposition)
				if player_rating is None:
					return
				player_rating = round(player_rating / 10)
				self.by_ratings[player_rating][match_rating] += 1

	def dim2_image(self, dir):
		xs, ys, wts = [], [], []
		for player_rating, d in self.by_ratings.items():
			for match_rating, ct in d.items():
				xs.append(player_rating)
				ys.append(match_rating)
				wts.append(ct)
		fig, ax = plt.subplots()
		plt.hist2d(xs, ys, bins=80, weights=wts)
		plt.xticks( [40*x for x in range(0,6)] )
		plt.yticks( [40*y for y in range(0,6)] )
		plt.savefig(os.path.join(dir, "2d.png"), dpi=300)
		plt.close(fig)

	def dim1_images(self, dir):
		for player_rating, d in self.by_ratings.items():
			match_ratings, wts = [], []
			for x, wt in d.items():
				match_ratings.append(x)
				wts.append(wt)
			fig, ax = plt.subplots()
			ax.hist(match_ratings, bins=500, weights=wts)
			plt.xticks( [40*x for x in range(0,6)] )
			plt.yticks( [25*y for y in range(0,6)] )
			plt.savefig(os.path.join(dir, 'match_dist_{0}.png'.format(player_rating)), dpi = 300)
			plt.close(fig)
