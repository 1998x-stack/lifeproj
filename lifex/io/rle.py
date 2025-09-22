from __future__ import annotations
from typing import Set, Tuple, Iterable, Optional
from ..rules import LifeRule, DEFAULT_RULE

Coord = Tuple[int, int]


def parse_rle(text: str) -> Tuple[Set[Coord], Tuple[int, int], LifeRule]:
    """解析 RLE 文本为 (坐标集合, (宽,高), 规则)。

    RLE 主体字符:
      - 'o' 活细胞, 'b' 死细胞, '$' 换行, '!' 结束
      - 数字前缀表示重复次数（默认 1）
    头部形如: x = <w>, y = <h>, rule = B3/S23
    """
    lines = [ln.strip() for ln in text.strip().splitlines() if ln.strip()]
    # 过滤注释
    body_lines = []
    rule = DEFAULT_RULE
    width = height = None

    # 头部
    if lines and lines[0].lower().startswith("x"):
        head = lines[0]
        for part in head.split(","):
            part = part.strip()
            if part.lower().startswith("x"):
                width = int(part.split("=")[1])
            elif part.lower().startswith("y"):
                height = int(part.split("=")[1])
            elif "rule" in part.lower():
                rstr = part.split("=")[1].strip()
                rule = LifeRule.parse(rstr)
        body_lines = lines[1:]
    else:
        body_lines = lines

    body = "".join(ln for ln in body_lines if not ln.startswith("#"))

    cells: Set[Coord] = set()
    x = y = 0
    num_buf = ""
    i = 0
    while i < len(body):
        ch = body[i]
        if ch.isdigit():
            num_buf += ch
        elif ch in ("o", "b", "$", "!"):
            n = int(num_buf) if num_buf else 1
            num_buf = ""
            if ch == "o":
                for _ in range(n):
                    cells.add((x, y))
                    x += 1
            elif ch == "b":
                x += n
            elif ch == "$":
                y += n
                x = 0
            elif ch == "!":
                break
        else:
            # 其它空白忽略
            pass
        i += 1

    # 宽高可从头部或坐标推导
    if width is None or height is None:
        if cells:
            xs = [cx for cx, _ in cells]
            ys = [cy for _, cy in cells]
            width = max(xs) + 1
            height = max(ys) + 1
        else:
            width = height = 0

    return cells, (width, height), rule


def to_rle(cells: Iterable[Coord], rule: LifeRule = DEFAULT_RULE) -> str:
    """将坐标集合编码为紧凑 RLE（自动包围盒）。"""
    S = set(cells)
    if not S:
        return f"x = 0, y = 0, rule = {rule}\n!"

    xs = [x for x, _ in S]
    ys = [y for _, y in S]
    xmin, ymin, xmax, ymax = min(xs), min(ys), max(xs), max(ys)
    width = xmax - xmin + 1
    height = ymax - ymin + 1

    rows = []
    for yy in range(ymin, ymax + 1):
        row = []
        run_char = None
        run_len = 0

        def flush():
            nonlocal run_char, run_len, row
            if run_len == 0:
                return
            if run_len == 1:
                row.append(run_char)
            else:
                row.append(f"{run_len}{run_char}")
            run_len = 0

        for xx in range(xmin, xmax + 1):
            ch = "o" if (xx, yy) in S else "b"
            if run_char is None:
                run_char = ch
                run_len = 1
            elif ch == run_char:
                run_len += 1
            else:
                flush()
                run_char = ch
                run_len = 1
        flush()
        # 行末尾的 'b' 可省略
        line = "".join(row).rstrip("b")
        rows.append(line if line else "b")

    body = "$".join(rows) + "!"
    header = f"x = {width}, y = {height}, rule = {rule}"
    return header + "\n" + body


def only_rle_body(text: str) -> str:
    """提取 RLE 主体（去掉头部），供某些库直接解析。"""
    lines = [ln.strip() for ln in text.strip().splitlines() if ln.strip()]
    if lines and lines[0].lower().startswith("x"):
        body = "\n".join(lines[1:])
    else:
        body = "\n".join(lines)
    return body


def wrap_rle_body(body: str, rule: LifeRule = DEFAULT_RULE) -> str:
    """给仅有主体的 RLE 加上标准头。宽高无法知时让查看器自动计算。"""
    return f"rule = {rule}\n{body if body.strip().endswith('!') else body.strip() + '!'}"