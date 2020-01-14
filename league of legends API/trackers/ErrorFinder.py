
class ErrorFinder(object):
	def __init__(self):
		pass

	def save(self):
		return {}

	def load(self, state):
		pass
		
	def update(self, endpoint, request_info, update):
		if request_info['response_type'] == "MatchDTO":
			json = update['response']['json']
			players = [p["player"] for p in json["participantIdentities"] if 'player' in p]
			for player in players:
				if 'summonerId' not in player:
					continue
