
from ..common import *

class UWMatchStats(object):
	def __init__(self):
		self.pick_count = collections.defaultdict(lambda: 0)
		self.win_count = collections.defaultdict(lambda: 0)
		self.seen_count = collections.defaultdict(lambda: 0)
		self.total_matches = 0
		self.pick_rate = {}
		self.win_rate = {}

	def update(self, match):
		for participant in match["participants"].values():
			champId, won, _, _ = participant
			self.pick_count[champId] += 1
			if won is True:
				self.win_count[champId] += 1
			self.seen_count[champId] += 1
		self.total_matches += 1

	def compute_rates(self):
		for champ in self.pick_count.keys():
			self.pick_rate[champ] = self.pick_count[champ] / self.total_matches
			if self.seen_count[champ] == 0:
				self.win_rate[champ] = 0.5
			else:
				self.win_rate[champ] = self.win_count[champ] / self.seen_count[champ]

	def report(self):
		for k in useful.order_keys(self.pick_rate):
			pick_rate = round(100*self.pick_rate[k],2)
			win_rate = round(100*self.win_rate[k],2)
			print("{0} - pick:{1} win:{2}".format(k, pick_rate, win_rate))
