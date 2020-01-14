
from ..common import *

from .PositionAssignment import assign_positions_safe

class SummonerMatchLinks(object):
	def __init__(self):
		self.graph = networkx.Graph()
		self.rejected_match = 0
		self.total_links = 0
		self.total_match = 0
		self.total_ranks = 0
		self.verbose = False
		self.rank_distribution = collections.defaultdict(lambda: collections.defaultdict(lambda: 0))
		self.norm_rank_distribution = {}
		self.fields = ['rank_distribution', 'rejected_match', 'total_links', 'total_match', 'total_ranks']

	def startup(self):
		self.normalize()

	def save(self):
		state = {'version':1}
		state.update( useful.dslice_obj(self, self.fields) )
		return state

	def load(self, state):
		useful.dupdate_obj(self, state, self.fields)

	def update(self, endpoint, request_info, update):
		json = update['response']['json']
		if request_info['response_type'] == "MatchDTO":
			if json['queueId'] != 420:
				return

			if self.total_match % 10000 == 0:
				self.normalize()
			if self.total_match % 20000 == 0 and self.verbose is True:
				self.report()

			self.total_match += 1
			participants = {p['participantId']:p for p in json['participants']}
			players = {p['participantId']:p["player"] for p in json["participantIdentities"] if 'player' in p}
			player_positions = assign_positions_safe(participants)
			if len(player_positions) < 10:
				player_positions = self.position_assignment.assign_positions_by_champ(participants)
			if len(player_positions) < 10:
				self.rejected_match += 1
				return

			for pid1, player_position1 in player_positions.items():
				player1 = (players[pid1]['summonerId'], player_position1)
				player1_rank = self.player_rank.get_rank( player1 )
				if player1_rank is not None:
					player1_rank = min(24, round(player1_rank / 100))
				else:
					continue
				for pid2, player_position2 in player_positions.items():
					if pid1 >= pid2:
						continue
					#self.graph.add_edge(player1, player2)
					player2 = (players[pid2]['summonerId'], player_position2)
					player2_rank = self.player_rank.get_rank( player2 )
					if player2_rank is not None:
						player2_rank = min(24, round(player2_rank / 100))
						self.rank_distribution[player1_rank][player2_rank] += 1
						self.rank_distribution[player2_rank][player1_rank] += 1
						self.total_ranks += 1
					self.total_links += 1

	def normalize(self):
		for player1_rank, dist in self.rank_distribution.items():
			N = sum(dist.values())
			self.norm_rank_distribution[player1_rank] = collections.defaultdict(lambda: 0)
			for player2_rank, ct in dist.items():
				self.norm_rank_distribution[player1_rank][player2_rank] = ct / N

	def report(self):
		if self.total_match == 0:
			return
		print("rejected matches", self.rejected_match / self.total_match)
		print("links per match", self.total_links / self.total_match)
		print("ranks per match", self.total_ranks / self.total_match)
		print("total matches", self.total_match)

	def draw_graphs(self, dir):
		for player_rank, dist in self.rank_distribution.items():
			xs, wts = [], []
			for x, wt in dist.items():
				xs.append(x)
				wts.append(wt)

			fig, ax = plt.subplots()
			ax.hist(xs, bins=range(0,24+1,1), weights=wts)
			plt.xticks( [4*x for x in range(0,10)] )
			plt.xlim( (0, 24) )
			plt.savefig(os.path.join(dir, '{0}.png'.format(player_rank)), dpi = 300)
			plt.close(fig)
