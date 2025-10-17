# app.py
import streamlit as st

# SDKs
from google import genai
from openai import OpenAI

st.title("Secure Prompt Optimizer")

# 1) Read secrets securely
gemini_key = st.secrets.get("GEMINI_API_KEY")
openai_key = st.secrets.get("OPENAI_API_KEY")

# 2) Initialize clients only if keys exist
gem_client = None
if gemini_key:
    gem_client = genai.Client(api_key=gemini_key)  # google-genai SDK
else:
    st.info("Add GEMINI_API_KEY to secrets to enable Gemini calls.")

oai_client = None
if openai_key:
    oai_client = OpenAI(api_key=openai_key)        # official OpenAI SDK
else:
    st.info("Add OPENAI_API_KEY to secrets to enable OpenAI calls.")

# 3) Simple UI
task = st.text_area("Describe your task")
model_pref = st.selectbox("Primary model", ["Gemini first", "OpenAI first"])
max_tokens = st.slider("Max output tokens", 64, 2048, 512)

# 4) Safe helpers
def call_gemini(prompt: str) -> str:
    if not gem_client:
        return "Gemini unavailable: missing GEMINI_API_KEY."
    try:
        resp = gem_client.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt
        )
        return resp.text or ""
    except Exception as e:
        return f"Gemini error: {e}"

def call_openai(prompt: str) -> str:
    if not oai_client:
        return "OpenAI unavailable: missing OPENAI_API_KEY."
    try:
        resp = oai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=0.7,
        )
        return resp.choices[0].message.content
    except Exception as e:
        return f"OpenAI error: {e}"

# 5) Generate optimized prompt
if st.button("Generate Prompt"):
    base = f"""
You are a prompt engineer.
Rewrite the task into a precise prompt with:
- Role and goal
- Step-by-step plan
- Constraints (tone, format, length)
- Optional few-shot hints
- A verification checklist

Task: {task}
Output: Only the final optimized prompt text.
""".strip()

    if model_pref == "Gemini first":
        out = call_gemini(base)
        if "unavailable" in out or "error" in out:
            out = call_openai(base)
    else:
        out = call_openai(base)
        if "unavailable" in out or "error" in out:
            out = call_gemini(base)

    st.subheader("Optimized Prompt")
    st.code(out)