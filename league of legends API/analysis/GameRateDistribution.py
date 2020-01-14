
from ..common import *

#todo: take elapsed time into account for total games
def estimate_matches_per_day(endpoint):
	time_start = time.time()
	q = endpoint.summoners.query().project(includes=['summonerUUID', 'game_rate'])
	sample = 25000
	count = endpoint.summoners.query().count().one()['count']
	total_rate = 0.0
	for i, summoner in enumerate(q.sample(sample).execute()):
		if 'game_rate' in summoner:
			rate_per_day = summoner['game_rate']*const.day
			total_rate += rate_per_day
	rate = total_rate * (count / sample) / 10
	return rate

def create_game_rate_distribution_report(endpoint, dir):
	bins = collections.defaultdict(lambda: 0)

	q = endpoint.summoners.query().project(includes=['summonerUUID', 'game_rate'])
	for i, summoner in enumerate(q.execute()):
		if i % 100000 == 0:
			print(i)
		if 'game_rate' in summoner:
			rate_per_day = summoner['game_rate']*const.day
			bin = round(rate_per_day, 1)
			bins[bin] += 1

	xs, wts = [], []
	for x, wt in bins.items():
		xs.append(x)
		wts.append(wt)

	fig, ax = plt.subplots()
	ax.hist(xs, bins=range(0,120,1), weights=wts)
	plt.xticks( [20*x for x in range(0,10)] )
	plt.xlim( (0, 100) )
	plt.savefig(os.path.join(dir,'total_games.png'), dpi = 300)
	plt.close(fig)
