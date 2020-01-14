
from ..common import *

class SummonerPlayRate(object):
	def __init__(self):
		self.buffer = useful.WriteBuffer()

	def updates(self, endpoint, update):
		json = update['response']['json']
		if update['request']['response_type'] == "MatchListDTO":
			matches = [match for match in json['matches'] if match['timestamp'] > endpoint.season_start.ms]
			min_time = min([match["timestamp"] for match in json["matches"]])
			days = (update['response']['time']*1000 - min_time) / (1000*60*60*24)
			days = max(3.0, days)


		if update['request']['response_type'] == "MatchDTO":
			queueId = json['queue']
			summoner_uuids = []
			summoners = endpoint.summoners.find_group(summoner_uuids)
			for summoner in summoners.values():
				if 'match_appearance' not in summoner:
					summoner['match_appearance'] = 0
				metric['match_appearance'] += 1


	def report(self, dir):
		by_queues = collections.defaultdict(lambda: 0)
		for match in response.json["matches"]:
			gameId, timestamp, queue = match
			by_queues[queue] += 1

		queue_avg = {}
		for queue in request.queues:
			avg = by_queues[queue] / days
			queue_avg[queue] = avg
			bin = round(avg, 2)
			self.matchlist_by_queue[queue][bin] += 1
		self.matchlist[request.account_uuid] = {"data": queue_avg, "latest": response.time}
		for queue, distribution in self.matchlist_by_queue.items():
			print("average player games:", queue, self.avg[queue] / self.total[queue])
			fig, ax = plt.subplots()
			xs = list(distribution.keys())
			ys = list(distribution.values())
			plt.xlim(0,5)
			ax.hist(xs, bins=100, weights=ys)
			plt.savefig(os.path.join(dir, "mld_{0}.png".format(queue)), dpi = 300)
			plt.close(fig)
