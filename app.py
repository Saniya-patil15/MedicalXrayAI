import streamlit as st
from PIL import Image
from scripts.bone_resnet import analyze_bone_with_custom_model
from scripts.processor import analyze_chest
from scripts.summarizer import generate_medical_summary

st.set_page_config(page_title="Medical AI Dashboard", layout="wide")

# ------------------------
# HEADER
# ------------------------
st.title("🩺 AI Medical X-Ray Analysis System")
st.markdown("Upload an X-ray to detect fractures or chest diseases using AI.")

# ------------------------
# SIDEBAR
# ------------------------
analysis_mode = st.sidebar.radio(
    "Select X-Ray Type:",
    ("Bone", "Chest")
)

language = st.sidebar.selectbox(
    "Report Language:",
    ("English", "Marathi", "Hindi")
)

# ------------------------
# FILE UPLOAD
# ------------------------
uploaded_file = st.file_uploader(
    "📤 Upload X-ray Image",
    type=["jpg", "jpeg", "png"]
)

if uploaded_file:
    image = Image.open(uploaded_file)

    col1, col2 = st.columns([1, 1])

    # ------------------------
    # LEFT: IMAGE PREVIEW
    # ------------------------
    with col1:
        st.subheader("Uploaded X-ray")
        st.image(image, width="stretch")

    # ------------------------
    # RIGHT: ANALYSIS
    # ------------------------
    with col2:
        if st.button("🔍 Generate Full Analysis"):

            temp_path = "temp_processing.jpg"
            image.save(temp_path)

            with st.spinner("Analyzing X-ray... Please wait"):

                # ------------------------
                # BONE MODEL
                # ------------------------
                if "Bone" in analysis_mode:
                    finding, confidence = analyze_bone_with_custom_model(
                        temp_path,
                        "models/bone_fracture_resnet.pth"
                    )

                # ------------------------
                # CHEST MODEL
                # ------------------------
                else:
                    results = analyze_chest(temp_path)
                    finding = results["prediction"]
                    confidence = results["confidence"]

                    if finding == "NORMAL":
                        finding = "Normal / No Significant Abnormalities"

                # ------------------------
                # RESULT DISPLAY
                # ------------------------

                st.subheader("📊 Analysis Result")

                # Color logic
                if "Normal" in finding:
                    st.success(f"🟢 {finding}")
                else:
                    st.error(f"🔴 {finding}")

                st.metric("Confidence", f"{confidence * 100:.2f}%")

                # ------------------------
                # SUMMARY
                # ------------------------
                if language == "Marathi":
                    st.subheader("📝 वैद्यकीय सारांश")
                elif language == "Hindi":
                    st.subheader("📝 चिकित्सा सारांश")
                else:
                    st.subheader("📝 Medical Summary")

                summary = generate_medical_summary(
                    finding,
                    confidence,
                    language,
                    analysis_mode
                )

                # ------------------------
                # FORMATTED DISPLAY (UPDATED)
                # ------------------------
                formatted_summary = summary.replace("\n", "<br>")

                if language in ["Marathi", "Hindi"]:
                    st.markdown(
                        f"""<div style="
                            font-family: 'Noto Sans Devanagari', 'Mangal', sans-serif;
                            font-size: 16px;
                            line-height: 1.8;
                            padding: 15px;
                            background-color: #f0f2f6;
                            border-radius: 10px;
                            border-left: 4px solid #4CAF50;
                            white-space: pre-wrap;
                        ">{formatted_summary}</div>""",
                        unsafe_allow_html=True
                    )
                else:
                    st.markdown(
                        f"""<div style="
                            font-size: 16px;
                            line-height: 1.8;
                            padding: 15px;
                            background-color: #f9fafc;
                            border-radius: 10px;
                            border-left: 5px solid #2E86C1;
                            white-space: pre-wrap;
                        ">{formatted_summary}</div>""",
                        unsafe_allow_html=True
                    )