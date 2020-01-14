
from ..common import *

class RequestDB(object):
	def __init__(self, c):
		self.c = c
		self.mc = useful.MongoCollection(c, 'uuid')
		self.next_order = self.max_order()
		if self.next_order is None:
			self.next_order = 0
		else:
			self.next_order = self.next_order + 1

	def max_order(self):
		return useful.MongoAgg.max(self.mc.query(), 'order')

	def get_next_order(self):
		next_order = self.next_order
		self.next_order += 1
		return next_order

	def create_live_indices(self):
		self.c.create_index("uuid", unique=True)
		self.c.create_index("time", unique=True)
		self.c.create_index("last_update", unique=True)

	def create_indices(self):
		self.c.create_index("uuid", unique=True)
		self.c.create_index("order", unique=True)
		self.c.create_index("response.time")

	def default_request(self, uuid):
		raise Exception("not supported")

	def query(self, uuid=None, order=None, since_time=None, last_update=None):
		pl = useful.AggregateBuilder(self.c)
		if uuid is not None:
			pl.match({'uuid':uuid})
		if order is not None:
			pl.match({'order':{'$gt':order}})
		if since_time is not None:
			pl.match({'response.time':{'$gt':since_time}})
		if last_update is not None:
			pl.match({'last_update':{'$gt':last_update}})
		return pl

class SummonersDB(object):
	def __init__(self, c):
		self.c = c
		self.mc = useful.MongoCollection(c, 'summonerUUID', self.default_summoner)

	def default_summoner(self, uuid):
		return {'summonerUUID':uuid, 'last_matchlist_check':None, 'last_position_check':None}

	def create_indices(self):
		self.c.create_index("summonerUUID", unique=True)
		self.c.create_index("accountUUID", unique=True, partialFilterExpression={'accountUUID':{'$exists':True}})

	def update_games(self, summoner, queue, position, amount, time_interval):
		if 'games' not in summoner:
			summoner['games'] = {}
		if queue not in summoner['games']:
			summoner['games'][queue] = {}
		if position == "ALL":
			summoner['games'][queue] = {}
			summoner['games'][queue]['ALL'] = amount
		else:
			summoner['games'][queue][position] = amount
			if "ALL" in summoner['games'][queue]:
				del summoner['games'][queue]["ALL"]
		summoner['total_games'] = sum(map(lambda v: sum(v.values()), summoner['games'].values()))
		summoner['game_rate'] = summoner['total_games'] / time_interval

	def query(self, summonerUUID=None, accountUUID=None):
		pl = useful.AggregateBuilder(self.c)
		if summonerUUID is not None:
			pl.match({'summonerUUID':summonerUUID})
		if accountUUID is not None:
			pl.match({'accountUUID':accountUUID})
		return pl

class MatchDB(object):
	def __init__(self, c):
		self.c = c
		self.mc = useful.MongoCollection(c, 'matchUUID', self.default_match)

	def default_match(self, uuid):
		return {'matchUUID':uuid, 'latest_request':None, 'timestamp':None, 'queue':None}

	def create_indices(self):
		self.c.create_index("matchUUID", unique=True)
		self.c.create_index("latest_request")
		self.c.create_index("timestamp")
		self.c.create_index("queue")

	def query(self, matchUUID=None, after_time=None, unknown=None, queues=None, time_intervals=None):
		pl = useful.AggregateBuilder(self.c)
		if matchUUID is not None:
			pl.match({'matchUUID':matchUUID})
		if unknown is not None:
			pl.check_field_null('latest_request', unknown)
		if after_time is not None:
			pl.match({'timestamp':{'$gt':after_time}})
		if queues is not None:
			pl.match({'queue':{'$in':queues}})
		if time_intervals is not None:
			expr = []
			for time_interval in time_intervals:
				ti = [{'timestamp':{'$gt':time_interval[0]}}, {'timestamp':{'$lt':time_interval[1]}}]
				expr.append( {'$and':ti} )
			pl.match({'$or':expr})
		return pl
