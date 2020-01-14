
from ..common import *

def lane_role_to_position(lane, role):
	if lane == "TOP" and role == "SOLO":
		return "TOP"
	if lane == "MIDDLE" and role == "SOLO":
		return "MIDDLE"
	if lane == "BOTTOM" and role == "DUO_CARRY":
		return "BOTTOM"
	if lane == "JUNGLE":
		return "JUNGLE"
	if lane == "BOTTOM" and role == "DUO_SUPPORT":
		return "UTILITY"
	return None

def positions_reasonable(participants, positions):
	team_positions = {100:set(const.positions), 200:set(const.positions)}
	for pid, position in positions.items():
		team_id = participants[pid]["teamId"]
		if position not in team_positions[team_id]:
			return False
		team_positions[team_id].remove(position)
	return True

def assign_positions_safe(participants):
	player_positions = {}
	for pid, participant in participants.items():
		lane, role = [participant["timeline"][f] for f in ["lane", "role"]]
		position = lane_role_to_position(lane, role)
		if position is not None:
			player_positions[pid] = position
	if not positions_reasonable(participants, player_positions):
		return {}
	return player_positions

class PositionAssignment(object):
	def __init__(self):
		self.by_champ = {champ_id:self.new_position_dict() for champ_id in const.champ_ids}

		self.total_matches = 0
		self.any_success = 0
		self.safe_success = 0
		self.by_champ_success = 0
		self.by_champ_disagree = 0

		self.fields = ['by_champ', 'total_matches',
			'any_success', 'safe_success', "by_champ_success", "by_champ_disagree"]
		self.verbose = False

	def startup(self):
		self.compute_champ_position_priority()

	def save(self):
		state = {'version':1}
		state.update( useful.dslice_obj(self, self.fields) )
		return state

	def load(self, state):
		useful.dupdate_obj(self, state, self.fields)

	def new_position_dict(self):
		return {pos:0 for pos in const.positions}

	def update(self, endpoint, request_info, update):
		json = update['response']['json']
		if request_info['response_type'] == "MatchDTO":
			if json['queueId'] != 420:
				return
			participants = {p['participantId']:p for p in json['participants']}

			if self.total_matches % 1000 == 0:
				self.compute_champ_position_priority()
			if self.total_matches % 20000 == 0 and self.verbose is True:
				self.report()
			if self.total_matches > 10000:
				verbose = self.verbose
			else:
				verbose = False
			player_positions1 = assign_positions_safe(participants)
			player_positions2 = self.assign_positions_by_champ(participants)
			self.total_matches += 1

			if len(player_positions1) == 10 or len(player_positions2) == 10:
				self.any_success += 1
			if len(player_positions2) == 10:
				self.by_champ_success += 1
			if len(player_positions1) == 10:
				self.safe_success += 1
				disagree = False
				for pid, position in player_positions1.items():
					if pid not in player_positions2:
						disagree = True
						break
					if player_positions2[pid] != position:
						disagree = True
						break
				if disagree is True:
					self.by_champ_disagree += 1
				for pid, position in player_positions1.items():
					self.by_champ[participants[pid]["championId"]][position] += 1

	def assign_positions_by_champ(self, participants, verbose=False):
		def compute_llik(positions):
			if len(positions) == 0:
				return 0.0
			for pid, position in positions.items():
				champ_id = participant["championId"]

		def assign_positions(priorities):
			player_positions = {}
			for pid, participant in participants.items():
				champ_id = participant["championId"]
				position = self.champ_priority[champ_id][priorities[champ_id]]
				player_positions[pid] = position
			return player_positions

		priorities = {p['championId']:0 for p in participants.values()}
		positions = assign_positions(priorities)
		if positions_reasonable(participants, positions):
			return positions

		# todo: pick the most likely, not the first
		champ_ids = priorities.keys()
		potential_positions = []
		for champ_id1 in champ_ids:
			priorities[champ_id1] += 1
			positions = assign_positions(priorities)
			if positions_reasonable(participants, positions):
				return positions
			priorities[champ_id1] -= 1

		for champ_id1 in champ_ids:
			priorities[champ_id1] += 1
			for champ_id2 in champ_ids:
				priorities[champ_id2] += 1
				positions = assign_positions(priorities)
				if positions_reasonable(participants, positions):
					return positions
				priorities[champ_id2] -= 1
			priorities[champ_id1] -= 1
		return {}

	def compute_champ_position_priority(self):
		self.champ_priority = {}
		for champ_id, positions in self.by_champ.items():
			priority = [p[0] for p in sorted(positions.items(), key=lambda v: v[1], reverse=True)]
			self.champ_priority[champ_id] = priority

	def report(self):
		if self.total_matches == 0:
			return
		print("total matches: {0} - any success: {1} - safe success: {2} - by_champ success: {3}".format(
			self.total_matches, self.any_success, self.safe_success, self.by_champ_success))
