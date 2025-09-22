from __future__ import annotations
from typing import Iterable, Optional, Tuple
import os
import numpy as np
import imageio.v2 as imageio
import matplotlib.pyplot as plt
from matplotlib import animation


def save_gif(frames: Iterable[np.ndarray], out_path: str, fps: int = 10) -> str:
    """将帧序列保存为 GIF。帧为 0/1 numpy 数组。"""
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    imgs = []
    for arr in frames:
        # 变成灰度 0..255
        img = (arr * 255).astype(np.uint8)
        imgs.append(img)
    imageio.mimsave(out_path, imgs, duration=1.0 / fps)
    return out_path


def save_mp4(frames: Iterable[np.ndarray], out_path: str, fps: int = 20) -> str:
    """将帧序列保存为 MP4（需要本机 ffmpeg）。"""
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    # 用 matplotlib.animation 写视频
    frames = list(frames)
    if not frames:
        raise ValueError("无帧可写入。")
    h, w = frames[0].shape

    fig = plt.figure(figsize=(w / 20, h / 20), dpi=100)
    ax = plt.axes([0, 0, 1, 1])
    ax.set_axis_off()
    im = ax.imshow(frames[0], interpolation="nearest", vmin=0, vmax=1)

    def init():
        im.set_data(frames[0])
        return (im,)

    def animate(i):
        im.set_data(frames[i])
        return (im,)

    ani = animation.FuncAnimation(
        fig, animate, init_func=init, frames=len(frames), interval=1000 / fps, blit=True
    )
    Writer = animation.writers.get("ffmpeg", None)
    if Writer is None:
        raise RuntimeError("未找到 ffmpeg 写入器。请在系统中安装 ffmpeg。")
    writer = Writer(fps=fps, metadata=dict(artist="lifex"))
    ani.save(out_path, writer=writer)
    plt.close(fig)
    return out_path