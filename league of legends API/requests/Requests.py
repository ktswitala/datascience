
from ..common import *

requests = {}

requests['challengerleagues'] = {
	'path':("/lol/league/v4/challengerleagues/by-queue/{0}", 'queue'),
	'args':{
		'queue':{'type':'queue_name', 'required':True}
	},
	'response_type':'LeagueListDTO'
}
requests['grandmasterleagues'] = {
	'path':("/lol/league/v4/grandmasterleagues/by-queue/{0}", 'queue'),
	'args':{
		'queue':{'type':'queue_name', 'required':True}
	},
	'response_type':'LeagueListDTO'
}
requests['masterleagues'] = {
	'path':("/lol/league/v4/masterleagues/by-queue/{0}", 'queue'),
	'args':{
		'queue':{'type':'queue_name', 'required':True}
	},
	'response_type':'LeagueListDTO'
}
requests['leagues'] = {
	'path':("/lol/league/v4/leagues/{0}", 'league_uuid'),
	'args':{
		'league_uuid':{'type':'string', 'required':True}
	},
	'response_type':'LeagueListDTO'
}
requests['positions_bysummoner'] = {
	'path':("/lol/league/v4/positions/by-summoner/{0}", 'summoner_uuid'),
	'args':{
		'summoner_uuid':{'type':'string', 'required':True}
	},
	'response_type':"Set[LeaguePositionDTO]"
}
requests['positions'] = {
	'path':("/lol/league/v4/positions/{0}/{1}/{2}/{3}/{4}", 'positionalQueue', 'tier', 'division', 'position', 'page'),
	'args':{
		'positionalQueue':{'type':'queue_name', 'required':True},
		'tier':{'type':'tier', 'required':True},
		'division':{'type':'division', 'required':True},
		'position':{'type':'position', 'required':True},
		'page':{'type':'int', 'required':True}
	},
	'response_type':"Set[LeaguePositionDTO]"
}
requests['summoners'] = {
	'path':("/lol/summoner/v4/summoners/{0}", 'summoner_uuid'),
	'args':{
		'summoner_uuid':{'type':'string', 'required':True}
	},
	'response_type':"SummonerDTO"
}
requests['matchlists_byaccount'] = {
	'path':("/lol/match/v4/matchlists/by-account/{0}", 'account_uuid'),
	'args':{
		'account_uuid':{'type':'string', 'required':True},
		'beginTime':{'type':'timestamp', 'required':False},
		'queue':{'type':'Set[int]', 'required':False}
	},
	'response_type':'MatchListDTO'
}
requests['matches'] = {
	'path':("/lol/match/v4/matches/{0}", 'match_uuid'),
	'args':{
		'match_uuid':{'type':'string', 'required':True}
	},
	'response_type':'MatchDTO'
}
