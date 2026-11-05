"""Deterministic KPC V6.1 comparison engine. No OCR or UI dependencies."""
from __future__ import annotations
from collections import Counter
from dataclasses import dataclass, field
import re
from typing import Mapping

PREFIX = re.compile(r"^(?:KPC|KPÇ)\s*", re.IGNORECASE)
VALID_DIGITS = re.compile(r"^[0-9]+$")


@dataclass
class ParsedList:
    name: str
    codes: list[str] = field(default_factory=list)
    invalid: list[str] = field(default_factory=list)
    tokens: int = 0

    @property
    def counts(self):
        return Counter(self.codes)


def normalize(raw: str) -> str:
    """Remove KPC/KPÇ & spaces; pad to five; reject >5 significant digits.

    Examples: KPC018569 -> 18569; 23 -> 00023; 00000123 -> 00123.
    """
    value = PREFIX.sub('', str(raw).strip())
    value = re.sub(r'\s+', '', value)
    if not value or not VALID_DIGITS.fullmatch(value):
        raise ValueError('yalnız KPC prefiksi və rəqəmlər qəbul edilir')
    significant = value.lstrip('0')
    if len(significant) > 5:
        raise ValueError('5-dən çox əhəmiyyətli rəqəm')
    return significant.zfill(5)


def parse_text(name: str, text: str) -> ParsedList:
    """Strict one-token-per-separator parser. Never guesses or repairs digits.

    Commas, semicolons, vertical bars, newlines and tabs separate tokens.
    Multiple space separated code items are also supported without breaking
    'KPC 01234' into two tokens.
    """
    parsed = ParsedList(name=name)
    # Handle pasted markdown tables, headings; avoid silently accepting dates.
    text = str(text).replace('\ufeff', '')
    chunks = re.split(r'[,;\n\r\t|]+', text)
    for chunk in chunks:
        chunk = chunk.strip()
        if not chunk or re.fullmatch(r'[:\-\s]+', chunk):
            continue
        # whitespace between separate numbers/prefixed codes
        parts = re.findall(r'(?:KPC|KPÇ)\s*\d+|\d+|[^\s]+', chunk, flags=re.I)
        # If the line is a prose sentence, mark non-numeric words invalid;
        # never cherry-pick only numeric fragments as a successful input.
        for part in parts:
            parsed.tokens += 1
            try:
                parsed.codes.append(normalize(part))
            except ValueError:
                parsed.invalid.append(part)
    return parsed


def compare(lists: Mapping[str, ParsedList]) -> dict:
    """Three independent checks: count/format, full sorted lists, Counter.

    All three inputs must exist and be valid. No partial input can be 'match'.
    """
    if set(lists) != {'A', 'B', 'C'}:
        raise ValueError('A, B və C siyahılarının hamısı tələb olunur')
    count_format = (
        all(not p.invalid and p.tokens > 0 and p.tokens == len(p.codes) for p in lists.values())
        and len({len(p.codes) for p in lists.values()}) == 1
    )
    sorted_equal = sorted(lists['A'].codes) == sorted(lists['B'].codes) == sorted(lists['C'].codes)
    counters = {k: v.counts for k, v in lists.items()}
    counter_equal = counters['A'] == counters['B'] == counters['C']
    valid = all(not p.invalid and p.tokens > 0 for p in lists.values())
    match = count_format and sorted_equal and counter_equal and valid

    # For each code, report every list's actual occurrence count whenever they differ.
    mismatch_rows = []
    for code in sorted(set().union(*(set(c) for c in counters.values()))):
        quantities = [counters[k][code] for k in ('A','B','C')]
        if len(set(quantities)) > 1:
            mismatch_rows.append({'KPC': code, 'A': quantities[0], 'B': quantities[1], 'C': quantities[2]})
    duplicates = {k: {code: qty for code, qty in sorted(c.items()) if qty > 1} for k, c in counters.items()}
    return {
        'match': match, 'ready': valid,
        'checks': {'count_and_format': count_format, 'sorted_full_comparison': sorted_equal,
                   'counter_multiset': counter_equal},
        'sizes': {k: len(v.codes) for k,v in lists.items()},
        'invalid': {k: list(v.invalid) for k,v in lists.items()},
        'duplicates': duplicates,
        'differences': mismatch_rows,
    }
