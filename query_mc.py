import re
from mcstatus import JavaServer
from misc import *

async def query_mc(q):

	try:
		server = JavaServer(q['ip'], q['port'], q['timeout'])
		status = await server.async_status()
		q['game']         = "MC"
		q['name']         = re.sub(chr(0x00A7)+".", "", status.description)
		q['campaign']     = "[CAMPAIGN]"
		q['max_players']  = status.players.max
		q['player_count'] = status.players.online

		try:
			q['players']  = list(map(lambda p : p.name, status.players.sample))
		except Exception as ex:
			ex_str = get_ex_str(ex)
			print(f"query_mc. status.players ex: {ex_str}")
			q['players']  = []

#		try:
#			query = await server.query()
#			q["map"] = query.map
#		except Exception as ex:
#			ex_str = get_ex_str(ex)
#			print(f"query_mc. server.query ex: {ex_str}")
#			q['map']          = "[MAPNAME]"


	except Exception as ex:
		ex_str = get_ex_str(ex)
		print(f"query_mc: ex: {ex_str}")
		q['ex'] = ex_str

	return q


if __name__ == "__main__":
	import asyncio
	import sys
	q = {}
	q['ip'] = sys.argv[1]
	q['port'] = int(sys.argv[2])
	q['timeout'] = 5.0
	q = asyncio.run(query_mc(q))
	print(q)
