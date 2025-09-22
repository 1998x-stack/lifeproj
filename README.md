# lifex

一个可插拔的 Conway's Game of Life 项目：支持 **稀疏引擎**、可选 **HashLife**，读写 **RLE**，基于 **YAML** 的模式/行为库，命令行导出 **GIF/MP4**。

## 安装

```bash
python -m venv .venv && source .venv/bin/activate  # Windows 用 .venv\Scripts\activate
pip install numpy matplotlib imageio pyyaml
# 若想用 HashLife（强推）：
pip install python-lifelib   # 需本机有编译环境，文档详述依赖
# 或教学实现（可选且慢）：
pip install hashlife
```