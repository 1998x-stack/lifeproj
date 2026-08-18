# lifeproj

可插拔的 **Conway's Game of Life** 项目，构建于 `fun-sim-core` 工厂架构之上：注册为一个 `life` 模拟，支持**稀疏引擎**与可选的 **HashLife**，读写 **RLE**，YAML 行为库，导出 **GIF / MP4 / RLE**。

## 架构

- `lifex/` — Life 领域库：`engines/`（sparse / hashlife）、`rules.py`、`io/`（rle / yaml_patterns / video）
- `lifex/life_sim.py` — 核心 `Simulation` 集成（`LifeSim`，name=`life`）
- `lifex/engine_builder.py` — 引擎工厂（hashlife→sparse 回退）
- `lifex/__main__.py` — 基于 `fun-sim-core` 的标准 CLI（`list` / `run`）

## 安装

```bash
/opt/homebrew/bin/python3.12 -m venv .venv && source .venv/bin/activate
pip install -e ../fun-sim-core        # 依赖的共享核心
pip install -e .                      # 本应用
pip install numpy matplotlib imageio pyyaml python-lifelib
```

## 使用

```bash
python -m lifex list                        # 列出已注册仿真
python -m lifex run life --config configs/life.yaml --steps 100 --out runs/
```

### 传统完整 CLI（保留）

```bash
python -m lifex.cli --engine sparse --pattern glider --gif --fps 15 --out-dir out
```

## 测试

```bash
./.venv/bin/python -m pytest tests/ -q
```

## License

MIT
