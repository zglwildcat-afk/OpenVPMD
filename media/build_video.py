# 依赖: pip install moviepy==1.0.3 pandas
# 用法: python build_video.py media/scenes.json media/audio media/images bg_music.mp3 output.mp4
import os, sys, json
from moviepy.editor import (
    ImageClip, AudioFileClip, concatenate_videoclips, CompositeVideoClip, TextClip, CompositeAudioClip
)
from moviepy.video.fx.resize import resize
import moviepy.video.fx.all as vfx

def load_scenes(json_path):
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def ken_burns(image_path, duration, w=1920, h=1080, zoom=1.06):
    clip = ImageClip(image_path).set_duration(duration).resize((w, h))
    # 简单放大效果
    def size_at(t):
        factor = 1 + (zoom - 1) * (t / duration)
        return (int(w * factor), int(h * factor))
    # 使用 resize(lambda t: ...)
    clip = clip.resize(lambda t: 1 + (zoom - 1) * (t / duration))
    return clip

def make_text_clip(text, duration, w=1920, h=1080):
    txt = TextClip(text, fontsize=48, font='DejaVu-Sans-Bold', color='white', stroke_color='black', stroke_width=1, method='label')
    txt = txt.set_position(('center', h*0.78)).set_duration(duration).fadein(0.5).fadeout(0.5)
    return txt

def main(scenes_json, audio_dir, image_dir, bg_music_path, out_path):
    scenes = load_scenes(scenes_json)
    clips = []
    for s in scenes:
        sid = s['id']
        duration = s.get('duration_sec', 20)
        img_path = os.path.join(image_dir, f"scene_{sid:02d}.jpg")
        audio_path = os.path.join(audio_dir, f"scene_{sid:02d}.mp3")
        if not os.path.exists(img_path):
            print(f"缺失图片，使用纯色背景: {img_path}")
            from moviepy.editor import ColorClip
            base = ColorClip((1920,1080), color=(25,35,60)).set_duration(duration)
        else:
            base = ken_burns(img_path, duration)
        # 文案文字
        subtitle = s.get('subtitle','')
        if subtitle:
            txt = make_text_clip(subtitle, duration)
            comp = CompositeVideoClip([base, txt])
        else:
            comp = base
        # 添加旁白音轨（若存在）
        if os.path.exists(audio_path):
            a = AudioFileClip(audio_path)
            comp = comp.set_audio(a)
        clips.append(comp.crossfadeout(0.8))
    final = concatenate_videoclips(clips, method='compose')
    # 背景音乐混合
    if bg_music_path and os.path.exists(bg_music_path):
        music = AudioFileClip(bg_music_path).volumex(0.15)
        from moviepy.audio.fx.all import audio_loop
        music = audio_loop(music, duration=final.duration)
        final_audio = CompositeAudioClip([final.audio.volumex(1.0) if final.audio else None, music]).set_duration(final.duration)
        # CompositeAudioClip不能包含 None：构造时过滤
        tracks = []
        if final.audio:
            tracks.append(final.audio)
        tracks.append(music)
        final_audio = CompositeAudioClip(tracks).set_duration(final.duration)
        final = final.set_audio(final_audio)
    # 输出
    final.write_videofile(out_path, codec='libx264', audio_codec='aac', fps=30, threads=4, preset='medium')

if __name__ == '__main__':
    if len(sys.argv) < 6:
        print("用法: python build_video.py <scenes.json> <audio_dir> <image_dir> <bg_music.mp3> <out.mp4>")
    else:
        main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
