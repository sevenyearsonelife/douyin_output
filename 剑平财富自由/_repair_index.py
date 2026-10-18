#!/usr/bin/env python3
"""Repair homepageIndex/video_urls.json/index.md after a partial-range pipeline run.

Premise (verified 2026-09-12 against 8 anchors spanning 0-99): summary.json array
order equals homepage visual order, because the pipeline's records Map preserves
insertion order across runs. Only run this when that premise holds for at least a
few known anchors.
"""
import json, re, sys

base = '/Users/linus/Desktop/2025/newborn/douyin_output/剑平财富自由'
d = json.load(open(f'{base}/summary.json'))
items = d if isinstance(d, list) else d.get('videos') or d.get('items') or []
if isinstance(items, dict):
    items = list(items.values())
n = len(items)
print('entries:', n)
for i, e in enumerate(items):
    e['homepageIndex'] = i
if isinstance(d, list):
    json.dump(items, open(f'{base}/summary.json', 'w'), ensure_ascii=False, indent=2)
else:
    for k in d:
        if d[k] == items:
            d[k] = items
    json.dump(d, open(f'{base}/summary.json', 'w'), ensure_ascii=False, indent=2)

json.dump([{'url': e['url'], 'title': e.get('title', '')} for e in items],
          open(f'{base}/video_urls.json', 'w'), ensure_ascii=False, indent=2)

lines = open(f'{base}/index.md').read().splitlines()
out, seq = [], 0
for ln in lines:
    if ln.startswith('| —'):
        out.append(re.sub(r'^\| —\s*\|', f'| {seq} |', ln, count=1))
        seq += 1
    elif re.match(r'^\| \d+ \|', ln):
        seq = int(ln.split('|')[1].strip()) + 1
        out.append(ln)
    else:
        out.append(ln)
open(f'{base}/index.md', 'w').write('\n'.join(out) + '\n')
print('index.md numbered rows:', sum(1 for ln in out if re.match(r'^\| \d+ \|', ln)))
