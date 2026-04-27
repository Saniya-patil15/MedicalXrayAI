from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import shutil

from scripts.processor import analyze_chest
from scripts.bone_resnet import analyze_bone_with_custom_model
from scripts.summarizer import generate_medical_summary
from scripts.chat import chat_with_report

app = FastAPI()

# ---------------------------------------------------
# CORS
# ---------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------
# REQUEST MODELS
# ---------------------------------------------------
class SummaryRequest(BaseModel):
    finding: str
    confidence: float
    language: str
    analysis_mode: str


class ChatRequest(BaseModel):
    finding: str
    confidence: float
    summary: str
    question: str
    language: str


# ---------------------------------------------------
# HOME
# ---------------------------------------------------
@app.get("/")
def home():
    return {"message": "Medical X-Ray AI Backend Running"}


# ---------------------------------------------------
# CHEST ANALYSIS API
# ---------------------------------------------------
@app.post("/analyze-chest")
async def analyze_uploaded_chest(file: UploadFile = File(...)):
    file_path = f"temp_{file.filename}"

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    result = analyze_chest(file_path)
    return result


# ---------------------------------------------------
# BONE ANALYSIS API
# ---------------------------------------------------
@app.post("/analyze-bone")
async def analyze_uploaded_bone(file: UploadFile = File(...)):
    file_path = f"temp_{file.filename}"

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    finding, confidence = analyze_bone_with_custom_model(
        file_path,
        "models/bone_fracture_resnet.pth"
    )

    return {
        "prediction": finding,
        "confidence": confidence
    }


# ---------------------------------------------------
# SUMMARY API
# ---------------------------------------------------
@app.post("/generate-summary")
def generate_summary(data: SummaryRequest):

    summary = generate_medical_summary(
        data.finding,
        data.confidence,
        data.language,
        data.analysis_mode
    )

    return {
        "summary": summary
    }


# ---------------------------------------------------
# CHAT API
# ---------------------------------------------------
@app.post("/chat")
def chat_api(data: ChatRequest):

    answer = chat_with_report(
        data.finding,
        data.confidence,
        data.summary,
        data.question,
        data.language
    )

    return {
        "answer": answer
    }