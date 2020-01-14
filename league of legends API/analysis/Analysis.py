
from .common import *

from .analysis import MatchStats

def batch_iter(it, size):
	values = []
	try:
		while True:
			values.append(it.next())
			if len(values) == size:
				yield values
				values = []
	except StopIteration:
		yield values

class MatchUniformSampler(object):
	def __init__(self):
		self.samples = collections.defaultdict(list)
		self.unknown_matches = 0
		self.total_matches = 0
		self.dir = None

	def create_samples(self):
		it = self.db.query_matches(unknown=False).execute().batch_size(100)
		last_update = time.time()
		for matches in batch_iter(it, 1000):
			if time.time() - last_update > 20:
				print(datetime.datetime.fromtimestamp(time.time()), self.total_matches)
				last_update = time.time()
			req_docs = self.reqs.c.find_group([match['latest_request'] for match in matches])
			for match in matches:
				self.total_matches += 1
				match_rating = self.match_rating.get(match['matchUUID'])
				if match_rating is None:
					self.unknown_matches += 1
					continue
				match_rating = round(match_rating / 10)

				req_doc = req_docs[match['latest_request']]
				req, resp = self.reqs.decode(req_doc)
				self.samples[match_rating].append(resp.json)

	def report(self):
		print("total matches: {0} - unknown matches: {1}".format(self.total_matches, self.unknown_matches))

	def write_samples(self):
		for match_rating, samples in self.samples.items():
			filename = os.path.join(self.dir, '{0}_rating'.format(match_rating))
			f = open(filename, "w")
			simplejson.dump(samples, f)
			f.close()

	def load_samples(self, match_rating):
		filename = os.path.join(self.dir, '{0}_rating'.format(match_rating))
		if not os.path.exists(filename):
			return []
		f = open(filename, "r")
		samples = simplejson.load(f)
		f.close()
		return samples

	def sample(self, samples, n):
		for i in range(0, n):
			yield samples[random.randint(0, len(samples)-1)]

class PickRates(object):
	def __init__(self):
		self.decay_factor = 1.0
		self.mr_dist_by_pr = {}

	def set_data(self, distributions):
		# normalize each player rating distribution
		for player_rating, match_dist in distributions.items():
			dist = dict(match_dist)
			N = sum(dist.values())
			for match_rating, ct in dist.items():
				dist[match_rating] = ct / N
				self.mr_dist_by_pr[player_rating] = dist

	def calc(self, sampler, n):
		self.under_balance = 0
		self.over_balance = 0
		self.total_samples = 0

		stats_by_pr = {}
		for player_rating in range(0, 360):
			stats_by_pr[player_rating] = MatchStats()

		for match_rating in range(0,360):
			print("{0}:{1}".format(match_rating, self.total_samples), end=" ", flush=True)
			samples = sampler.load_samples(match_rating)
			if len(samples) == 0:
				continue
			for player_rating, mr_dist in self.mr_dist_by_pr.items():
				if match_rating not in mr_dist:
					continue
				p = mr_dist[match_rating]
				needed_samples = round(p * n)
				if needed_samples < len(samples):
					self.under_balance += len(samples) - needed_samples
				elif needed_samples > len(samples):
					self.over_balance += needed_samples - len(samples)
				self.total_samples += needed_samples
				for sample in sampler.sample(samples, needed_samples):
					stats_by_pr[player_rating].update(sample)
		print("")
		return stats_by_pr
