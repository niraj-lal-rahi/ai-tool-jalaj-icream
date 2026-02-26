from __future__ import annotations

from dataclasses import dataclass


@dataclass
class SaleItem:
    name: str
    sold_qty: float
    returned_qty: float
    unit_price: float

    @property
    def net_qty(self) -> float:
        return self.sold_qty - self.returned_qty

    @property
    def net_value(self) -> float:
        return self.net_qty * self.unit_price
