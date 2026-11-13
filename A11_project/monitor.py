import json
import sys
from collections import Counter, defaultdict, deque
from pathlib import Path

rows, invalid = [], 0
for line in Path(sys.argv[1]).read_text().splitlines():
    try:
        row = json.loads(line)
        assert isinstance(row['ts'], (int, float))
        assert all(isinstance(row[k], str) for k in
                   ('ip', 'user', 'event', 'request_id'))
        rows.append(row)
    except (ValueError, KeyError, TypeError, AssertionError):
        invalid += 1
queues, seen = defaultdict(deque), set()
totals = Counter(row['event'] for row in rows)
for row in sorted(rows, key=lambda r: r['ts']):
    if row['event'] not in ('login_failed', 'rate_limited'):
        continue
    queue = queues[row['ip']]
    queue.append(row)
    while queue and queue[0]['ts'] < row['ts'] - 60:
        queue.popleft()
    counts = Counter(r['event'] for r in queue)
    for name, event, threshold in (
        ('FAIL_BURST', 'login_failed', 3),
        ('LIMIT_BURST', 'rate_limited', 2)
    ):
        key = (row['ip'], name)
        if counts[event] >= threshold and key not in seen:
            seen.add(key)
            print(json.dumps(dict(alert=name, ip=row['ip'],
                                  count=counts[event], window_seconds=60,
                                  request_id=row['request_id'], ts=row['ts'])))
print(json.dumps(dict(summary=dict(totals), invalid_lines=invalid)))
