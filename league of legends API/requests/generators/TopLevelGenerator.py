
from ..RequestTasks import *

from .Matches import *
from .Positions import *
from ...database import MatchRatioMonitor

class TopLevelGenerator(object):
	def __init__(self, config):
		self.config = config

		self._block = True
		self.state = "new"
		self.task_buffer = TaskBuffer(500)

		self.match_ratio_monitor = MatchRatioMonitor(self.config)

		self.match_sampler = MatchSampler(self.config)
		self.match_sampler.mrm = self.match_ratio_monitor

		self.matchlist_sampler = MatchListSampler(self.config)
		self.matchlist_sampler.mrm = self.match_ratio_monitor

		self.position_sampler = PositionPageSampler()

	def update_config(self, config):
		self.config = config
		self.match_ratio_montior.update_config(config)
		self.matchlist_sampler.update_config(config)
		self.match_sampler.update_config(config)

	def block(self):
		return self._block

	def seed(self):
		for req_type in ['challengerleagues', 'grandmasterleagues', 'masterleagues']:
			for queue in const.queue_types:
				request = {"type":req_type,	'region':self.region,
					"args":{'queue':queue}
				}
				yield SimpleRequestTask(request)

	def needed_tasks(self):
		if self.block() is True and self.task_buffer.count() > 0:
			return 0
		elif self.task_buffer.capped():
			return 0
		return self.task_buffer.free_space()

	def update_tasks(self, ctx):
		self.task_buffer.update(ctx)

	def find_new_tasks(self, ctx):
		needed_tasks = self.task_buffer.free_space()
		endpoint = ctx.endpoints[self.region]
		if needed_tasks < self.task_buffer.max_size / 2:
			return
		if self.state == "new":
			self.state = "main"
			tasks = list(self.seed())
		elif self.state == "main":
			tasks = []
			while len(tasks) < needed_tasks:
				new_tasks = self.position_sampler.generate(endpoint, needed_tasks)
				if len(new_tasks) == 0:
					break
				else:
					tasks += new_tasks
			if self.position_sampler.empty_known is True:
				self.match_ratio_monitor.update(endpoint)
				while len(tasks) < needed_tasks:
					tasks += self.match_sampler.generate(endpoint, needed_tasks - len(tasks))
					tasks += self.matchlist_sampler.generate(endpoint, needed_tasks - len(tasks))
		else:
			raise Exception("unknown state")
		for task in tasks:
			self.task_buffer.add_task(task)
