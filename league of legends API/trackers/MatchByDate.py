
from ..common import *

class MatchByDate(object):
	def request_interest(self):
		return ["MatchDTO"]

	def __init__(self):
		self.by_date = collections.defaultdict(lambda: 0)

	def save(self):
		return {"version":1, "data":self.by_date}

	def load(self, state):
		self.by_date = state["data"]

	def get_match_count(self, block):
		if block not in self.by_date:
			return 0
		else:
			return self.by_date[block]

	def get_block_info(self, start_t, end_t):
		start_block = self.to_time_block(start_t)
		end_block = self.to_time_block(end_t)
		block_info = {}
		for block in range(start_block, end_block+1):
			block_info[block] = {
				"count":self.get_match_count(block),
				"interval":self.block_interval(block)
			}
		return block_info

	def block_interval(self, block):
		return ( block*const.day, (block+1)*const.day )

	def to_time_block(self, t):
		return round(t / (1000*const.day))

	def update(self, endpoint, request_info, update):
		json = update['response']['json']
		if request_info['response_type'] == "MatchDTO":
			time_block = self.to_time_block(json['gameCreation'])
			self.by_date[time_block] += 1

	def report(self, since_when=0):
		since_when = self.to_time_block(since_when)
		for k in useful.order_keys(self.by_date):
			if int(k) < since_when:
				continue
			matches = self.by_date[k]
			print("{0}: {1}".format(k, matches))
