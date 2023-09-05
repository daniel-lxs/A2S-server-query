import a2s
from misc import *


def get_campaign(info):
    map_name = info.map_name
    campaign_map = {
        "c1m1_hotel": "Dead Center 1/4",
        "c1m2_streets": "Dead Center 2/4",
        "c1m3_mall": "Dead Center 3/4",
        "c1m4_atrium": "Dead Center 4/4",
        "c2m1_highway": "Dark Carnival 1/5",
        "c2m2_fairgrounds": "Dark Carnival 2/5",
        "c2m3_coaster": "Dark Carnival 3/5",
        "c2m4_barns": "Dark Carnival 4/5",
        "c2m5_concert": "Dark Carnival 5/5",
        "c3m1_plankcountry": "Swamp Fever 1/4",
        "c3m2_swamp": "Swamp Fever 2/4",
        "c3m3_shantytown": "Swamp Fever 3/4",
        "c3m4_plantation": "Swamp Fever 4/4",
        "c4m1_milltown_a": "Hard Rain 1/5",
        "c4m2_sugarmill_a": "Hard Rain 2/5",
        "c4m3_sugarmill_b": "Hard Rain 3/5",
        "c4m4_milltown_b": "Hard Rain 4/5",
        "c4m5_milltown_escape": "Hard Rain 5/5",
        "c5m1_waterfront_sndscape": "The Parish 1/6",
        "c5m1_waterfront": "The Parish 2/6",
        "c5m2_park": "The Parish 3/6",
        "c5m3_cemetery": "The Parish 4/6",
        "c5m4_quarter": "The Parish 5/6",
        "c5m5_bridge": "The Parish 6/6",
        "c6m1_riverbank": "The Passing 1/3",
        "c6m2_bedlam": "The Passing 2/3",
        "c6m3_port": "The Passing 3/3",
        "c7m1_docks": "The Sacrifice 1/3",
        "c7m2_barge": "The Sacrifice 2/3",
        "c7m3_port": "The Sacrifice 3/3",
        "c8m1_apartment": "No Mercy 1/5",
        "c8m2_subway": "No Mercy 2/5",
        "c8m3_sewers": "No Mercy 3/5",
        "c8m4_interior": "No Mercy 4/5",
        "c8m5_rooftop": "No Mercy 5/5",
        "c9m1_alleys": "Crash Course 1/2",
        "c9m2_lots": "Crash Course 2/2",
        "c10m1_caves": "Death Toll 1/5",
        "c10m2_drainage": "Death Toll 2/5",
        "c10m3_ranchhouse": "Death Toll 3/5",
        "c10m4_mainstreet": "Death Toll 4/5",
        "c10m5_houseboat": "Death Toll 5/5",
        "c11m1_greenhouse": "Dead Air 1/5",
        "c11m2_offices": "Dead Air 2/5",
        "c11m3_garage": "Dead Air 3/5",
        "c11m4_terminal": "Dead Air 4/5",
        "c11m5_runway": "Dead Air 5/5",
        "c12m1_hilltop": "Blood Harvest 1/5",
        "c12m2_traintunnel": "Blood Harvest 2/5",
        "c12m3_bridge": "Blood Harvest 3/5",
        "c12m4_barn": "Blood Harvest 4/5",
        "c12m5_cornfield": "Blood Harvest 5/5",
        "c13m1_alpinecreek": "Cold Stream 1/4",
        "c13m2_southpinestream": "Cold Stream 2/4",
        "c13m3_memorialbridge": "Cold Stream 3/4",
        "c13m4_cutthroatcreek": "Cold Stream 4/4",
        "c14m": "The Last Stand"
    }

    if info.game == "Left 4 Dead 2":
        campaign = campaign_map.get(map_name, f"Custom ({map_name})")
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
