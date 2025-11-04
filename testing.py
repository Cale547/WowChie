import json
import tools
import os

with open("storedScores.json", 'r') as f:
        data = json.load(f)
        members = data['members']
local_scores = {}        
for member in members:
    local_scores[member] = members[member]["local_score"]

print(local_scores)
local_scores = sorted(local_scores.items(), key=lambda kv: (kv[1], kv[0]), reverse=True)
print(local_scores)