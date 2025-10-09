import streamlit as st
from openai import OpenAI
import os

# --- Secure API Key Handling ---
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    st.error("Please set your OPENAI_API_KEY environment variable.")
    st.stop()

client = OpenAI(api_key=openai_api_key)

# --- Streamlit Page Setup ---
st.set_page_config(
    page_title="Nefron - AI Prompt Orchestrator",
    page_icon="🧠",
    layout="wide"
)
st.title("🧠 NEFRON – Multi-AI Prompt Orchestrator")
st.markdown("""
Nefron (Next Evolutionary Framework for Refining and Orchestrating Narratives) is an **AI prompt optimizer and intelligent router**.

- **Optimizes** prompts for best results.
- **Splits** complex tasks into subtasks.
- **Assigns** subtasks to specialist AI models.
- **Merges** all responses into a single output.
""")

# --- User Input ---
prompt = st.text_area("Enter your task for Nefron:")

# --- Model Routing Logic ---
def route_task(subtask):
    subtask = subtask.lower()
    if "image" in subtask or "picture" in subtask:
        return "DALL·E"
    elif "music" in subtask or "sound" in subtask:
        return "MusicGen"
    elif "code" in subtask or "program" in subtask:
        return "GPT-5"
    elif "analyze" in subtask or "data" in subtask:
        return "Gemini"
    else:
        return "Claude"

# --- Error Handling Utility ---
def safe_openai_chat(prompt, model="gpt-4o-mini"):
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Error querying OpenAI: {e}")
        return ""

# --- Main Execution ---
if st.button("🚀 Run Nefron"):
    if not prompt.strip():
        st.warning("⚠️ Please enter a prompt first.")
    else:
        # Step 1: Optimize the prompt
        st.info("🔍 Step 1: Optimizing your prompt...")
        optimizer_prompt = f"Improve this prompt to make it detailed, clear, and structured:\n\n{prompt}"
        optimized_prompt = safe_openai_chat(optimizer_prompt)
        if not optimized_prompt:
            st.stop()

        st.subheader("✨ Optimized Prompt:")
        st.write(optimized_prompt)

        # Step 2: Split into subtasks
        st.info("🧩 Step 2: Analyzing and splitting tasks...")
        analysis_prompt = (
            "Split this prompt into subtasks (if needed). "
            "Each task should be one clear line (if only one, just return one line):\n\n"
            f"{optimized_prompt}"
        )
        subtasks_response_raw = safe_openai_chat(analysis_prompt)
        if not subtasks_response_raw:
            st.stop()
        subtasks = [t.strip() for t in subtasks_response_raw.split("\n") if t.strip()]

        st.subheader("🧩 Subtasks Identified:")
        for t in subtasks:
            st.write(f"- {t}")

        # Step 3: Assign to best models and run
        st.info("🤖 Step 3: Assigning to best AI models and generating results...")
        results = []
        for subtask in subtasks:
            model = route_task(subtask)
            st.write(f"**{subtask} → {model}**")
            ai_task_prompt = f"[{model}] Execute this task as best as possible:\n{subtask}"
            ai_response = safe_openai_chat(ai_task_prompt)
            results.append(
                f"### Task: {subtask}\n**Model:** {model}\n**Result:**\n{ai_response}\n"
            )

        # Final merged output
        st.subheader("🧠 Final Merged Output:")
        st.markdown("\n\n".join(results))

        # Optionally, allow user to download output
        st.download_button(
            label="Download Results",
            data="\n\n".join(results),
            file_name="nefron_output.md",
            mime="text/markdown"
        )