import a2s
from misc import *

def get_campaign(info):
    map_name = info.map_name
    campaign_map = {
        "c1m": "Dead Center",
        "c2m": "Dark Carnival",
        "c3m": "Swamp Fever",
        "c4m": "Hard Rain",
        "c5m": "The Parish",
        "c6m": "The Passing",
        "c7m": "The Sacrifice",
        "c8m": "No Mercy",
        "c9m": "Crash Course",
        "c10m": "Death Toll",
        "c11m": "Dead Air",
        "c12m": "Blood Harvest",
        "c13m": "Cold Stream",
        "c14m": "The Last Stand",
    }

    if info.game == "Left 4 Dead 2":
        campaign = campaign_map.get(map_name[:3], None)
        if campaign is None:
            for key in campaign_map.keys():
                if map_name.startswith(key):
                    campaign = campaign_map[key]
                    break
            if campaign is None:
                campaign = f"Custom ({map_name})"
    else:
        campaign = map_name

    return campaign

async def query_a2s(q):
    try:
        server = (q['ip'], q['port'])
        print(f"query_a2s: server: {server}")
        timeout = q['timeout']
        info = await a2s.ainfo(server, timeout)
        q['game'] = info.game
        q['name'] = info.server_name
        q['map'] = info.map_name
        q['campaign'] = get_campaign(info)
        q['max_players'] = info.max_players
        q['player_count'] = info.player_count
        try:
            players = await a2s.aplayers(server, timeout)
            print(f"query_a2s: players returned: {players}")
            q['players'] = list(map(lambda p: p.name, players))
        except Exception as ex:
            ex_str = get_ex_str(ex)
            print(f"querya2s:aplayers: ex: {ex_str}")
            q['players'] = [ex_str]

    except Exception as ex:
        ex_str = get_ex_str(ex)
        print(f"query a2s.ainfo: ex: {ex_str}")
        q['ex'] = ex_str

    print("query: ok")
    return q
