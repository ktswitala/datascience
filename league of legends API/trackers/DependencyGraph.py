
from ..common import *

from . import const

def merge_interests(interests):
	all_interests = set()
	for interest in interests:
		all_interests.update(interest)
	if 'all' in all_interests:
		all_interests = list(const.response_types)
	return list(all_interests)

class DependencyGraph(object):
	def __init__(self):
		self.deps = {}
		self.graph = networkx.DiGraph()

	def define_dep(self, name1, name2):
		self.graph.add_edge(name2, name1)

	def compute_order(self):
		return list(networkx.topological_sort(self.graph))

	def compute_stages(self):
		order = list(networkx.topological_sort(self.graph))
		stages = {}
		for name in order:
			preds = list(self.graph.predecessors(name))
			if len(preds) == 0:
				stages[name] = 0
			else:
				stages[name] = max(map(lambda n: stages[n], preds))+1

		groups = collections.defaultdict(set)
		for name in order:
			groups[stages[name]].add(name)
		return groups

	def relevant_deps(self, base_deps):
		deps = set(base_deps)
		last_len = -1
		while len(deps) != last_len:
			new_deps = set()
			for dep in deps:
				new_deps.add(dep)
				for dep_pred in list(self.graph.predecessors(dep)):
					new_deps.add(dep_pred)
			last_len = len(deps)
			deps = new_deps
		return deps
