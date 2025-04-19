import streamlit as st
import base64
import json
import time
from PyPDF2 import PdfReader
from streamlit_lottie import st_lottie
from google.generativeai import configure, GenerativeModel

# Configure Gemini API
configure(api_key="AIzaSyB-N8Jf_wJciQWc0AWlUOXv6Y-QDdfeI88")
model = GenerativeModel("gemini-1.5-pro")

# Punchlines
punchlines = [
    "Cooking your resume roast...🔥",
    "Adding some extra spice...🌶",
    "Your career is about to get flamed...💥",
    "Checking for buzzwords... 🕵",
    "Roasting responsibly... 🍳",
    "Almost done, hang tight...⏳"
]

# Load Lottie
def load_lottiefile(filepath: str):
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

# Background
def set_background(image_file):
    with open(image_file, "rb") as img_file:
        encoded = base64.b64encode(img_file.read()).decode()
    st.markdown(f"""
        <style>
        .stApp {{
            background-image: url("data:image/png;base64,{encoded}");
            background-size: cover;
            background-position: center;
        }}
        </style>
    """, unsafe_allow_html=True)

# Session init
if "page" not in st.session_state:
    st.session_state.page = 0

# PAGE 0 - Welcome
if st.session_state.page == 0:
    set_background("background1.png")
    st.markdown("""
        <style>
        .centered-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 85vh;
            text-align: center;
        }
        .custom-title {
            font-size: 60px;
            color: white;
            margin-bottom: 0.5rem;
        }
        .custom-subtitle {
            font-size: 24px;
            color: white;
            margin-bottom: 2rem;
        }
        div.stButton > button {
            background-color: #FF4B4B;
            color: white;
            font-size: 18px;
            padding: 0.75rem 1.5rem;
            border-radius: 8px;
            border: none;
            cursor: pointer;
        }
        div.stButton {
            display: flex;
            justify-content: center;
            margin-top: -40px;
        }
        </style>
        <div class="centered-container">
            <div class="custom-title">Roastify 🔥</div>
            <div class="custom-subtitle">Your resume’s worst nightmare 😈</div>
        </div>
    """, unsafe_allow_html=True)

    if st.button("Upload your Resume (if you dare)"):
        st.session_state.page = 1
        st.rerun()

# PAGE 1 - Upload
elif st.session_state.page == 1:
    set_background("background2.png")
    st.header("Let's get this roast cookin' 🍳")
    uploaded_pdf = st.file_uploader("Upload your resume (PDF only)", type=["pdf"])
    industry = st.selectbox("Select your industry", ["Tech", "Marketing", "Design", "Finance", "General"])
    mode = st.radio("Choose roast mode", ["Funny", "Serious"])

    if st.button("Submit for Roastin' 🔥"):
        if uploaded_pdf:
            st.session_state.resume = uploaded_pdf
            st.session_state.industry = industry
            st.session_state.mode = mode
            st.session_state.page = 2
            st.rerun()

# PAGE 2 - Processing
elif st.session_state.page == 2:
    st_lottie(load_lottiefile("fire.json"), height=250)
    status = st.empty()
    for i in range(6):
        status.markdown(f"### {punchlines[i % len(punchlines)]}")
        time.sleep(2)

    pdf_reader = PdfReader(st.session_state.resume)
    pdf_text = ""
    for page in pdf_reader.pages:
        pdf_text += page.extract_text()

    mode_text = "roast the resume in a witty, humorous way" if st.session_state.mode == "Funny" else "give a serious, critical analysis of the resume"

    prompt = f"""
    You are Roastify, an expert AI resume reviewer. The user uploaded a resume from the {st.session_state.industry} industry.
    Mode: {st.session_state.mode}. First, {mode_text}.
    Then provide detailed bullet-point suggestions on how to improve it.
    Finally, identify clear skill gaps and suggest free online resources (with clickable links) to bridge those gaps.

    Resume:
    {pdf_text}
    """

    response = model.generate_content(prompt)
    text = response.text

    # Attempt to split the response into roast, suggestions, and skill gaps
    try:
        # Split by clear identifiers (could be modified based on actual response format)
        roast_end_index = text.lower().find("suggestions:")
        suggestions_start_index = text.lower().find("suggestions:")
        skill_gaps_start_index = text.lower().find("skill gaps:")

        roast = text[:roast_end_index].strip() if roast_end_index != -1 else text.strip()
        suggestions = text[suggestions_start_index + len("suggestions:"):skill_gaps_start_index].strip() if suggestions_start_index != -1 else "Could not extract suggestions."
        skill_gap = text[skill_gaps_start_index + len("skill gaps:"):].strip() if skill_gaps_start_index != -1 else "Could not extract skill gaps."

    except ValueError:
        roast = text.strip()
        suggestions = "Could not extract suggestions."
        skill_gap = "Could not extract skill gaps."

    st.session_state.resume_text = pdf_text
    st.session_state.roast = roast
    st.session_state.suggestions = suggestions
    st.session_state.skill_gap = skill_gap
    st.session_state.page = 3
    st.rerun()

# PAGE 3 - Result
elif st.session_state.page == 3:
    st.balloons()

    # Top row: Resume + Roast
    col1, col2 = st.columns([1, 1.2])
    with col1:
        st.markdown("""
            <div style='background-color:#E6F4F1; padding:20px; border-radius:15px;'>
            <h4>📄 <b>Resume Text</b></h4>
        """, unsafe_allow_html=True)
        st.code(st.session_state.resume_text, language="markdown")
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("""
            <div style='background-color:#FF6B6B; padding:20px; border-radius:15px; color:white;'>
            <h4>🔥 <b>Roast</b></h4>
            <p>{}</p>
            </div>
        """.format(st.session_state.roast.replace("\n", "<br>")), unsafe_allow_html=True)

    # Bottom row: Suggestions + Skill Gap
    c1, c2 = st.columns([1, 1])  # Equal width for suggestions and skill gaps

    with c1:
        st.markdown("""
            <div style='background-color:#FFA726; padding:20px; border-radius:15px; color:white;'>
            <h4>💡 <b>Suggestions</b></h4>
            <ul>
        """, unsafe_allow_html=True)
        for line in st.session_state.suggestions.split("\n"):
            if line.strip():
                st.markdown(f"<li>{line.strip()}</li>", unsafe_allow_html=True)
        st.markdown("</ul></div>", unsafe_allow_html=True)

    with c2:
        st.markdown("""
            <div style='background-color:#4DB6AC; padding:20px; border-radius:15px; color:white;'>
            <h4>🧠 <b>Skill Gaps & Resources</b></h4>
            <ul>
        """, unsafe_allow_html=True)
        for line in st.session_state.skill_gap.split("\n"):
            if ":" in line:
                topic, link = line.split(":", 1)
                st.markdown(f"<li><b>{topic.strip()}</b>: <a href='{link.strip()}' target='_blank'>Click here</a></li>", unsafe_allow_html=True)
            elif line.strip():
                st.markdown(f"<li>{line.strip()}</li>", unsafe_allow_html=True)
        st.markdown("</ul></div>", unsafe_allow_html=True)

    if st.button("Upload another resume"):
        st.session_state.page = 0
        st.rerun()