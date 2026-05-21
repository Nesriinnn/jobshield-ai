from pathlib import Path
from typing import Any
import json

import joblib
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field


APP_DIR = Path(__file__).resolve().parent
MODEL_PATH = APP_DIR / "jobshield_model.pkl"
VECTORIZER_PATH = APP_DIR / "vectorizer.pkl"
METADATA_PATH = APP_DIR / "model_metadata.json"
DEFAULT_FRAUD_THRESHOLD = 0.5

SUSPICIOUS_KEYWORDS = {
    "registration fee": "Asks for a registration fee",
    "processing fee": "Mentions a processing fee",
    "security deposit": "Requests a security deposit",
    "urgent hiring": "Uses urgent hiring pressure",
    "guaranteed selection": "Promises guaranteed selection",
    "no interview": "Claims no interview is needed",
    "earn instantly": "Promises instant earnings",
    "work from home": "Uses broad work-from-home wording",
    "limited seats": "Creates artificial scarcity",
    "whatsapp": "Moves communication to WhatsApp",
    "bank details": "Requests sensitive bank details",
    "pay now": "Pushes immediate payment",
}


class AnalyzeRequest(BaseModel):
    job_text: str = Field(..., min_length=20, description="Job description text to analyze")


class AnalyzeResponse(BaseModel):
    verdict: str
    fraud_score: int
    risk_level: str
    confidence_score: int
    explanation: str
    red_flags: list[str]


app = FastAPI(
    title="JobShield AI API",
    description="AI-powered job scam detection using TF-IDF and Logistic Regression.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

model: Any | None = None
vectorizer: Any | None = None
model_metadata: dict[str, Any] = {"fraud_threshold": DEFAULT_FRAUD_THRESHOLD}


def load_ml_assets() -> None:
    """Load trained ML files once when the API starts."""
    global model, vectorizer, model_metadata

    if not MODEL_PATH.exists() or not VECTORIZER_PATH.exists():
        model = None
        vectorizer = None
        model_metadata = {"fraud_threshold": DEFAULT_FRAUD_THRESHOLD}
        return

    model = joblib.load(MODEL_PATH)
    vectorizer = joblib.load(VECTORIZER_PATH)
    if METADATA_PATH.exists():
        model_metadata = json.loads(METADATA_PATH.read_text(encoding="utf-8"))
    else:
        model_metadata = {"fraud_threshold": DEFAULT_FRAUD_THRESHOLD}


@app.on_event("startup")
def startup_event() -> None:
    load_ml_assets()


@app.get("/")
def health_check() -> dict[str, str]:
    return {
        "message": "JobShield AI backend is running",
        "model_status": "loaded" if model is not None and vectorizer is not None else "not trained",
    }


def detect_red_flags(text: str) -> list[str]:
    lower_text = text.lower()
    return [
        reason
        for keyword, reason in SUSPICIOUS_KEYWORDS.items()
        if keyword in lower_text
    ]


def get_risk_level(score: int) -> str:
    if score >= 75:
        return "High"
    if score >= 45:
        return "Medium"
    return "Low"


def build_explanation(verdict: str, score: int, red_flags: list[str]) -> str:
    if verdict == "Fraudulent":
        base = "The model found this posting similar to known fraudulent job descriptions."
    else:
        base = "The model found this posting closer to legitimate job descriptions."

    if red_flags:
        return f"{base} It also detected {len(red_flags)} suspicious signal(s) in the text."

    if score >= 45:
        return f"{base} No direct keyword red flags were found, but the overall language still looks risky."

    return f"{base} No strong scam keyword patterns were detected."


@app.post("/analyze", response_model=AnalyzeResponse)
def analyze_job(request: AnalyzeRequest) -> AnalyzeResponse:
    if model is None or vectorizer is None:
        raise HTTPException(
            status_code=503,
            detail=(
                "ML model is not trained yet. Run `python backend/train_model.py` "
                "and restart the FastAPI server."
            ),
        )

    job_text = request.job_text.strip()
    if len(job_text) < 20:
        raise HTTPException(status_code=400, detail="Please enter a longer job description.")

    text_vector = vectorizer.transform([job_text])
    probabilities = model.predict_proba(text_vector)[0]
    fraud_class_index = list(model.classes_).index(1)
    fraud_probability = float(probabilities[fraud_class_index])

    red_flags = detect_red_flags(job_text)
    model_score = round(fraud_probability * 100)
    red_flag_boost = min(len(red_flags) * 7, 35)
    fraud_score = min(99, model_score + red_flag_boost)

    fraud_threshold = float(model_metadata.get("fraud_threshold", DEFAULT_FRAUD_THRESHOLD))
    verdict = "Fraudulent" if fraud_probability >= fraud_threshold or fraud_score >= 55 else "Legitimate"
    confidence_score = round(max(probabilities) * 100)
    risk_level = get_risk_level(fraud_score)
    explanation = build_explanation(verdict, fraud_score, red_flags)

    return AnalyzeResponse(
        verdict=verdict,
        fraud_score=fraud_score,
        risk_level=risk_level,
        confidence_score=confidence_score,
        explanation=explanation,
        red_flags=red_flags,
    )
