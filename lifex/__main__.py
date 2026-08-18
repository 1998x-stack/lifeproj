#!/usr/bin/env python3
"""Core-driven entry: python -m lifex run life --config ..."""
from fun_sim_core.cli import make_parser, run_from_parser
from .life_sim import build_registry


def main(argv=None) -> int:
    reg = build_registry()
    parser = make_parser("lifex", "Conway's Game of Life (built on fun-sim-core)")
    args = parser.parse_args(argv)
    return run_from_parser(args, reg)


if __name__ == "__main__":
    raise SystemExit(main())
