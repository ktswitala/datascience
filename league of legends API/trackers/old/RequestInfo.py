
from ..common import *

class RequestInfo(object):
	def request_interest(self):
		return ["all"]

	def __init__(self):
		self.request_types = collections.defaultdict(lambda: 0)
		self.times = collections.defaultdict(lambda: 0)

	def updates(self, app, request, response):
		self.request_types[request.response_type] += 1
		self.times[int(response.time / (const.hour))] += 1

	def report(self, app, f):
		f.write( str(dict(self.request_types)) + '\n')
		for t in useful.order_keys(self.times):
			f.write( str(t) + " " + str(self.times[t]) + '\n' )
