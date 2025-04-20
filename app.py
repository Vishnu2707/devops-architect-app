import streamlit as st
import requests
import os
import json
from dotenv import load_dotenv
from utils.formatter import clean_output
from utils.diagram_gen import generate_architecture_diagram

# Load environment variables
load_dotenv()
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")

# Load system prompt components
with open("prompts/devops_intro.txt", "r") as f:
    base_prompt = f.read()

with open("prompts/writing_guidelines.txt", "r") as f:
    writing_rules = f.read()

# App setup
st.set_page_config(page_title="DevOps Architect GPT – Vish!!", layout="wide")
st.title("🛠️ DevOps Architect GPT – Things made simpler")
st.caption("Smart infra & pipeline design. Just ask or upload your config file.")

# Session state for continuity
if "full_response" not in st.session_state:
    st.session_state.full_response = ""
if "last_prompt" not in st.session_state:
    st.session_state.last_prompt = ""

# Output Mode Selector
mode = st.radio("Choose your output style:", ["💡 Full Setup", "🛠 Infra Only", "📦 Code Only", "📄 Like an SRE doc", "🧠 Just Explain"])

# Input Prompt
preset = st.selectbox("Choose a quick-start prompt or write your own:", ["", "🔐 Secure AWS Setup", "🚀 CI/CD GitHub Actions", "☁️ Terraform S3 + EC2"])
examples = {
    "🔐 Secure AWS Setup": "Help me deploy a secure and cost-effective web app on AWS using Node.js, React, and PostgreSQL.",
    "🚀 CI/CD GitHub Actions": "Here’s my GitHub Actions file. Can you review and improve it for deploying a React frontend and Node.js backend?",
    "☁️ Terraform S3 + EC2": "Please check my Terraform file. I want to host a static site on S3 behind CloudFront and run Node.js on EC2."
}
user_input = st.text_area("What's your DevOps need?", value=examples.get(preset, ""), height=140)

# File uploader
uploaded_file = st.file_uploader("Upload config or code file (optional)", type=["yaml", "yml", "tf", "json", "sh"])
file_contents = uploaded_file.read().decode("utf-8") if uploaded_file else ""

# LLM call
def call_model(prompt, model_name):
    url = "https://api.together.xyz/inference"
    headers = {
        "Authorization": f"Bearer {TOGETHER_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": model_name,
        "prompt": prompt,
        "max_tokens": 2048,
        "temperature": 0.5
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 200:
        json_data = response.json()
        if "choices" in json_data:
            return json_data["choices"][0]["text"].strip()
        elif "output" in json_data and "choices" in json_data["output"]:
            return json_data["output"]["choices"][0]["text"].strip()
        return f"⚠️ Unrecognized response format: {json.dumps(json_data)}"
    return f"❌ API Error {response.status_code}: {response.text}"

# Prompt Builder
def build_prompt(user_input, file_contents, mode):
    section = f"=== USER NEED ===\n{user_input.strip()}\n\n"
    file_block = f"=== CONFIG FILE ===\n{file_contents.strip()}\n\n" if file_contents else ""
    intent = {
        "💡 Full Setup": "Include infra, CI/CD, app setup, security, secrets, cost-saving tips, and sample code.",
        "🛠 Infra Only": "Give only infrastructure setup like Terraform or AWS Console steps.",
        "📦 Code Only": "Give only backend/frontend code and deployment-ready YAML/configs.",
        "📄 Like an SRE doc": "Write the response like an internal SRE runbook. Use headings and concise steps.",
        "🧠 Just Explain": "Explain how this setup works in plain English, step by step."
    }[mode]
    end = (
        f"{file_block}"
        f"{section}"
        f"{base_prompt}\n\n"
        f"=== WRITING GUIDELINES ===\n{writing_rules}\n\n"
        f"Now act like a senior DevOps engineer. {intent}\n"
        "Do not add generic closings. Don’t say 'let’s work together'. Don’t repeat or ask questions at the end.\n\nAssistant:"
    )
    return end

# Run
if st.button("Generate Solution"):
    if user_input.strip():
        with st.spinner("Thinking like an architect..."):
            prompt = build_prompt(user_input, file_contents, mode)
            model_choice = "meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8"
            raw_response = call_model(prompt, model_choice)
            clean = clean_output(raw_response)

            st.session_state.full_response = clean
            st.session_state.last_prompt = prompt

            st.markdown("### ✅ Suggested Solution")
            st.markdown(clean)

            if "infra" in mode.lower() or "setup" in mode.lower():
                st.markdown("---")
                st.markdown("### 🧱 Architecture Diagram")
                image = generate_architecture_diagram(clean)
                if image:
                    st.image(image, caption="Generated Diagram", use_column_width=True)
    else:
        st.warning("Please enter your problem statement.")

# Continue Button
if st.session_state.full_response:
    if st.button("🔄 Continue Answer"):
        followup_prompt = f"{st.session_state.last_prompt}\n\nContinue from where you left off:\n"
        continued_output = call_model(followup_prompt, "meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8")
        cleaned_continued = clean_output(continued_output)

        st.session_state.full_response += "\n\n" + cleaned_continued

        st.markdown("### ✅ Continued Response")
        st.markdown(st.session_state.full_response)

