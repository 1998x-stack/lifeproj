from __future__ import annotations
from typing import Iterable, Set, Tuple, Optional
from .base import BaseEngine, Coord
from ..rules import LifeRule
from ..io import rle as rle_io

_HAS_LIFELIB = False
_LL_SESS = None
try:
    import lifelib  # type: ignore
    _HAS_LIFELIB = True
except Exception:
    _HAS_LIFELIB = False

# 作为兜底，尝试 johnhw/hashlife（纯 Python 教学版）
_HAS_PY_HASHLIFE = False
try:
    import hashlife as pyhashlife  # type: ignore
    _HAS_PY_HASHLIFE = True
except Exception:
    _HAS_PY_HASHLIFE = False


class HashlifeEngine(BaseEngine):
    """HashLife 适配器：优先 lifelib，其次 johnhw/hashlife。
    注意：不同库的坐标/导出接口略有差异，这里做了最保守的适配。
    """

    def __init__(self, rule: LifeRule):
        super().__init__(rule)
        self._pattern = None  # 后端特定对象
        self._backend = None  # "lifelib" 或 "pyhashlife"
        # 规则字符串
        self._rule_str = str(rule).lower().replace("s", "/s").replace("b", "b")
        # lifelib 需要 b3s23 这种形式
        self._rule_ll = self._rule_str.replace("/", "").lower()  # b3s23

        if _HAS_LIFELIB:
            self._backend = "lifelib"
            self._sess = lifelib.load_rules(self._rule_ll)  # type: ignore
            self._lt = self._sess.lifetree()
        elif _HAS_PY_HASHLIFE:
            self._backend = "pyhashlife"
            # 纯 Python 版本以 RLE 作为主要交换格式
        else:
            raise RuntimeError(
                "未找到 HashLife 实现。请安装 python-lifelib（推荐）或 johnhw/hashlife。\n"
                "pip install python-lifelib    # 首选\n"
                "pip install hashlife          # 教学实现"
            )

    def from_alive_set(self, alive: Iterable[Coord]) -> None:
        # 将集合转换为 RLE 再喂给后端
        rle_text = rle_io.to_rle(set(alive), self.rule)
        self.from_rle(rle_text)

    def from_rle(self, rle_text: str) -> None:
        if self._backend == "lifelib":
            self._pattern = self._lt.pattern(rle_io.only_rle_body(rle_text))
        else:
            # pyhashlife 一般也接受 RLE 字符串
            self._pattern = pyhashlife.parse(rle_io.only_rle_body(rle_text))  # type: ignore

    def to_rle(self) -> str:
        if self._backend == "lifelib":
            # 尝试若干常见 API 名称
            p = self._pattern
            for attr in ("to_rle", "rle", "to_string"):
                if hasattr(p, attr):
                    try:
                        if attr == "to_string":
                            body = getattr(p, attr)("rle")  # type: ignore
                        else:
                            body = getattr(p, attr)()  # type: ignore
                        return rle_io.wrap_rle_body(body, self.rule)
                    except Exception:
                        pass
            # 兜底：用 cells 重构
            cells = self.alive_set()
            return rle_io.to_rle(cells, self.rule)
        else:
            # pyhashlife: 同样尝试常见方法
            p = self._pattern
            if hasattr(p, "to_rle"):
                body = p.to_rle()
            elif hasattr(p, "rle"):
                body = p.rle()
            else:
                # 兜底：抽坐标
                cells = self.alive_set()
                return rle_io.to_rle(cells, self.rule)
            return rle_io.wrap_rle_body(body, self.rule)

    def alive_set(self) -> Set[Coord]:
        # 先从 RLE 导出，再解析为坐标集合（通用且稳定）
        try:
            rle_text = self.to_rle()
            cells, _, _ = rle_io.parse_rle(rle_text)
            return cells
        except Exception:
            return set()

    def step(self, n: int = 1) -> None:
        if self._backend == "lifelib":
            # lifelib 支持索引切片：p[n] 返回 n 步后的模式
            self._pattern = self._pattern[n]
        else:
            # pyhashlife 教学实现通常有 advance(n)
            if hasattr(self._pattern, "advance"):
                self._pattern = self._pattern.advance(n)  # type: ignore
            else:
                # 退化：转稀疏引擎演化再回写
                from .sparse import SparseEngine  # 避免循环导入
                sp = SparseEngine(self.rule)
                sp.from_alive_set(self.alive_set())
                sp.step(n)
                self.from_alive_set(sp.alive_set())

    def bbox(self) -> Optional[Tuple[int, int, int, int]]:
        cells = self.alive_set()
        if not cells:
            return None
        xs = [x for x, _ in cells]
        ys = [y for _, y in cells]
        return (min(xs), min(ys), max(xs), max(ys))