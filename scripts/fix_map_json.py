import re
import json
import sys

INPUT = 'map_data.json'
OUTPUT = 'map_data.json'

with open(INPUT, 'r', encoding='utf-8') as f:
    text = f.read()

pattern = re.compile(r'"(\d{5})"\s*:\s*{', re.M)
entries = {}
positions = []
for m in pattern.finditer(text):
    positions.append((m.group(1), m.start(), m.end()-1))

if not positions:
    print('No entries found matching ZIP pattern. Aborting.')
    sys.exit(1)

for key, start_idx, brace_idx in positions:
    i = brace_idx
    count = 0
    j = i
    L = len(text)
    while j < L:
        if text[j] == '{':
            count += 1
        elif text[j] == '}':
            count -= 1
        j += 1
        if count == 0:
            break
    obj_text = text[i:j]
    # Attempt to fix common trailing-comma issues inside the object
    # Remove any ',\s*}' occurrences
    obj_text_fixed = re.sub(r',\s*}', '}', obj_text)
    obj_text_fixed = re.sub(r',\s*\n\s*}', '\n}', obj_text_fixed)
    try:
        obj = json.loads(obj_text_fixed)
        entries[key] = obj
    except Exception as e:
        # As a fallback, try to make the object JSON-compliant by quoting keys and fixing trailing commas
        print(f'Warning: json.loads failed for {key}: {e}. Trying tolerant eval...')
        # Very small safe eval: replace true/false/null if any, though not expected
        tmp = obj_text_fixed
        tmp = tmp.replace('\n', ' ')
        try:
            obj = json.loads(tmp)
            entries[key] = obj
        except Exception as e2:
            print(f'Failed to parse object for {key}. Skipping.')

# Write combined JSON
with open(OUTPUT, 'w', encoding='utf-8') as f:
    json.dump(entries, f, indent=2, sort_keys=True)

print(f'Wrote {len(entries)} entries to {OUTPUT}')
