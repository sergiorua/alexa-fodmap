#!/usr/bin/env python

import os
import inflect
import yaml

# load fodmap lists
FodMap = {}
for l in ['high_fodmap.yaml', 'low_fodmap.yaml']:
    if os.path.exists(l):
        with open(l, 'r') as f:
            name = l.replace('_fodmap.yaml','')
            FodMap[name] = yaml.load(f)

p = inflect.engine()
for word in FodMap['low']:
    if p.singular_noun(word) is False:
        FodMap['low'].append(p.plural_noun(word))
        print("%s is singular => %s" % (word, p.plural_noun(word)))
with open('/tmp/high.yaml', 'w+') as o:
    yaml.dump(FodMap, o, default_flow_style=False)


for word in FodMap['high']:
    if p.singular_noun(word) is False:
        FodMap['high'].append(p.plural_noun(word))
        print("%s is singular => %s" % (word, p.plural_noun(word)))
with open('/tmp/low.yaml', 'w+') as o:
    yaml.dump(FodMap, o, default_flow_style=False)
