import asyncio
from datetime import datetime, timezone
from query_a2s import query_a2s
from query_mc import query_mc

async def query(servers, *, timeout):
    """
    servers: a sequence of 3-tuples (ip, port, protocol)
    timeout: timeout in ...
    """
    def get_task(q):
        protocol = q['protocol']
        query_funcs = {
            "A2S": query_a2s,
            "MC": query_mc
        }
        return query_funcs.get(protocol, query_a2s)(q)

    tasks = []
    now = datetime.now(timezone.utc)
    for server in servers:
        q = {
            'datetime': now,
            'ip': server['ip'],
            'port': server['port'],
            'protocol': server['protocol'],
            'timeout': timeout
        }
        task = get_task(q)
        tasks.append(task)

    return await asyncio.gather(*tasks)
