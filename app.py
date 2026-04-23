import streamlit as st
from PIL import Image
from scripts.bone_resnet import analyze_bone_with_custom_model
from scripts.processor import analyze_chest
from scripts.summarizer import generate_medical_summary
from scripts.chat import chat_with_report

st.set_page_config(page_title="Medical AI Dashboard", layout="wide")

# ------------------------
# SESSION STATE INIT
# ------------------------
if "analysis_done" not in st.session_state:
    st.session_state.analysis_done = False

if "finding" not in st.session_state:
    st.session_state.finding = None

if "confidence" not in st.session_state:
    st.session_state.confidence = None

if "summary" not in st.session_state:
    st.session_state.summary = None

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "last_uploaded_file" not in st.session_state:
    st.session_state.last_uploaded_file = None

if "chat_input" not in st.session_state:
    st.session_state.chat_input = ""

# ------------------------
# CHAT HANDLER
# ------------------------
def handle_user_input():
    user_question = st.session_state.chat_input.strip()

    if user_question:
        answer = chat_with_report(
            st.session_state.finding,
            st.session_state.confidence,
            st.session_state.summary,
            user_question,
        )

        # Save as pair: Question then Answer
        st.session_state.chat_history.append(("You", user_question))
        st.session_state.chat_history.append(("AI", answer))

        st.session_state.chat_input = ""

# ------------------------
# HEADER
# ------------------------
st.title("🩺 AI Medical X-Ray Analysis System")
st.markdown("Upload an X-ray to detect fractures or chest diseases using AI.")

# ------------------------
# SIDEBAR
# ------------------------
analysis_mode = st.sidebar.radio("Select X-Ray Type:", ("Bone", "Chest"))
language = st.sidebar.selectbox("Report Language:", ("English", "Marathi", "Hindi"))

# ------------------------
# FILE UPLOAD
# ------------------------
uploaded_file = st.file_uploader("📤 Upload X-ray Image", type=["jpg", "jpeg", "png"])

# RESET on new image
if uploaded_file is not None:
    if uploaded_file != st.session_state.last_uploaded_file:
        st.session_state.analysis_done = False
        st.session_state.finding = None
        st.session_state.confidence = None
        st.session_state.summary = None
        st.session_state.chat_history = []
        st.session_state.chat_input = ""
        st.session_state.last_uploaded_file = uploaded_file

# ------------------------
# MAIN UI
# ------------------------
if uploaded_file:
    image = Image.open(uploaded_file)

    # ========================
    # ROW 1: IMAGE + RESULT
    # ========================
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("Uploaded X-ray")
        st.image(image, width="stretch")

    with col2:
        if st.button("🔍 Generate Full Analysis"):
            st.session_state.analysis_done = True

            temp_path = "temp_processing.jpg"
            image.save(temp_path)

            with st.spinner("Analyzing X-ray... Please wait"):
                if "Bone" in analysis_mode:
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

            if "Normal" in finding:
                st.success(f"🟢 {finding}")
            else:
                st.error(f"🔴 {finding}")

            st.metric("Confidence", f"{confidence * 100:.2f}%")

    # ========================
    # ROW 2: SUMMARY + CHAT
    # ========================
    if st.session_state.analysis_done:

        col3, col4 = st.columns([1, 1])

        # -------- LEFT: SUMMARY --------
        with col3:
            if language == "Marathi":
                st.subheader("📝 वैद्यकीय सारांश")
            elif language == "Hindi":
                st.subheader("📝 चिकित्सा सारांश")
            else:
                st.subheader("📝 Medical Summary")

            summary = st.session_state.summary
            formatted_summary = summary.replace("\n", "<br>")

            st.markdown(
                f"""
                <div style="
                    font-size:16px;
                    line-height:1.8;
                    padding:15px;
                    background-color:#f9fafc;
                    border-radius:10px;
                    border-left:5px solid #2E86C1;
                ">
                    {formatted_summary}
                </div>
                """,
                unsafe_allow_html=True
            )

        # -------- RIGHT: CHAT --------
        with col4:
            st.subheader("💬 Ask Questions")

            st.text_input(
                "Type your question...",
                key="chat_input",
                on_change=handle_user_input
            )

            # Show newest Q&A pair first
            history = st.session_state.chat_history

            for i in range(len(history) - 2, -1, -2):
                user_role, user_msg = history[i]
                ai_role, ai_msg = history[i + 1]

                st.markdown(f"**🧑 You:** {user_msg}")
                st.markdown(f"**🤖 AI:** {ai_msg}")
                st.write("")