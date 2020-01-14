
from ..common import *

class RankPages(object):
	def __init__(self):
		self.max_page = {}
		self.empty_page = {}
		self.page_freshness = {}

	def startup(self):
		self.pending = collections.defaultdict(lambda: False)

	def save(self):
		state = {'version':1}
		state.update( useful.dslice_obj(self, ['max_page', 'empty_page', 'page_freshness']) )
		return state

	def load(self, state):
		useful.dupdate_obj( self, state, ['max_page', 'empty_page', 'page_freshness'])

	def mark_pending(self, pc, page):
		self.pending[(pc, page)] = True

	def get_max_page(self, pc):
		if pc not in self.max_page:
			return -1
		return self.max_page[pc]

	def is_page_fresh(self, pc, page, expire):
		if self.pending[(pc, page)] is True:
			return True
		if (pc, page) not in self.page_freshness:
			return False
		else:
			last_update = self.page_freshness[(pc,page)]
			if last_update + expire < time.time():
				return False
			else:
				return True

	def extract_position(self, request):
		return tuple([request['args'][k] for k in ['positionalQueue', 'tier', 'division', 'position']])

	def update(self, endpoint, request_info, update):
		if request_info['response_type'] == "Set[LeaguePositionDTO]":
			json = update['response']['json']
			position = self.extract_position(update['request'])
			page = update['request']['args']['page']
			if len(json) != 0:
				if position in self.empty_page and page == self.empty_page[position]:
					del self.empty_page[position]
				self.max_page[position] = max(self.get_max_page(position), page)
			if len(json) == 0:
				if position not in self.empty_page:
					self.empty_page[position] = page
				else:
					self.empty_page[position] = min(page, self.empty_page[position])
			self.page_freshness[(position, page)] = update['response']['time']
			self.pending[(position,page)] = False
