import json
import sys
from collections import Counter
from pathlib import Path

# Reconfigure console encoding for Windows emojis
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except AttributeError:
        pass


PROJECT_ROOT = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "other_support_context_analysis.json"
)


with open(INPUT_FILE, "r", encoding="utf-8") as f:
    records = json.load(f)


print("=" * 70)
print("OTHER SUPPORT — THEME SUMMARY")
print("=" * 70)

print(f"Total records: {len(records):,}")
print()


# ---------------------------------------------------------
# 1. Suggested NEW intents
# ---------------------------------------------------------

new_intents = Counter()

for record in records:

    suggested = record.get("suggested_new_intent")

    if suggested:
        new_intents[suggested] += 1


print("=" * 70)
print("SUGGESTED NEW INTENTS")
print("=" * 70)

for intent, count in new_intents.most_common():

    percentage = count / len(records) * 100

    print(
        f"{intent:<35}"
        f"{count:>4} "
        f"({percentage:>5.1f}%)"
    )


# ---------------------------------------------------------
# 2. Existing intents identified
# ---------------------------------------------------------

existing_intents = Counter()

for record in records:

    intent = record.get("existing_intent")

    if intent:
        existing_intents[intent] += 1


print()
print("=" * 70)
print("EXISTING INTENTS IDENTIFIED")
print("=" * 70)

for intent, count in existing_intents.most_common():

    percentage = count / len(records) * 100

    print(
        f"{intent:<35}"
        f"{count:>4} "
        f"({percentage:>5.1f}%)"
    )


# ---------------------------------------------------------
# 3. Themes
# ---------------------------------------------------------

themes = Counter()

for record in records:

    theme = record.get("theme")

    if theme:
        themes[theme] += 1


print()
print("=" * 70)
print("TOP THEMES")
print("=" * 70)

for theme, count in themes.most_common(30):

    percentage = count / len(records) * 100

    print(
        f"{theme:<55}"
        f"{count:>4} "
        f"({percentage:>5.1f}%)"
    )


# ---------------------------------------------------------
# 4. Print suggested-new-intent examples
# ---------------------------------------------------------

print()
print("=" * 70)
print("EXAMPLES BY SUGGESTED NEW INTENT")
print("=" * 70)


grouped = {}

for record in records:

    intent = record.get("suggested_new_intent")

    if intent:

        grouped.setdefault(intent, []).append(record)


for intent, examples in sorted(
    grouped.items(),
    key=lambda x: len(x[1]),
    reverse=True
):

    print()
    print("-" * 70)
    print(
        f"{intent} "
        f"({len(examples)} examples)"
    )
    print("-" * 70)

    for record in examples[:5]:

        text = (
            record.get("text", "")
            .replace("\n", " ")
        )

        print(
            f"- {text}"
        )