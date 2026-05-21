# JobShield AI

JobShield AI is a full-stack AI-powered job scam detection web application. It analyzes job descriptions and predicts whether a job post looks legitimate or fraudulent.

## Features

- Paste a job description and analyze it instantly
- ML-based fraud prediction using TF-IDF and Logistic Regression
- Fraud score, risk level, confidence score, explanation, and red flags
- FastAPI backend with `/analyze` endpoint
- Dark professional frontend built with HTML, CSS, and JavaScript
- Dashboard and recent analysis history
- Loading state and friendly error handling

## Tech Stack

**Frontend**
- HTML
- CSS
- JavaScript

**Backend**
- Python
- FastAPI

**Machine Learning**
- Scikit-learn
- TF-IDF Vectorizer
- Logistic Regression
- Joblib

## Project Structure

```text
jobshield-ai/
+-- backend/
|   +-- main.py
|   +-- train_model.py
|   +-- model_metadata.json
+-- dataset/
|   +-- fake_job_postings.csv
+-- frontend/
|   +-- index.html
|   +-- style.css
|   +-- script.js
+-- requirements.txt
+-- README.md
```

## Dataset

This project uses the Fake Job Posting Dataset. Place the dataset file here:

```text
dataset/fake_job_postings.csv
```

Important columns:

- `description`
- `fraudulent`

The training script can also use extra columns if they exist, such as `title`, `company_profile`, `requirements`, `benefits`, `industry`, and `function`.

## Setup

Install dependencies:

```powershell
py -m pip install -r requirements.txt
```

Train the model:

```powershell
py backend\train_model.py
```

This creates:

```text
backend/jobshield_model.pkl
backend/vectorizer.pkl
backend/model_metadata.json
```

Start the backend:

```powershell
py -m uvicorn backend.main:app --reload
```

Backend URL:

```text
http://127.0.0.1:8000
```

Open the frontend:

```text
frontend/index.html
```

## API Response Example

```json
{
  "verdict": "Fraudulent",
  "fraud_score": 82,
  "risk_level": "High",
  "confidence_score": 53,
  "explanation": "The model found this posting similar to known fraudulent job descriptions. It also detected 6 suspicious signal(s) in the text.",
  "red_flags": [
    "Asks for a registration fee",
    "Uses urgent hiring pressure"
  ]
}
```

## Team

- Steward
- Thasnim
- Nesrin
- Sharaffu
- Raneeb
