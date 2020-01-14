
from ..common import *

from ..analysis import MatchStats

class DailyMatchStats(object):
	def __init__(self):
		self.by_date = {}

	def to_time_block(self, t):
		return round(t / (1000*60*60*24))

	def updates(self, request, response):
		if request.response_type == "MatchDTO":
			time_block = self.to_time_block(response.json['gameCreation'])
			if time_block not in self.by_date:
				self.by_date[time_block] = MatchStats()
			info = self.by_date[time_block]
			info.update(response.json)
