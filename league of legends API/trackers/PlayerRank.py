
from ..common import *

class PlayerRank(object):
	def request_interest(self):
		return ["Set[LeaguePositionDTO]"]

	def __init__(self):
		self.ranks = {}

	def save(self):
		return {'version':1, 'data':self.ranks}

	def load(self, state):
		self.ranks = state['data']

	def get_rank(self, key):
		return self.ranks.get(key, None)

	def compute_percentiles(self):
		self.bins = {p:collections.defaultdict(lambda: 0) for p in const.positions}
		for (id, position), score in self.ranks.items():
			self.bins[position][score] += 1
		for position, bin in self.bins.items():
			xs, wts = [], []
			for x, wt in bin.items():
				xs.append(x)
				wts.append(wt)

			fig, ax = plt.subplots()
			ax.hist(xs, bins=range(0,3200,1), weights=wts)
			plt.xticks( [400*x for x in range(0,10)] )
			plt.xlim( (0, 3000) )
			plt.savefig('{0}.png'.format(position), dpi = 300)
			plt.close(fig)


	def update(self, endpoint, request_info, update):
		if request_info['response_type'] == "Set[LeaguePositionDTO]":
			json = update['response']['json']
			for rank in json:
				score = const.score_rank(rank['tier'], rank['rank'], rank['leaguePoints'])
				self.ranks[(rank['summonerId'], rank['position'])] = score
