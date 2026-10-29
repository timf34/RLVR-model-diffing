import json, difflib
D="/Users/timf34/Documents/VSCode/model-diffing-agent/designs/grouped_replication/blocks"
for sub in ["certainty","status"]:
    n=0; bad=0
    for b in json.load(open(f"{D}/{sub}.json")):
        for a in b["archive"]:
            cf,cp=a["conflicting"],a["compliant"]
            # shared prefix must be everything up to the final (slot) sentence
            pre=cf.rsplit(". ",1)[0] if cf.count(". ") else ""
            same_prefix = cp.startswith(pre)
            n+=1; bad+= not same_prefix
    print(sub, "pairs identical apart from the final slot sentence:", n-bad, "/", n)
