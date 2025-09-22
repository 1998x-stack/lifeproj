from dataclasses import dataclass
from typing import FrozenSet


@dataclass(frozen=True)
class LifeRule:
    """生命游戏规则（外总和规则，例：B3/S23）。

    属性:
        births:  使死细胞诞生的邻居数量集合
        survives: 使活细胞存活的邻居数量集合
    """
    births: FrozenSet[int]
    survives: FrozenSet[int]

    @staticmethod
    def parse(rule_str: str) -> "LifeRule":
        """解析规则字符串，如 'B3/S23' 或 'b3/s23'。"""
        r = rule_str.strip().lower()
        if not r or "/" not in r:
            raise ValueError(f"非法规则: {rule_str}")
        b_part, s_part = r.split("/")
        if not (b_part.startswith("b") and s_part.startswith("s")):
            raise ValueError(f"非法规则: {rule_str}")
        births = frozenset(int(ch) for ch in b_part[1:] if ch.isdigit())
        survives = frozenset(int(ch) for ch in s_part[1:] if ch.isdigit())
        return LifeRule(births, survives)

    def __str__(self) -> str:
        b = "".join(str(x) for x in sorted(self.births))
        s = "".join(str(x) for x in sorted(self.survives))
        return f"B{b}/S{s}"


# 默认规则
DEFAULT_RULE = LifeRule.parse("B3/S23")
print(DEFAULT_RULE)