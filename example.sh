# 1) 看一个 100 步的滑翔机动画（GIF）
python -m lifex.cli --pattern Glider --gif --steps 100 --every 1

# 2) 生成 Gosper 枪，直接快进 1000 步（HashLife）
python -m lifex.cli --engine hashlife --pattern "Gosper Glider Gun" --steps 1000 --every 200 --gif

# 3) 保存最终 RLE 以便在 Golly 中打开
python -m lifex.cli --pattern LWSS --steps 64 --save-rle