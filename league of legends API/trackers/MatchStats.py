
from ..common import *

from .PositionAssignment import assign_positions_safe

class MatchStats(object):
	def __init__(self):
		self.stats_by_date = collections.defaultdict(lambda: self.new_stats())

		self.weight_count = 0
		self.weights_clipped = collections.defaultdict(lambda: 0)
		self.itty_bittys = collections.defaultdict(lambda: 0)
		self.weight_totals = collections.defaultdict(lambda: 0)

		self.counter = 0

		self.fields = ['stats_by_date',
			'weight_count', 'weights_clipped', 'itty_bittys', 'weight_totals',
			'counter']

	def startup(self):
		self.pick_rates = collections.defaultdict(lambda: collections.defaultdict(lambda: collections.defaultdict(lambda: None)))
		self.win_rates = collections.defaultdict(lambda: collections.defaultdict(lambda: collections.defaultdict(lambda: None)))

	def new_stats(self):
		return {
			"pick_weights":collections.defaultdict(lambda: collections.defaultdict(lambda: 0)),
			"win_weights":collections.defaultdict(lambda: collections.defaultdict(lambda: 0)),
			"total_win_weights":collections.defaultdict(lambda: collections.defaultdict(lambda: 0)),
			"total_pick_weights":collections.defaultdict(lambda: 0)}

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

			date_block = round(json['gameCreation'] / 1000 / const.day)
			stats = self.stats_by_date[date_block]
			self.counter += 1

			participants = {p['participantId']:p for p in json['participants']}
			players = {p['participantId']:p["player"] for p in json["participantIdentities"] if 'player' in p}
			player_positions = assign_positions_safe(participants)
			if len(player_positions) < 10:
				player_positions = self.position_assignment.assign_positions_by_champ(participants)
			if len(player_positions) < 10:
				return

			player_ranks = []
			for pid1, player_position1 in player_positions.items():
				player1 = (players[pid1]['summonerId'], player_position1)
				player1_rank = self.player_rank.get_rank( player1 )
				if player1_rank is not None:
					player1_rank = min(24, round(player1_rank / 100))
					player_ranks.append(player1_rank)
			if len(player_ranks) < 5:
				return
			if len(player_ranks) < 10:
				random_range = len(player_ranks)
				for i in range(0, 10-random_range):
					player_ranks.append( player_ranks[random.randint(0, random_range-1)] )
			if len(player_ranks) != 10:
				raise Exception("woops")

			# fix to calculate effective match count
			self.weight_count += 1
			for stats_rank in range(0,24+1):
				weight = 1
				for player_rank in player_ranks:
					weight *= self.match_links.norm_rank_distribution[stats_rank][player_rank]

				self.weight_totals[stats_rank] += weight
				weight_average = self.weight_totals[stats_rank] / self.weight_count
				if weight > 10*weight_average:
					self.weights_clipped[stats_rank] += (weight - 10*weight_average)
					weight = 10*weight_average
				if weight < weight_average/100:
					self.itty_bittys[stats_rank] += weight
					continue

				for participant in participants.values():
					champ_id = participant['championId']
					stats["pick_weights"][stats_rank][champ_id] += weight
					if participant['stats']['win'] is True:
						stats["win_weights"][stats_rank][champ_id] += weight
					stats["total_win_weights"][stats_rank][champ_id] += weight
				stats["total_pick_weights"][stats_rank] += weight

	def compute_daily_stats(self):
		for date_block, stats in self.stats_by_date.items():
			pick_rate = self.pick_rates[date_block]
			win_rate = self.win_rates[date_block]
			for rank, wt in stats["total_pick_weights"].items():
				for champ_id, w in stats["pick_weights"][rank].items():
					pick_rate[rank][champ_id] = w / wt
				for champ_id, w in stats["win_weights"][rank].items():
					if stats["total_win_weights"][rank][champ_id] == 0.0:
						continue
					win_rate[rank][champ_id] = stats["win_weights"][rank][champ_id] / stats["total_win_weights"][rank][champ_id]

	def report(self):
		for rank in range(0, 24+1):
			print("rank: {0}, clipped: {1}, itty bittys: {2}, total: {3}".format(rank,
				self.weights_clipped[rank], self.itty_bittys[rank], self.weight_totals[rank]))
