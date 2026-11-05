"""KPC V6.2: strict, deterministic 2-or-3-list multiset audit."""
from __future__ import annotations
from collections import Counter
from dataclasses import dataclass, field
from itertools import combinations
from typing import Mapping
import re

PREFIX = re.compile(r"^(?:KPC|KPÇ)\s*", re.IGNORECASE)
CODE = re.compile(r"^[0-9]+$")

@dataclass
class ParsedList:
    name: str
    codes: list[str] = field(default_factory=list)
    invalid: list[str] = field(default_factory=list)
    tokens: int = 0

    @property
    def counts(self):
        return Counter(self.codes)


def normalize(token: str) -> str:
    s = PREFIX.sub('', str(token).strip())
    s = re.sub(r'\s+', '', s)
    if not CODE.fullmatch(s):
        raise ValueError('KPC/KPÇ prefiksi və rəqəmlərdən başqa simvol')
    meaningful = s.lstrip('0')
    if len(meaningful) > 5:
        raise ValueError('5-dən çox əhəmiyyətli rəqəm')
    return meaningful.zfill(5)


def parse_text(name: str, value: str) -> ParsedList:
    result = ParsedList(name)
    text = str(value).replace('\ufeff', '').replace('\u200b', '')
    # Pasted markdown tables are permitted; only a pure Markdown separator is skipped.
    lines = re.split(r'[,;\n\r\t|]+', text)
    for line in lines:
        line = line.strip()
        if not line or re.fullmatch(r'[-:\s]+', line):
            continue
        parts = re.findall(r'(?:KPC|KPÇ)\s*\d+|\d+|\S+', line, flags=re.I)
        for part in parts:
            result.tokens += 1
            try:
                result.codes.append(normalize(part))
            except ValueError:
                result.invalid.append(part)
    return result


def compare(inputs: Mapping[str, ParsedList]) -> dict:
    names = [k for k in ('A','B','C') if k in inputs]
    if len(names) < 2:
        raise ValueError('Minimum 2 siyahı tələb olunur')
    clean = all(not inputs[k].invalid and inputs[k].tokens == len(inputs[k].codes) and inputs[k].tokens > 0 for k in names)
    size_equal = len({len(inputs[k].codes) for k in names}) == 1
    check1 = clean and size_equal
    check2 = all(sorted(inputs[a].codes) == sorted(inputs[b].codes) for a,b in combinations(names,2))
    cnt = {k: inputs[k].counts for k in names}
    check3 = all(cnt[a] == cnt[b] for a,b in combinations(names,2))
    diff = []
    for code in sorted(set().union(*(set(cnt[k]) for k in names))):
        qty = {k: cnt[k][code] for k in names}
        if len(set(qty.values())) > 1:
            diff.append({'KPC':code, **qty})
    return {
        'names':names, 'match':check1 and check2 and check3,
        'checks': {'say_və_format':check1,'sıralanmış_tam_müqayisə':check2,'Counter_multiset':check3},
        'sizes':{k:len(inputs[k].codes) for k in names},
        'invalid':{k:inputs[k].invalid for k in names},
        'duplicates':{k:{c:n for c,n in sorted(cnt[k].items()) if n>1} for k in names},
        'differences':diff,
    }
