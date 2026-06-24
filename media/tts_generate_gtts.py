# 依赖: pip install gTTS==2.3.2 pandas
# 用法: python tts_generate_gtts.py media/scenes.csv media/audio
import os
import sys
import pandas as pd
from gtts import gTTS


def ensure_dir(p):
    if not os.path.exists(p):
        os.makedirs(p)


def main(csv_path, out_dir, lang='zh-cn'):
    df = pd.read_csv(csv_path)
    ensure_dir(out_dir)
    for idx, row in df.iterrows():
        sid = int(row['id'])
        text = str(row['narration'])
        fname = f"scene_{sid:02d}.mp3"
        out_path = os.path.join(out_dir, fname)
        if os.path.exists(out_path):
            print(f"跳过已存在: {out_path}")
            continue
        try:
            tts = gTTS(text, lang=lang)
            tts.save(out_path)
            print(f"已生成: {out_path}")
        except Exception as e:
            print(f"生成失败 {sid}: {e}")


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('用法: python tts_generate_gtts.py <scenes.csv> <out_dir>')
    else:
        main(sys.argv[1], sys.argv[2])
