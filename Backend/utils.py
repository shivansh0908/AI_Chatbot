# utils.py
import re
from collections import OrderedDict

def normalize_whitespace(s: str) -> str:
    return re.sub(r'\s+', ' ', s).strip()

def dedupe_keep_order(strings):
    seen = set()
    out = []
    for s in strings:
        if s not in seen:
            out.append(s)
            seen.add(s)
    return out
