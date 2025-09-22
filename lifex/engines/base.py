from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Iterable, Set, Tuple, Optional
from ..rules import LifeRule, DEFAULT_RULE


Coord = Tuple[int, int]


class BaseEngine(ABC):
    """引擎抽象基类：定义最小接口以实现可插拔。"""

    def __init__(self, rule: LifeRule = DEFAULT_RULE):
        self.rule = rule

    # ---- 状态装载 / 导出 ----
    @abstractmethod
    def from_alive_set(self, alive: Iterable[Coord]) -> None:
        """用活细胞坐标集合设置当前状态。"""

    @abstractmethod
    def from_rle(self, rle_text: str) -> None:
        """从 RLE 文本设置当前状态。"""

    @abstractmethod
    def to_rle(self) -> str:
        """导出当前状态为 RLE 字符串（含 x,y,rule 头）。"""

    @abstractmethod
    def alive_set(self) -> Set[Coord]:
        """获取当前活细胞集合（有限支持）。"""

    # ---- 演化 ----
    @abstractmethod
    def step(self, n: int = 1) -> None:
        """推进 n 代。"""

    def run(self, steps: int) -> None:
        """推进指定步数（语义糖）。"""
        self.step(steps)

    # ---- 辅助 ----
    @abstractmethod
    def bbox(self) -> Optional[Tuple[int, int, int, int]]:
        """返回当前活细胞最小包围盒 (xmin, ymin, xmax, ymax)。若空则 None。"""