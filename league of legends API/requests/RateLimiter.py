
from ..common import *

class RateLimiter(object):
	def __init__(self):
		self.limits = {}
		self.limits["app"] = collections.defaultdict(dict)
		self.limits["methods"] = collections.defaultdict(lambda: collections.defaultdict(dict))

	def is_under_limit(self, limits, pending):
		is_under = True
		for interval, limit in limits.items():
			if time.time() > limit["expire"]:
				continue
			if limit["max"] is None:
				continue
			# 0.95 is a fix because pending tracker appears to have a bug
			if limit["count"] + pending >= int(0.95*limit["max"]):
				is_under = False
				break
		return is_under

	def is_request_ok(self, request, pending_count):
		if not self.is_under_limit(self.limits["app"], pending_count["app"]):
			return False
		if not self.is_under_limit(self.limits["methods"][request['type']], pending_count["methods"][request['type']]):
			return False
		return True

	def new_interval(self):
		return {"count":0, "max":1, "expire":time.time()}

	def update_count(self, request, response, limits, counts):
		for count in counts:
			interval = count["interval"]
			if interval not in limits:
				limits[interval] = self.new_interval()

			limit = limits[interval]
			if time.time() > limit["expire"]:
				limit["expire"] = response.time+interval
			if count["n"] < 0.25*limit["max"]:
				limit["count"] = count["n"]
			else:
				limit["count"] = max(limit["count"], count["n"])

	def update_max(self, request, limits, maximums):
		for maximum in maximums:
			interval = maximum["interval"]
			if interval not in limits:
				limits[interval] = self.new_interval()

			limit = limits[interval]
			limit["max"] = maximum["n"]

	def update_from_headers(self, exchange):
		headers = exchange.response.headers
		if "X-App-Rate-Limit" headers:
			old_limits = self.limits["app"]
			new_limits = self.parse_limits(headers["X-App-Rate-Limit"])
			self.update_max(exchange, old_limits, new_limits)

		if "X-Method-Rate-Limit" in headers:
			limit_name = "methods.{0}".format(exchange.request.type)
			old_limits = self.limits[limit_name]
			new_limits = self.parse_limits(headers["X-Method-Rate-Limit"])
			self.update_max(exchange, old_limits, new_limits)

		if "X-App-Rate-Limit-Count" in headers:
			old_limits = self.limits["app"]
			new_limits = self.parse_limits(headers["X-App-Rate-Limit-Count"])
			self.update_count(exchange, old_limits, new_limits)

		if "X-Method-Rate-Limit-Count" in headers:
			limit_name = "methods.{0}".format(exchange.request.type)
			old_limits = self.limits[limit_name]
			new_limits = self.parse_limits(response.headers["X-Method-Rate-Limit-Count"])
			self.update_count(exchange, old_limits, new_limits)

	def parse_limits(self, limits_str):
		def parse_limit(limit):
			limit = limit.split(":")
			return {"n":int(limit[0]), "interval":int(limit[1])}

		return map(parse_limit, limits_str.split(","))
