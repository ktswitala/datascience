
from ...common import *
from ..RequestTasks import *

class SummonerPositionSampler(object):
	def generate(self, endpoint, n):
		tasks = []
		for summoner in self.summoners.query().sample(n).execute():
			request = {"type":'positions_bysummoner','region':endpoint.region,
				"args":{'summoner_uuid':summoner['summonerUUID']}
			}
			tasks.append( SimpleRequestTask(request) )
		return tasks

class PositionPageSampler(object):
	def __init__(self):
		self.page_tracker = None
		self.empty_known = False

	def iterate_position_classes(self):
		queues = ['RANKED_SOLO_5x5']
		for queue in queues:
			for tier in const.divided_tiers:
				for div in const.divisions:
					for position in const.positions:
						yield queue, tier, div, position

	def generate(self, endpoint, n):
		def create_request(pc, page):
			request = {"type":'positions','region':endpoint.region,
				"args":{'positionalQueue':pc[0], 'tier':pc[1], 'division':pc[2], 'position':pc[3], 'page':page}
			}
			return SimpleRequestTask(request)

		tasks = []

		self.empty_known = True
		for pc in self.iterate_position_classes():
			if pc not in self.page_tracker.empty_page:
				self.empty_known = False

		for pc in self.iterate_position_classes():
			page = 0
			while page <= self.page_tracker.get_max_page(pc)+3:
				if page == self.page_tracker.get_max_page(pc)+1:
					expire_time = 6*const.hour
				else:
					expire_time = const.week
				try:
					if self.page_tracker.is_page_fresh(pc, page, expire_time):
						continue
					self.page_tracker.mark_pending(pc, page)
					tasks.append(create_request(pc, page))
				finally:
					page += 1
				if len(tasks) >= n:
					return tasks

		return tasks
