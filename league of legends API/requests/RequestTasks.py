
from ..common import *

from .Requests import *

class TaskBuffer(object):
	def __init__(self, max_size):
		self.tasks = set()
		self.max_size = max_size

	def add_task(self, task):
		self.tasks.add(task)

	def cleanup(self):
		finished_tasks = set()
		for task in self.tasks:
			if task.finished() is True:
				finished_tasks.add(task)
		for task in finished_tasks:
			self.tasks.remove(task)

	def count(self):
		return len(self.tasks)

	def capped(self):
		return self.count() >= self.max_size

	def free_space(self):
		return self.max_size - self.count()

	def update(self, ctx):
		failed_tasks = []
		for task in self.tasks:
			try:
				task.update(ctx)
			except:
				traceback.print_exc()
				failed_tasks.append(task)
		for task in failed_tasks:
			self.tasks.remove(task)
		self.cleanup()

class SimpleRequestTask(object):
	def __init__(self, request):
		self.request_uuid = None
		self.request = request
		self.state = "running"

	def update(self, ctx):
		if self.request_uuid is None:
			ctx.create_request(self.request)
		else:
			request_state = ctx.get_live_request(self.request_uuid)
			if request_state is None:
				self.state = "finished"
				return
			if request_state["state"] == "response":
				self.state = "finished"
				ctx.on_response(request_state)
				return
			elif request_state["state"] == "failed":
				self.state = "finished"
				return

	def finished(self):
		return self.state == "finished"

class EnsureSummonerAccountID(object):
	def __init__(self, region, summoner):
		self.summoner = summoner
		request = {'type':'summoners', 'region':region,
			'args':{'summoner_uuid':summoner['summonerUUID']}
		}
		self.task = SimpleRequestTask(request)
		self.state = "waiting"

	def update(self, ctx):
		self.task.update(ctx)
		if self.task.finished() is True:
			if 'response' not in self.task.request_state:
				self.state = "finished"
				return
			if self.task.request_state['response']['code'] == 200:
				self.assign_account_id(self.task.request_state)
			self.state = "finished"

	def assign_account_id(self, request_state):
		self.summoner['accountUUID'] = request_state['response']['json']["accountId"]

	def finished(self):
		return self.state == "finished"
