from __future__ import annotations
import os
from dataclasses import dataclass, field
from pathlib import Path

from fun_sim_core.config import as_dataclass
from fun_sim_core.simulation import Simulation
from fun_sim_core.registry import Registry

from .rules import LifeRule, DEFAULT_RULE
from .engine_builder import create_engine
from .io import yaml_patterns, rle as rle_io, video as video_io
from .utils.render import to_array

_default_yaml = os.path.join(os.path.dirname(__file__), "patterns", "behaviors.yaml")


@dataclass
class LifeConfig:
    engine: str = "sparse"
    rule: str = str(DEFAULT_RULE)
    pattern: str | None = None
    rle_file: str | None = None
    rle_text: str | None = None
    yaml: str = _default_yaml
    steps: int = 100
    every: int = 1
    pad: int = 2
    out_dir: str = "out"
    save_rle: bool = False
    gif: bool = False
    mp4: bool = False
    fps: int = 15
    bbox: tuple | None = None


class LifeSim:
    """Conway's Game of Life as a core Simulation (engine + pattern + export)."""
    name = "life"
    default_config = LifeConfig()
    interactive = False

    def configure(self, overrides: dict | None = None) -> None:
        self.config = as_dataclass(overrides or {}, LifeConfig)

    def _load_pattern_into(self, engine) -> str:
        """Seed the engine from pattern/rle config; returns a display base name."""
        cfg = self.config
        if cfg.pattern:
            data = yaml_patterns.load_patterns(cfg.yaml)
            rle_text = yaml_patterns.get_rle_by_name(data, cfg.pattern)
            if not rle_text:
                raise ValueError(f"pattern '{cfg.pattern}' not found in {cfg.yaml}")
            engine.from_rle(rle_text)
            return cfg.pattern
        if cfg.rle_file:
            engine.from_rle(Path(cfg.rle_file).read_text(encoding="utf-8"))
            return Path(cfg.rle_file).stem
        if cfg.rle_text:
            engine.from_rle(cfg.rle_text)
            return "pattern"
        raise ValueError("LifeSim requires one of: pattern, rle_file, rle_text")

    def setup(self) -> None:
        rule = LifeRule.parse(self.config.rule)
        self.engine = create_engine(self.config.engine, rule)
        self.base = self._load_pattern_into(self.engine)

    def step(self, *a, **k) -> None:
        self.engine.step(1)

    def run(self, steps: int = 1):
        self.engine.step(max(1, int(steps)))
        return self.engine.alive_set()

    def export(self, out_dir) -> None:
        cfg = self.config
        out = Path(out_dir)
        out.mkdir(parents=True, exist_ok=True)
        base = self.base or "pattern"

        if cfg.save_rle:
            (out / f"{base}_final.rle").write_text(self.engine.to_rle(), encoding="utf-8")
        if cfg.gif or cfg.mp4:
            frames = list(self._frames())
            if cfg.gif:
                video_io.save_gif(frames, str(out / f"{base}.gif"), fps=cfg.fps)
            if cfg.mp4:
                video_io.save_mp4(frames, str(out / f"{base}.mp4"), fps=cfg.fps)

    def _frames(self):
        cfg = self.config
        bbox = tuple(cfg.bbox) if cfg.bbox else None
        yield to_array(self.engine.alive_set(), bbox=bbox, pad=cfg.pad)
        remain = cfg.steps
        engine = self.engine
        while remain > 0:
            s = min(cfg.every, remain)
            engine.step(s)
            remain -= s
            yield to_array(engine.alive_set(), bbox=bbox, pad=cfg.pad)


def build_registry() -> Registry:
    reg = Registry()
    reg.register("life")(LifeSim)
    return reg
