# app.py
import os
import time
import streamlit as st
from google import genai
from openai import OpenAI

GEM_MODEL = "gemini-1.5-flash"  # pick a free-tier friendly model from pricing docs
OPENAI_MODEL = "gpt-4o-mini"    # keep cheap/concise; enforce token caps

st.title("Prompt Optimizer MVP")

task = st.text_area("Describe your task")
style = st.selectbox("Style", ["creative", "step-by-step", "structured"])
max_tokens = st.slider("Max output tokens", 128, 2048, 512)
use_openai_if_needed = st.checkbox("Escalate to OpenAI if low quality", value=False)

def draft_prompt(task, style):
    return f"""
You are a prompt engineer.
Rewrite the following task into a precise, creative prompt with:
- Clear role and goal
- Step-by-step plan
- Constraints (tone, format, length)
- Few-shot examples if useful
- Verification checklist

Task: {task}
Style: {style}
Output: A single optimized prompt string only.
""".strip()

def llm_call_gemini(txt):
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    resp = client.models.generate_content(model=GEM_MODEL, contents=txt)
    return resp.text

def llm_call_openai(txt):
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    resp = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[{"role": "user", "content": txt}],
        max_tokens=max_tokens,
        temperature=0.7,
    )
    return resp.choices[0].message.content

def judge_quality(prompt_str, task):
    judge_instruction = f"""
Judge if this optimized prompt will likely solve the task:
- Criteria: relevance, clarity, constraints, testability (0-10 each)
- Return: JSON with scores and a brief fix suggestion
Task: {task}
Prompt: {prompt_str}
Only return JSON.
"""
    # Cheap judge: Gemini by default
    return llm_call_gemini(judge_instruction)

if st.button("Generate Prompt"):
    base = draft_prompt(task, style)
    # Respect Gemini rate limits: 5 RPM → simple sleep in busy loops; here single call
    draft = llm_call_gemini(base)
    verdict = judge_quality(draft, task)
    st.subheader("Draft")
    st.code(draft)

    st.subheader("Judge")
    st.code(verdict)

    # Optional escalation
    if use_openai_if_needed and '"relevance":' in verdict and "10" not in verdict:
        revised = f"Improve this prompt for the task while preserving structure:

{draft}"
        better = llm_call_openai(revised)
        st.subheader("Revised (OpenAI)")
        st.code(better)