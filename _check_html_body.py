from pathlib import Path
import re
p = Path(r"D:\scan chain dianosis agent\output\SCD-FR-008_scan_diagnosis_report.html")
text = p.read_text(encoding="utf-8")
low = text.lower()
bi = low.find("<body")
be = low.rfind("</body>")
head_end = low.find("</head>")
body = text[bi:be] if bi >= 0 and be >= 0 else ""
style_in_body = len(re.findall(r"<style\b", body, re.I))
# CSS class definitions as text nodes (not in attributes)
orphan = re.findall(r"^\s*\.[a-zA-Z][\w-]*\s*\{", body, re.M)
print("body_chars:", len(body))
print("style_tags_in_body:", style_in_body)
print('class="row-count" in body:', 'class="row-count"' in body)
print('class="table-scroll" in body:', 'class="table-scroll"' in body)
print("orphan_selector_lines_in_body:", len(orphan))
if orphan:
    print("first orphan lines:", orphan[:5])
else:
    print("No orphaned CSS selector lines in body")
