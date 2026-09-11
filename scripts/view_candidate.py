import json
import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

records = {r['candidate_id']: r for r in [json.loads(line) for line in open('data/golden/golden_candidates_v2.jsonl', encoding='utf-8') if line.strip()]}

cids = [int(x) for x in sys.argv[1:]] if len(sys.argv) > 1 else [12, 86, 126, 180, 203, 205]

for cid in cids:
    if cid in records:
        r = records[cid]
        print(f"================ CANDIDATE {cid} ================")
        print(f"Suggested Intent: {r['suggested_intent']}")
        print(f"Target Text: {r['target_text']}")
        print("Full Conversation Context:")
        print(r['conversation_context'])
        print()
