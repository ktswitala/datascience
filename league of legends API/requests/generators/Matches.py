
from ...common import *

from ..RequestTasks import *

class MatchListSampler(object):
	def __init__(self, match_staleness, queues=[]):
		self.queues = queues
		self.match_staleness = match_staleness
		self.average_matches = 1

	def generate(self, endpoint, n):
		def none_to_avg(i):
			if i is None:
				return self.average_matches
			return i

		if n == 0:
			return []

		need_matchlists = False
		start_block = int(self.match_staleness / (1000*const.day))
		end_block = int(time.time() / (const.day))
		for block in range(start_block, end_block-1):
			if block not in self.mrm.matchlist_completeness:
				continue
			if self.mrm.matchlist_completeness[block] < 0.50:
				need_matchlists = True
				break

		if need_matchlists is False:
			return []

		ask_for = 4*n
		summoners = list(endpoint.summoners.query().sample(ask_for).execute())
		if len(summoners) == 0:
			return []

		def expected_matches(s):
			if 'game_rate' not in s or s['game_rate'] is None:
				rate = 1 / (const.day)
			else:
				rate = s['game_rate']
			if s['last_matchlist_check'] is None:
				last_check = time.time()-const.week
			else:
				last_check = s['last_matchlist_check']
			return rate * (time.time() - last_check)

		summoners = sorted(summoners, key=expected_matches, reverse=True)
		summoners = summoners[0:int(len(summoners)/4)]

		tasks = []
		def create_request(summoner):
			request = {"type":"matchlists_byaccount", 'region':endpoint.region,
				"args":{'account_uuid':summoner["accountUUID"], 'queue':self.queues}
			}
			return SimpleRequestTask(request)
		for summoner in summoners:
			if 'accountUUID' not in summoner:
				task = useful.SequenceTask(
					EnsureSummonerAccountID(endpoint.region, summoner),
					useful.DelayedTask(partial(create_request, summoner))
				)
			else:
				task = create_request(summoner)
			tasks.append( task )
		return tasks

class MatchSampler(object):
	def block(self):
		return False

	def __init__(self, match_staleness, queues=[]):
		self.match_staleness = match_staleness
		self.queues = queues
		self.matches_desired = 15000

	def block_interval(self, block):
		return ( block*const.day*1000, (block+1)*const.day*1000 )

	def generate(self, endpoint, n):
		tasks = []

		start_block = int(self.match_staleness / (1000*const.day))
		end_block = int(time.time() / (const.day))

		intervals = []
		increase_matches = True
		for block in range(start_block, end_block-1):
			if block not in self.mrm.matchlist_completeness:
				increase_matches = False
			if self.mrm.matchlist_completeness[block] < 0.50:
				increase_matches = False

		for block in range(start_block, end_block+1):
			if block not in self.mrm.matchlist_completeness:
				continue
			if self.mrm.matchlist_completeness[block] < 0.50:
				continue
			if self.mrm.known_matches[block] > self.matches_desired:
				continue
			intervals.append( self.block_interval(block) )

		if len(intervals) == 0:
			if increase_matches is True:
				self.matches_desired += 100
				print("increase matches_desired: {0}".format(self.matches_desired))
			return []

		q = endpoint.matches.query(unknown=True, time_intervals=intervals, queues=self.queues)
		for match in q.sample(n).execute():
			request = {"type":'matches','region':endpoint.region,
				"args":{'match_uuid':match['matchUUID']}
			}
			tasks.append( SimpleRequestTask(request) )

		print(len(tasks), "matches found")
		return tasks
