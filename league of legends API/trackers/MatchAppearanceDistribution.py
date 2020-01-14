
from ..common import *

class MatchAppearanceDistribution(object):
	def __init__(self, endpoint):
		self.appearances = collections.defaultdict(lambda: 0)
		for summoner in endpoint.summoners.query().project(includes=['summonerUUID']).execute():
			self.appearances[summoner['summonerUUID']] = 0

	def save(self):
		return {'version':1, 'data':self.appearances}

	def load(self, state):
		self.appearances = state['data']

	def update(self, endpoint, request_info, update):
		json = update['response']['json']
		if request_info['response_type'] == "MatchDTO":
			if json['queueId'] not in [420,440,470]:
				return
			players = [p["player"] for p in json["participantIdentities"] if 'player' in p]
			for player in players:
				self.appearances[player['summonerId']] += 1

	def report(self, dir):
		self.bins = collections.defaultdict(lambda: 0)
		for appearance in self.appearances.values():
			self.bins[appearance] += 1

		xs, wts = [], []
		for x, wt in self.bins.items():
			xs.append(x)
			wts.append(wt)

		fig, ax = plt.subplots()
		ax.hist(xs, bins=range(0,50,1), weights=wts)
		plt.xticks( [2*x for x in range(0,20)] )
		plt.xlim( (0, 20) )
		plt.savefig(os.path.join(dir, 'match_appear.png'), dpi = 300)
		plt.close(fig)
