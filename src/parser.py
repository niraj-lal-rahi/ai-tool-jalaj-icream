from __future__ import annotations

import ast
import operator
import re
from typing import Iterable, List

from .models import SaleItem

# Supports English + Devanagari names and plain numeric formats.
LINE_PATTERN = re.compile(
    r"^\s*(?P<name>[\w\u0900-\u097F][\w\u0900-\u097F\-\s]*)[,:\s]+"
    r"(?P<sold>[\d\u0966-\u096F\+\-\*/\.]+)\s*[,\s]+"
    r"(?P<returned>[\d\u0966-\u096F\+\-\*/\.]+)\s*[,\s]+"
    r"(?P<price>[\d\u0966-\u096F\+\-\*/\.]+)\s*$",
    re.IGNORECASE,
)

FALLBACK_PATTERN = re.compile(
    r"^\s*(?P<name>[\w\u0900-\u097F][\w\u0900-\u097F\-\s]*)\s+"
    r"(?:sold|बेचा)\s+(?P<sold>[\d\u0966-\u096F\+\-\*/\.]+)\s+"
    r"(?:returned|वापस)\s+(?P<returned>[\d\u0966-\u096F\+\-\*/\.]+)\s+"
    r"(?:price|भाव|रेट)\s+(?P<price>[\d\u0966-\u096F\+\-\*/\.]+)\s*$",
    re.IGNORECASE,
)

SAFE_EXPR_PATTERN = re.compile(r"^[0-9.\-+*/\s]+$")
ALLOWED_BIN_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
}


DEVANAGARI_DIGITS = str.maketrans("०१२३४५६७८९", "0123456789")


def _normalize_digits(value: str) -> str:
    return value.translate(DEVANAGARI_DIGITS)


def _safe_eval_numeric_expression(expression: str) -> float:
    node = ast.parse(expression, mode="eval").body

    def _eval(current: ast.AST) -> float:
        if isinstance(current, ast.Constant) and isinstance(current.value, (int, float)):
            return float(current.value)

        if isinstance(current, ast.UnaryOp) and isinstance(current.op, ast.USub):
            return -_eval(current.operand)

        if isinstance(current, ast.BinOp) and type(current.op) in ALLOWED_BIN_OPS:
            left = _eval(current.left)
            right = _eval(current.right)
            return ALLOWED_BIN_OPS[type(current.op)](left, right)

        raise ValueError("Unsupported arithmetic expression")

    return _eval(node)


def _evaluate_number(value: str) -> float:
    normalized = _normalize_digits(value)
    if SAFE_EXPR_PATTERN.match(normalized):
        try:
            return float(_safe_eval_numeric_expression(normalized))
        except Exception:
            pass
    return float(normalized)


def extract_seller_name(lines: Iterable[str]) -> str | None:
    """Pick the first likely seller heading from top OCR lines.

    A heading-like line has text but no obvious numeric tokens.
    """
    for raw_line in lines:
        line = re.sub(r"\s+", " ", raw_line).strip()
        if len(line) < 2:
            continue

        if re.search(r"[0-9\u0966-\u096F]", line):
            continue

        # Exclude labels such as date/page often found in notebooks.
        lowered = line.lower()
        if lowered in {"date", "page"}:
            continue

        return line

    return None


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
        sold = _evaluate_number(match.group("sold"))
        returned = _evaluate_number(match.group("returned"))
        price = _evaluate_number(match.group("price"))
        items.append(SaleItem(name=name, sold_qty=sold, returned_qty=returned, unit_price=price))

    return items
