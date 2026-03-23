import os
import re

search_patterns = [
    r"\{%\s*url\s+['\"]order['\"]\s*%\}",
    r"reverse\(['\"]order['\"]\)",
    r"redirect\(['\"]order['\"]\)"
]

project_dir = r"c:\Users\sagacious wizzy\Desktop\drop down"
templates_dir = os.path.join(project_dir, "templates")

print(f"Searching in {templates_dir} and {project_dir}...")

for root, dirs, files in os.walk(project_dir):
    if ".venv" in root or ".git" in root or ".gemini" in root:
        continue
    for file in files:
        if file.endswith((".html", ".py", ".js")):
            filepath = os.path.join(root, file)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    for pattern in search_patterns:
                        if re.search(pattern, content):
                            print(f"FOUND MATCH in {filepath}: {pattern}")
                            # Print the line
                            f.seek(0)
                            lines = f.readlines()
                            for i, line in enumerate(lines):
                                if re.search(pattern, line):
                                    print(f"  Line {i+1}: {line.strip()}")
            except Exception as e:
                pass
