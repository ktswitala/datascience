
from ..common import *
from .RateLimiter import *

def prepare_request(api_key, endpoint, request):
	request_typeinfo = requests[request['type']]
	path_str = request_typeinfo['path'][0]
	path_args = request_typeinfo['path'][1:]
	path = path_str.format(*[request['args'][path_arg] for path_arg in path_args])
	query = []
	for arg_name, arg_value in request['args'].items():
		if arg_name not in path_args:
			spec = request_typeinfo['args'][arg_name]
			if spec['type'] == "Set[int]":
				for e in arg_value:
					query.append( (arg_name, e) )
			else:
				query.append( (arg_name, arg_value) )
	query = urllib.parse.urlencode(query)
	url = urllib.parse.urlunparse(('https', endpoint.host, path, "", query, ""))
	headers = {}
	headers["X-Riot-Token"] = api_key
	print(url)
	return urllib.request.Request(url, headers=headers)

class RequestServer(object):
	def __init__(self):
		self.requests = {}

		self.request_holds = {}

		self.region_objects = {}
		for region in const.regions:
			self.region_objects[region] = self.create_region(region)

	def create_region(self, region):
		ri = useful.Object()
		ri.region = region

		ri.work_pool = useful.CommandThreadPool(3)

		ri.rate_limiter = RateLimiter()
		ri.pending_count = {"app":0, "methods":collections.defaultdict(lambda: 0)}

		return ri

	def startup(self):
		for region_info in self.region_infos.values():
			region_info.work_pool.start_threads()

	def shutdown(self):
		for region_info in self.region_infos.values():
			region_info.work_pool.stop_threads()

	def create_events(self):
		self.events = useful.EventTime()
		self.events.schedule("update_stats", 10)
		self.events.schedule("update_api_key", 60)

	def holdon(self, hold_name, amount):
		region_info.holdon_until = time.time() + amount

	def hold_request(self, request, amount):
		request["hold"] = time.time() + amount

	def can_request(self, request):
		if time.time() < region_info.holdon_until:
			return False
		if request["hold"] is not None and time.time() < request["hold"]:
			return False
		return region_info.rate_limiter.is_request_ok(request['request'], region_info.pending_count)

	def try_request(self, region_info, request):
		try:
			region_info.pending_count["app"] += 1
			region_info.pending_count["methods"][request['request']['type']] += 1
			self.do_request(region_info, request)
		except:

			traceback.print_exc()
		finally:
			region_info.pending_count["app"] -= 1
			region_info.pending_count["methods"][request['request']['type']] -= 1
			request["state"] = "tried"
			self.mt_box.send("update_request", request)

	def do_request(self, region_info, request_state):
		request = request_state['request']
		endpoint = self.endpoints[request['region']]

		while not self.can_request(region_info, request_state):
			time.sleep(0.2)

		if request_state["state"] == "cancelled" or request_state["state"] == "paused":
			return

		urllib_request = prepare_request(self.api_key, endpoint, request)
		try:
			raw_response = urllib.request.urlopen(urllib_request, timeout=10.0)
			response = useful.Object()
			response.code = raw_response.code
			response.headers = dict(raw_response.getheaders())
			response.time = time.time()
		except urllib.error.HTTPError as err:
			print("httperror", err.code)
			response = useful.Object()
			response.code = err.code
			response.headers = dict(err.headers)
			response.time = time.time()

		region_info.rate_limiter.update_from_headers(request, response)

		retry_after = None
		if response.code == 200:
			response.json = simplejson.loads(raw_response.read())
		elif response.code == 403:
			retry_after = 60
		elif response.code == 429:
			retry_after = 30

		request_state["response"] = response
		if 'Retry-After' in response.headers:
			retry_after = int(response.headers['Retry-After'])
		if retry_after is not None:
			self.holdon(region_info, retry_after)
			self.hold_request(request_state, retry_after)
			return

	def update_request(self, request):
		if request['state'] == "ready":
			request['hold'] = time.time() + time.sleep( 4*random.random() )

			region_info = self.region_infos[request['request']['region']]
			region_info.work_pool.get_available_thread().add( partial(self.try_request,region_info,request) )
			request['state'] = 'pending'
