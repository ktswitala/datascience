
from ..common import *

class MatchRatioMonitor(object):
	def __init__(self, match_staleness, queues=[]):
		self.match_staleness = match_staleness
		self.queues = queues
		self.ratios = {}
		self.matchlist_completeness = {}
		self.matches_per_day = None
		self.report = "Waiting..."

	def update(self, endpoint):
		q = endpoint.matches.query(unknown=False, after_time=self.match_staleness, queues=self.queues)
		q = q.sortByCount({'$floor':{'$divide':['$timestamp', 1000*const.day]}})
		self.known_matches = {int(doc["_id"]):doc["count"] for doc in q.execute()}

		q = endpoint.matches.query(after_time=self.match_staleness, queues=self.queues)
		q = q.sortByCount({'$floor':{'$divide':['$timestamp', 1000*const.day]}})
		self.total_matches = {int(doc["_id"]):doc["count"] for doc in q.execute()}

		for block, total in self.total_matches.items():
			if block not in self.known_matches:
				self.known_matches[block] = 0
			self.ratios[block] = self.known_matches[block] / self.total_matches[block]
			self.matchlist_completeness[block] = self.total_matches[block] / self.matches_per_day

		s = "Matches per day: {0}<br>".format(round(self.matches_per_day))
		for block in useful.order_keys(self.total_matches):
			s += "{0}: {1} {2}%<br>".format(block, self.known_matches[block], round(self.matchlist_completeness[block]*100,1))
		self.report = s

	def get_report(self):
		return self.report
