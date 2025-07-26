import re
import json
from pathlib import Path

md_file = Path("data/processed/HSC26-Bangla1st-Paper-with-answers.md")
text = md_file.read_text(encoding='utf-8')

# Split on "## " headings
pattern = r'(?:^|\n)## (.+)'
splits = re.split(pattern, text)

data = []

for i in range(1, len(splits), 2):
    section = splits[i].strip()
    content = splits[i]+"\n"+splits[i+1].strip()
    data.append({
        "section": section,
        "content": content
    })

# Save JSON
json_file = md_file.with_suffix(".json")
with open(json_file, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"Saved structured JSON to {json_file}")
