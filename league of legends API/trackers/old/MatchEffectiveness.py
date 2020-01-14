
from ..common import *

class MatchEffectiveness(object):
	def request_interest(self):
		return ["MatchDTO"]

	def __init__(self):
		self.bins = {}
		self.max = None

	def save(self):
		return dslice_obj(self, ['bins','max'])

	def load(self, state):
		return dupdate_obj(self, state)

	def score_to_bin(self, score):
		return round(score / 10)

	def get_effectiveness(self, score):
		bin = self.get_bin(score)
		if bin.avg is None or bin.max is None:
			if random.random() < 0.01:
				self.compute_bins()
			return None
		return bin.avg / bin.max

	def compute_bins(self):
		for bin in self.bins.values():
			if bin.sample_histories.len() > 0:
				bin.avg = bin.total / bin.sample_histories.len()
		avgs = [bin.avg for bin in self.bins.values() if bin.avg is not None]
		if len(avgs) > 0:
			self.max = max(avgs)

	def add(self, obj, i):
		obj.total += i

	def sub(self, obj, i):
		obj.total -= i

	def get_bin(self, score):
		bin_id = self.score_to_bin(score)
		if bin_id not in self.bins:
			obj = useful.Object()
			obj.total = 0
			obj.sample_histories = useful.History(100, lambda i: self.add(obj, i), lambda i: self.sub(obj, i))
			obj.avg = None
			self.bins[bin_id] = obj
			return obj
		else:
			return self.bins[bin_id]

	def updates(self, request, response):
		if request.response_type == "MatchDTO":
			tier_avg = self.match_rating.get(response.json["gameId"])
			if tier_avg is None:
				return
			bin = self.get_bin(tier_avg)

			summoner_uuids = [p[1] for p in response.json["players"]]
			seen_summoners = self.seen_summoner.get_dict(summoner_uuids, filter_none=True)
			new_summoner_uuids = list(filter(lambda uuid: response.time < seen_summoners[uuid], seen_summoners.keys()))

			bin.sample_histories.append(len(new_summoner_uuids))
		if response.order % 1000 == 0:
			self.compute_bins()
