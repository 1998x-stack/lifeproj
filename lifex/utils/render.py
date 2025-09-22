from __future__ import annotations
import numpy as np
from typing import Iterable, Tuple, Optional

Coord = Tuple[int, int]


def to_array(cells: Iterable[Coord],
             bbox: Optional[Tuple[int, int, int, int]] = None,
             pad: int = 2) -> np.ndarray:
    """将坐标集合栅格化为 0/1 矩阵，用于绘图/导出。

    参数:
      cells: 活细胞坐标
      bbox: (xmin, ymin, xmax, ymax)，若 None 则按数据自适应
      pad:  四周留白
    """
    S = set(cells)
    if not S:
        return np.zeros((1, 1), dtype=np.uint8)
    xs = [x for x, _ in S]
    ys = [y for _, y in S]
    xmin, ymin, xmax, ymax = min(xs), min(ys), max(xs), max(ys)
    if bbox is not None:
        xmin, ymin, xmax, ymax = bbox
    xmin -= pad
    ymin -= pad
    xmax += pad
    ymax += pad
    w = xmax - xmin + 1
    h = ymax - ymin + 1
    arr = np.zeros((h, w), dtype=np.uint8)
    for x, y in S:
        if xmin <= x <= xmax and ymin <= y <= ymax:
            arr[y - ymin, x - xmin] = 1
    return arr