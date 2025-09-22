from __future__ import annotations
from collections import defaultdict
from typing import Iterable, Set, Tuple, Optional
from .base import BaseEngine, Coord
from ..rules import LifeRule
from ..io import rle as rle_io


_OFFSETS = [
    (-1, -1), (0, -1), (1, -1),
    (-1,  0),          (1,  0),
    (-1,  1), (0,  1), (1,  1),
]


class SparseEngine(BaseEngine):
    """稀疏集合引擎：对稀疏世界非常高效，适合普遍使用。"""

    def __init__(self, rule: LifeRule):
        super().__init__(rule)
        self._alive: Set[Coord] = set()

    def from_alive_set(self, alive: Iterable[Coord]) -> None:
        self._alive = set(alive)

    def from_rle(self, rle_text: str) -> None:
        cells, _, _ = rle_io.parse_rle(rle_text)
        self._alive = cells

    def to_rle(self) -> str:
        return rle_io.to_rle(self._alive, self.rule)

    def alive_set(self) -> Set[Coord]:
        return set(self._alive)

    def step(self, n: int = 1) -> None:
        for _ in range(n):
            counts = defaultdict(int)
            for (x, y) in self._alive:
                for dx, dy in _OFFSETS:
                    counts[(x + dx, y + dy)] += 1
            next_alive: Set[Coord] = set()
            # 先考虑所有可能“被影响”的格子（包括活邻居格与活元）
            candidates = set(counts.keys()) | self._alive
            for c in candidates:
                k = counts.get(c, 0)
                if c in self._alive:
                    if k in self.rule.survives:
                        next_alive.add(c)
                else:
                    if k in self.rule.births:
                        next_alive.add(c)
            self._alive = next_alive

    def bbox(self) -> Optional[Tuple[int, int, int, int]]:
        if not self._alive:
            return None
        xs = [x for x, _ in self._alive]
        ys = [y for _, y in self._alive]
        return (min(xs), min(ys), max(xs), max(ys))