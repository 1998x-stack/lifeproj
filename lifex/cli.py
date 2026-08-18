from __future__ import annotations
import argparse
import os
from typing import Optional, Tuple, Iterable
from .rules import LifeRule, DEFAULT_RULE
from .engine_builder import create_engine
from .io import yaml_patterns, rle as rle_io, video as video_io
from .utils.render import to_array


def _gen_frames(engine, steps: int, every: int, pad: int,
                bbox: Optional[Tuple[int, int, int, int]]) -> Iterable:
    """生成帧（每 every 步采一帧）。"""
    # 首帧
    yield to_array(engine.alive_set(), bbox=bbox, pad=pad)
    remain = steps
    while remain > 0:
        s = min(every, remain)
        engine.step(s)
        remain -= s
        yield to_array(engine.alive_set(), bbox=bbox, pad=pad)


def main(argv=None) -> int:
    p = argparse.ArgumentParser(
        prog="lifex",
        description="Conway's Game of Life：可插拔引擎 + RLE + YAML 行为库 + GIF/MP4"
    )
    p.add_argument("--engine", default="sparse", help="引擎名称：sparse | hashlife（需依赖）")
    p.add_argument("--rule", default=str(DEFAULT_RULE), help="规则字符串，如 B3/S23")
    p.add_argument("--yaml", default=os.path.join(os.path.dirname(__file__), "patterns", "behaviors.yaml"),
                   help="行为/模式 YAML 文件路径")
    grp_in = p.add_mutually_exclusive_group(required=True)
    grp_in.add_argument("--pattern", help="从 YAML 中按名称加载（如 Glider, Block 等）")
    grp_in.add_argument("--rle-file", help="从 RLE 文件加载")
    grp_in.add_argument("--rle-text", help="直接给 RLE 文本（带或不带头部）")

    p.add_argument("--steps", type=int, default=100, help="总步数")
    p.add_argument("--every", type=int, default=1, help="采样间隔：每隔多少步输出一帧")
    p.add_argument("--pad", type=int, default=2, help="导出时四周留白")

    # 输出
    p.add_argument("--out-dir", default="out", help="输出目录")
    p.add_argument("--save-rle", action="store_true", help="保存最终状态为 RLE")
    p.add_argument("--gif", action="store_true", help="保存为 GIF（frames=steps/every+1）")
    p.add_argument("--mp4", action="store_true", help="保存为 MP4（需要 ffmpeg）")
    p.add_argument("--fps", type=int, default=15, help="GIF/MP4 帧率")
    p.add_argument("--bbox", type=int, nargs=4, metavar=("xmin","ymin","xmax","ymax"),
                   help="固定渲染包围盒（可避免飞出画面）；默认根据内容自适应")

    args = p.parse_args(argv)

    rule = LifeRule.parse(args.rule)
    engine = create_engine(args.engine, rule)

    # 装载初态
    if args.pattern:
        data = yaml_patterns.load_patterns(args.yaml)
        rle_text = yaml_patterns.get_rle_by_name(data, args.pattern)
        if not rle_text:
            raise SystemExit(f"未在 {args.yaml} 找到模式: {args.pattern}")
        engine.from_rle(rle_text)
    elif args.rle_file:
        with open(args.rle_file, "r", encoding="utf-8") as f:
            engine.from_rle(f.read())
    else:
        engine.from_rle(args.rle_text)

    # 生成帧并导出
    os.makedirs(args.out_dir, exist_ok=True)
    base = args.pattern or (os.path.splitext(os.path.basename(args.rle_file))[0] if args.rle_file else "pattern")

    # 帧生成器
    frames = _gen_frames(engine, steps=args.steps, every=args.every, pad=args.pad, bbox=tuple(args.bbox) if args.bbox else None)

    frames_list = list(frames)  # 为了可复用到 gif/mp4
    # 保存 RLE（最终帧）
    if args.save_rle:
        rle_path = os.path.join(args.out_dir, f"{base}_final.rle")
        with open(rle_path, "w", encoding="utf-8") as f:
            f.write(engine.to_rle())
        print(f"[OK] RLE 已保存: {rle_path}")

    # GIF
    if args.gif:
        gif_path = os.path.join(args.out_dir, f"{base}.gif")
        video_io.save_gif(frames_list, gif_path, fps=args.fps)
        print(f"[OK] GIF 已保存: {gif_path}")

    # MP4
    if args.mp4:
        mp4_path = os.path.join(args.out_dir, f"{base}.mp4")
        video_io.save_mp4(frames_list, mp4_path, fps=args.fps)
        print(f"[OK] MP4 已保存: {mp4_path}")

    if not args.gif and not args.mp4 and not args.save_rle:
        # 若未指定任何输出，就打印最终 RLE 到控制台
        print(engine.to_rle())

    return 0


if __name__ == "__main__":
    raise SystemExit(main())