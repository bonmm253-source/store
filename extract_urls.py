import re
import os

def find_urls(filepath):
    print(f"--- {filepath} ---")
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            urls = re.findall(r"\{%\s*url\s+(['\"][^'\"]+['\"]|[^%]+)\s*%\}", content)
            for url in urls:
                print(f"Found: {url.strip()}")
    except Exception as e:
        print(f"Error reading {filepath}: {e}")

project_dir = r"c:\Users\sagacious wizzy\Desktop\drop down"
find_urls(os.path.join(project_dir, "templates", "wrist.html"))
find_urls(os.path.join(project_dir, "templates", "base.html"))
find_urls(os.path.join(project_dir, "templates", "wristcollection.html"))
