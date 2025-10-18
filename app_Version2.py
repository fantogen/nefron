import streamlit as st
from streamlit_autorefresh import st_autorefresh
from google import genai
from openai import OpenAI

st.set_page_config(page_title="Nefron", page_icon="✨", layout="centered")

# -------------------- GLOBAL STYLE --------------------
style = """
<style>
@keyframes curveFadeIn {
  0% {clip-path: circle(0% at 50% 50%); opacity: 0;}
  100% {clip-path: circle(150% at 50% 50%); opacity: 1;}
}
@keyframes moveIn {
  0% {opacity: 0; transform: translateY(80px);}
  100% {opacity: 1; transform: translateY(0);}
}
body {
  background-color:#000;
  color: #FFD700;
  font-family: 'Poppins', sans-serif;
}
.main-logo {
  font-size:8rem;
  font-weight:900;
  color:#FFD700;
  -webkit-background-clip:text;
  -webkit-text-fill-color:transparent;
  background:linear-gradient(180deg,#FFD700 0%,#FFCE49 100%);
  filter:drop-shadow(0px 0px 30px rgba(255,215,0,0.8));
  animation: curveFadeIn 3.5s ease-in-out;
}
.app-name {
  font-size:2.8rem;
  letter-spacing:10px;
  margin-top:-2rem;
  color:#FFD700;
  animation: moveIn 3s ease-in-out;
}
.curved-container {
  border-radius:20px;
  border:2px solid #FFD700;
  background-color:#0A0A0A;
  box-shadow:0px 0px 25px rgba(255,215,0,0.3);
  padding:25px;
  animation: curveFadeIn 1.3s ease-in-out;
}
.chat-box, .history-box {
  border-radius:20px;
  border:2px solid #FFD700;
  background-color:#0A0A0A;
  margin-bottom:15px;
  padding:15px;
  box-shadow:0 0 10px rgba(255,215,0,0.4);
}
.stTextArea textarea {
  background-color:#000;
  color:#FFD700;
  border:1px solid #FFD700;
  border-radius:12px;
}
.stButton>button {
  background-color:#FFD700;
  color:#000;
  border-radius:10px;
  font-weight:bold;
  transition:0.3s;
}
.stButton>button:hover {
  background-color:#e6c200;
}
.copy-btn {
  display:inline-block;
  background-color:#FFD700;
  color:#000;
  padding:6px 10px;
  border-radius:6px;
  cursor:pointer;
  margin-top:10px;
}
</style>
"""
st.markdown(style, unsafe_allow_html=True)

# -------------------- INTRO STATE --------------------
if "loaded" not in st.session_state:
    st.session_state.loaded = False

if not st.session_state.loaded:
    # Auto refresh 5 times 1 second apart => ~5 seconds intro
    count = st_autorefresh(interval=1000, limit=5, key="intro")

    st.markdown("<div style='height:40vh'></div>", unsafe_allow_html=True)
    st.markdown("<h1 class='main-logo'>N</h1>", unsafe_allow_html=True)
    st.markdown("<h3 class='app-name'>NEFRON</h3>", unsafe_allow_html=True)

    if count == 5:
        st.session_state.loaded = True
        st.experimental_rerun() 
else:
    # -------------------- MAIN CONTENT --------------------
    st.title("✨ NEFRON - AI Prompt Optimizer")
    st.markdown("<div class='curved-container'>", unsafe_allow_html=True)

    if "history" not in st.session_state:
        st.session_state.history = []

    task = st.text_area("Describe your task", placeholder="e.g. Write a sci‑fi story about time travel in 200 words.")

    if st.button("Generate Optimized Prompt"):
        user_task = task.strip()
        if user_task:
            base_prompt = f"""
Act as a world-class AI prompt engineer.
Rewrite this user task into an advanced, creative, detailed prompt for an AI model.
Ensure:
1. Structured, step-based reasoning.
2. Contextual tone and desired output type.
3. Clear constraints (length, style, audience).
4. Output an original, self‑contained prompt.

User task: {user_task}
Return only the new optimized prompt.
""".strip()

            gem_client = genai.Client(api_key=st.secrets.get("GEMINI_API_KEY",""))
            optimized = ""
            try:
                resp = gem_client.models.generate_content(
                    model="gemini-1.5-flash",
                    contents=base_prompt
                )
                optimized = resp.text.strip() if resp.text else ""
            except Exception:
                oai_client = OpenAI(api_key=st.secrets.get("OPENAI_API_KEY",""))
                resp = oai_client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role":"user","content":base_prompt}],
                    max_tokens=700
                )
                optimized = resp.choices[0].message.content.strip()

            copy_text = optimized.replace('\n', ' ').replace('"', '\\"')

            st.markdown("<div class='chat-box'>", unsafe_allow_html=True)
            st.subheader("Optimized Creative Prompt")
            st.code(optimized, language="none")
            st.markdown(
                f'<button class="copy-btn" onclick="navigator.clipboard.writeText(\"{copy_text}\")">Copy Prompt</button>',
                unsafe_allow_html=True
            )

            # Suggest AI model based on intent
            task_lower = user_task.lower()
            if "code" in task_lower or "program" in task_lower:
                suggestion = ("https://platform.openai.com/", "OpenAI GPT‑4o (for coding & logic heavy tasks)")
            elif any(x in task_lower for
