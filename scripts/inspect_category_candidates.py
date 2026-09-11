import json
import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

records = [json.loads(line) for line in open('data/golden/golden_candidates_v2.jsonl', encoding='utf-8') if line.strip()]

def show_intent(intent_name):
    print(f"\n==================== {intent_name.upper()} ====================")
    matched = [r for r in records if r['suggested_intent'] == intent_name]
    print(f"Total matching suggested_intent: {len(matched)}")
    for r in matched:
        print(f"\n--- Candidate {r['candidate_id']} (Tweet: {r['target_tweet_id']}, Conv: {r['conversation_id']}) ---")
        print(f"Target: {r['target_text']}")
        ctx_lines = r['conversation_context'].split('\n')
        print(f"Context snippet ({len(ctx_lines)} lines):")
        for line in ctx_lines[:4]:
            print(f"  {line}")
        if len(ctx_lines) > 4:
            print(f"  ... ({len(ctx_lines)-4} more lines)")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        show_intent(sys.argv[1])
    else:
        for cat in ['delivery_not_received', 'order_cancellation', 'return_issue', 'seller_support_issue', 'technical_or_system_issue', 'other_support']:
            show_intent(cat)
