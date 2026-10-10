import streamlit as st
import asyncio, math
import edge_tts
from moviepy.editor import ColorClip, TextClip, CompositeVideoClip, AudioFileClip, concatenate_videoclips

st.set_page_config(page_title="Character Voice Video Creator", layout="wide")
st.title("🎙️ Character Voice Video Creator")

# --- Character Voices ---
voices = {
    "Telugu Male - Mohan": "te-IN-MohanNeural",
    "Telugu Female - Shruti": "te-IN-ShrutiNeural",
    "English Male - Guy (Hero)": "en-US-GuyNeural",
    "English Female - Jenny (Heroine)": "en-US-JennyNeural",
    "English Male Deep - Christopher": "en-US-ChristopherNeural",
    "Telugu English Mix - Neerja": "en-IN-NeerjaNeural"
}

char = st.selectbox("Select Character Voice / Character Voice Enchuko", list(voices.keys()))
voice_id = voices[char]

topic = st.text_input("Topic", "Ragi Kasu History")
duration = st.slider("Duration", 10, 60, 20)
num_scenes = math.ceil(duration / 5)

defaults = [f"{topic} part {i+1}" for i in range(num_scenes)]
scenes = []
for i in range(num_scenes):
    scenes.append(st.text_area(f"Scene {i+1} Dialogue", defaults[i], key=i))

async def make_audio(text, voice, file):
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(file)

if st.button("🎥 CREATE WITH CHARACTER VOICE"):
    clips = []
    bar = st.progress(0)

    for i, text in enumerate(scenes):
        st.write(f"Generating {char} - Scene {i+1}")

        # Character Voice Generation (FREE)
        asyncio.run(make_audio(text, voice_id, f"scene_{i}.mp3"))
        audio = AudioFileClip(f"scene_{i}.mp3")

        # Background
        bg = ColorClip(size=(1080, 1920), color=(20, 20, 80)).set_duration(audio.duration)
        txt = TextClip(text, fontsize=55, color='white', font='DejaVu-Sans-Bold', method='caption', size=(900, None)).set_duration(audio.duration).set_position('center')

        clip = CompositeVideoClip([bg, txt]).set_audio(audio)
        clips.append(clip)
        bar.progress((i+1)/num_scenes)

    final = concatenate_videoclips(clips)
    final.write_videofile("character_video.mp4", fps=24, codec='libx264')

    st.success(f"Video with {char} voice ready! ✅")
    st.video("character_video.mp4")
    with open("character_video.mp4", "rb") as f:
        st.download_button("Download Character Video", f, "character_video.mp4")
