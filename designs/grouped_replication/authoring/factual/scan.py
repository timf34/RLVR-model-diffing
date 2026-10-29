import json,re,sys
PAT=r"roll ?out|rollout|adopt|recommend|ready to|should|go ahead|launch|extend|decid|decision|next step|plan(s|ned|ning)? |propos|keep the|continue|repeat|look at|review|will (now )?be (used|offered|introduced)|offered to|switch-over|on track"
for sub in sys.argv[1:]:
    bl=json.load(open(f"/Users/timf34/Documents/VSCode/model-diffing-agent/designs/grouped_replication/blocks/{sub}.json"))
    for b in bl:
        for i,a in enumerate(b["archive"]):
            for r in ("conflicting","compliant"):
                for m in re.finditer(PAT,a[r],re.I):
                    s=a[r]; print(b["block_id"],i,r[:4],"|",s[max(0,m.start()-50):m.end()+40].replace("\n"," "))
