from __future__ import annotations

import re
from typing import Iterable, List

from .models import SaleItem

# Expected line examples (flexible spacing/separators):
# "Milk sold 10 returned 1 price 40"
# "Bread, 4, 0, 25"
LINE_PATTERN = re.compile(
    r"^\s*(?P<name>[A-Za-z][A-Za-z0-9\-\s]*)[,:\s]+"
    r"(?P<sold>\d+(?:\.\d+)?)\s*[,\s]+"
    r"(?P<returned>\d+(?:\.\d+)?)\s*[,\s]+"
    r"(?P<price>\d+(?:\.\d+)?)\s*$",
    re.IGNORECASE,
)

FALLBACK_PATTERN = re.compile(
    r"^\s*(?P<name>[A-Za-z][A-Za-z0-9\-\s]*)\s+sold\s+(?P<sold>\d+(?:\.\d+)?)\s+"
    r"returned\s+(?P<returned>\d+(?:\.\d+)?)\s+price\s+(?P<price>\d+(?:\.\d+)?)\s*$",
    re.IGNORECASE,
)


def parse_lines(lines: Iterable[str]) -> List[SaleItem]:
    items: List[SaleItem] = []

    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            continue

        match = LINE_PATTERN.match(line) or FALLBACK_PATTERN.match(line)
        if not match:
            continue

        name = re.sub(r"\s+", " ", match.group("name")).strip().title()
        sold = float(match.group("sold"))
        returned = float(match.group("returned"))
        price = float(match.group("price"))
        items.append(SaleItem(name=name, sold_qty=sold, returned_qty=returned, unit_price=price))

    return items
