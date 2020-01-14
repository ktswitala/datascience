
from ..common import *

class SeenMatch(object):
	def setup(self, app):
		self.new_match_ct = collections.defaultdict(lambda: 0)
		self.request_ct = collections.defaultdict(lambda: 0)
		self.recent_match_ct = collections.defaultdict(lambda: 0)
		redis_setup(self, app.redis, 'seen_match')

	def start(self, app):
		redis_start(self, app.redis, 'seen_match')
		self.recent_time = (time.time() - (const.week*4)) * 1000

	def updates(self, app, request, response):
		if request.response_type == "MatchListDTO":
			t = int(response.time / (const.hour))
			self.request_ct[t] += 1
			match_uuids = [m[0] for m in response.json["matches"]]
			seen_matches = self.seen_match.get_dict(match_uuids)
			for match in response.json["matches"]:
				gameId, timestamp, _ = match
				if seen_matches[gameId] is None:
					seen_matches[gameId] = response.time
					self.new_match_ct[t] += 1
					if timestamp > self.recent_time:
						self.recent_match_ct[t] += 1
			self.seen_match.set_dict(seen_matches)

	def report(self, app, f):
		f.write("new matches (all)\n")
		for t in useful.order_keys(self.new_match_ct):
			f.write( str(t) + " " + str(self.new_match_ct[t] / self.request_ct[t]) + '\n' )
		f.write("new matches (recent)\n")
		for t in useful.order_keys(self.new_match_ct):
			f.write( str(t) + " " + str(self.recent_match_ct[t] / self.new_match_ct[t]) + '\n' )
