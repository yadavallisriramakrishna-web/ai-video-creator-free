import streamlit as st
import math, json
from typing import List, Optional
from openai import OpenAI

class SceneDirective:
    def __init__(self, scene_index, narration, visual_prompt, camera_motion, motion_brush_target, sound_effect):
        self.scene_index = scene_index
        self.narration = narration
        self.visual_prompt = visual_prompt
        self.camera_motion = camera_motion
        self.motion_brush_target = motion_brush_target
        self.sound_effect = sound_effect

class DirectorAgent:
    def __init__(self, api_key):
        self.client = OpenAI(api_key=api_key)

    def plan(self, topic: str, duration: int, aspect_ratio: str, character_desc: Optional[str] = None) -> List[SceneDirective]:
        total_scenes = max(2, math.ceil(duration / 5.0))
        consistency = f"Character: {character_desc}. SAME face, SAME clothes." if character_desc else "Ensure visual continuity."
        all_scenes = []
        batch_size = 20
        batches = math.ceil(total_scenes / batch_size)

        for b in range(batches):
            count_in_batch = min(batch_size, total_scenes - len(all_scenes))
            start_idx = len(all_scenes) + 1
            prompt = f"""Act as AI Film Director. Topic: "{topic}" (Part {b+1} of {batches})
            Duration: {duration}s. Plan EXACTLY {count_in_batch} scenes from {start_idx}.
            Format: {aspect_ratio} {consistency}
            Return ONLY JSON: {{"scenes": [{{"scene_index": {start_idx}, "narration": "Telugu 4-5 sec line", "visual_prompt": "Cinematic 8k", "camera_motion": "Zoom In", "motion_brush_target": "coin", "sound_effect": "wind"}}]}}"""
            try:
                res = self.client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}],
                    response_format={"type": "json_object"}
                )
                raw = json.loads(res.choices[0].message.content).get("scenes", [])
                for s in raw:
                    all_scenes.append(SceneDirective(s.get("scene_index", len(all_scenes)+1), s.get("narration", ""), s.get("visual_prompt", ""), s.get("camera_motion", "Static"), s.get("motion_brush_target", "None"), s.get("sound_effect", "ambient")))
            except Exception as e:
                st.warning(f"Batch {b+1} error: {e}")
                for i in range(count_in_batch):
                    all_scenes.append(SceneDirective(len(all_scenes)+1, f"Exploring {topic} scene {len(all_scenes)+1}", f"Cinematic {topic}", "Pan Right", "particles", "wind"))
        return all_scenes

# --- UI ---
st.set_page_config(page_title="AI Video Creator", layout="wide")
st.title("🎬 AI Video Creator - OpenAI Only")

api_key = st.secrets.get("OPENAI_API_KEY") or st.text_input("OpenAI API Key", type="password")
topic = st.text_input("Topic", "Ragi kasu history telugu lo")
duration = st.slider("Duration (sec)", 10, 600, 30)
aspect_ratio = st.selectbox("Ratio", ["9:16 Vertical", "16:9 Horizontal", "1:1 Square"])
character = st.text_input("Character", "Telugu historian")

if st.button("Generate Plan 🚀"):
    if not api_key:
        st.error("OpenAI API Key pettu!")
    else:
        director = DirectorAgent(api_key)
        with st.spinner(f"{math.ceil(duration/5)} scenes planning..."):
            scenes = director.plan(topic, duration, aspect_ratio, character)
        st.success(f"{len(scenes)} Scenes Ready!")
        for s in scenes:
            with st.expander(f"Scene {s.scene_index}: {s.narration[:50]}"):
                st.json(s.__dict__)
        st.download_button("Download JSON", json.dumps([vars(x) for x in scenes], indent=2), "plan.json")
