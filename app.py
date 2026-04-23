import streamlit as st
from PIL import Image
from scripts.bone_resnet import analyze_bone_with_custom_model
from scripts.processor import analyze_chest
from scripts.summarizer import generate_medical_summary
from scripts.chat import chat_with_report

# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------
st.set_page_config(
    page_title="Medical AI Dashboard",
    layout="wide"
)

# ---------------------------------------------------
# SESSION STATE
# ---------------------------------------------------
defaults = {
    "analysis_done": False,
    "finding": None,
    "confidence": None,
    "summary": None,
    "chat_history": [],
    "chat_input": "",
    "chat_open": False,
    "last_uploaded_file": None
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# ---------------------------------------------------
# CHAT FUNCTION
# ---------------------------------------------------
def handle_user_input():
    question = st.session_state.chat_input.strip()

    if question:
        answer = chat_with_report(
            st.session_state.finding,
            st.session_state.confidence,
            st.session_state.summary,
            question
        )

        st.session_state.chat_history.append(("You", question))
        st.session_state.chat_history.append(("AI", answer))
        st.session_state.chat_input = ""

# ---------------------------------------------------
# CUSTOM CSS
# ---------------------------------------------------
st.markdown("""
<style>
.chat-toggle button {
    position: fixed;
    right: 25px;
    bottom: 25px;
    width: 65px;
    height: 65px;
    border-radius: 50%;
    font-size: 28px;
    z-index: 99999;
}

.chat-panel {
    position: fixed;
    right: 25px;
    bottom: 105px;
    width: 430px;
    height: 620px;
    background: white;
    border-radius: 20px;
    box-shadow: 0px 10px 35px rgba(0,0,0,0.25);
    z-index: 9999;
    padding: 0;
    overflow: hidden;
    border: 1px solid #ddd;
}

.chat-header {
    background: linear-gradient(90deg,#ff7300,#ff9a3c);
    color: white;
    padding: 18px;
    font-size: 22px;
    font-weight: bold;
}

.chat-body {
    height: 440px;
    overflow-y: auto;
    padding: 15px;
    background: #f8f9fa;
}

.user-row {
    text-align: right;
    margin-bottom: 12px;
}

.ai-row {
    text-align: left;
    margin-bottom: 15px;
}

.user-bubble {
    background: #0084ff;
    color: white;
    padding: 10px 14px;
    border-radius: 18px;
    display: inline-block;
    max-width: 80%;
}

.ai-bubble {
    background: #e5e7eb;
    color: black;
    padding: 10px 14px;
    border-radius: 18px;
    display: inline-block;
    max-width: 80%;
}

.chat-input-box {
    padding: 12px;
    background: white;
    border-top: 1px solid #eee;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------
# HEADER
# ---------------------------------------------------
st.title("🩺 AI Medical X-Ray Analysis System")
st.markdown("Upload an X-ray to detect fractures or chest diseases using AI.")

# ---------------------------------------------------
# SIDEBAR
# ---------------------------------------------------
analysis_mode = st.sidebar.radio("Select X-Ray Type:", ("Bone", "Chest"))
language = st.sidebar.selectbox(
    "Report Language:",
    ("English", "Marathi", "Hindi")
)

# ---------------------------------------------------
# UPLOAD
# ---------------------------------------------------
uploaded_file = st.file_uploader(
    "📤 Upload X-ray Image",
    type=["jpg", "jpeg", "png"]
)

# Reset when new image
if uploaded_file is not None:
    if uploaded_file != st.session_state.last_uploaded_file:
        st.session_state.analysis_done = False
        st.session_state.finding = None
        st.session_state.confidence = None
        st.session_state.summary = None
        st.session_state.chat_history = []
        st.session_state.chat_input = ""
        st.session_state.last_uploaded_file = uploaded_file

# ---------------------------------------------------
# MAIN ANALYSIS UI
# ---------------------------------------------------
if uploaded_file:
    image = Image.open(uploaded_file)

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("Uploaded X-ray")
        st.image(image, width="stretch")

    with col2:
        if st.button("🔍 Generate Full Analysis"):
            st.session_state.analysis_done = True

            temp_path = "temp_processing.jpg"
            image.save(temp_path)

            with st.spinner("Analyzing X-ray..."):
                if analysis_mode == "Bone":
                    finding, confidence = analyze_bone_with_custom_model(
                        temp_path,
                        "models/bone_fracture_resnet.pth"
                    )
                else:
                    results = analyze_chest(temp_path)
                    finding = results["prediction"]
                    confidence = results["confidence"]

                    if finding == "NORMAL":
                        finding = "Normal / No Significant Abnormalities"

                st.session_state.finding = finding
                st.session_state.confidence = confidence

                st.session_state.summary = generate_medical_summary(
                    finding,
                    confidence,
                    language,
                    analysis_mode
                )

        if st.session_state.analysis_done:
            finding = st.session_state.finding
            confidence = st.session_state.confidence

            st.subheader("📊 Analysis Result")

            if "Normal" in str(finding):
                st.success(f"🟢 {finding}")
            else:
                st.error(f"🔴 {finding}")

            st.metric("Confidence", f"{confidence*100:.2f}%")

# ---------------------------------------------------
# SUMMARY
# ---------------------------------------------------
if st.session_state.analysis_done:
    st.markdown("---")

    if language == "Marathi":
        st.subheader("📝 वैद्यकीय सारांश")
    elif language == "Hindi":
        st.subheader("📝 चिकित्सा सारांश")
    else:
        st.subheader("📝 Medical Summary")

    summary = st.session_state.summary.replace("\n", "<br>")

    st.markdown(
        f"""
        <div style="
            padding:18px;
            background:#f9fafc;
            border-left:5px solid #2E86C1;
            border-radius:12px;
            font-size:16px;
            line-height:1.8;">
            {summary}
        </div>
        """,
        unsafe_allow_html=True
    )

# ---------------------------------------------------
# FLOATING BUTTON
# ---------------------------------------------------
st.markdown('<div class="chat-toggle">', unsafe_allow_html=True)
if st.button("💬"):
    st.session_state.chat_open = not st.session_state.chat_open
st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------------------------------
# LARGE CHAT POPUP
# ---------------------------------------------------
if st.session_state.chat_open and st.session_state.analysis_done:

    chat_html = """
    <div class="chat-panel">
        <div class="chat-header">🤖 Medical AI Assistant</div>
        <div class="chat-body">
    """

    history = st.session_state.chat_history

    for i in range(0, len(history), 2):
        user_msg = history[i][1]
        ai_msg = history[i + 1][1]

        chat_html += f"""
        <div class="user-row">
            <span class="user-bubble">{user_msg}</span>
        </div>

        <div class="ai-row">
            <span class="ai-bubble">{ai_msg}</span>
        </div>
        """

    chat_html += "</div></div>"

    st.markdown(chat_html, unsafe_allow_html=True)

    # spacer so input appears in popup area visually
    st.markdown("<br><br><br><br><br><br><br><br>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([5, 4, 1])

    with col2:
        st.text_input(
            "Type your question...",
            key="chat_input",
            on_change=handle_user_input
        )