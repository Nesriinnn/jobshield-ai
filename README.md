# JobShield AI

JobShield AI is a full-stack AI-powered web application that detects suspicious and fraudulent job postings. Users can paste a job description, and the system predicts whether the post is likely to be legitimate or fraudulent.

The project uses a FastAPI backend, a HTML/CSS/JavaScript frontend, and a machine learning model trained with TF-IDF Vectorization and Logistic Regression.

## Features

- Analyze job descriptions for scam risk
- Predict whether a job post is legitimate or fraudulent
- Display fraud score as a percentage
- Show risk level: Low, Medium, or High
- Provide confidence score
- Show AI-generated explanation
- Detect suspicious red flags such as:
  - Registration fee
  - Urgent hiring
  - Guaranteed selection
  - No interview
  - Processing fee
  - Bank details request
- Dashboard page
- History page
- Loading animation while analyzing
- Friendly error messages if backend is not running
- Responsive dark-themed UI

## Tech Stack

### Frontend
- HTML
- CSS
- JavaScript

### Backend
- Python
- FastAPI
- Uvicorn

### Machine Learning
- Scikit-learn
- TF-IDF Vectorizer
- Logistic Regression
- Joblib
- Pandas

## Project Structure

```text
jobshield-ai/
|-- backend/
|   |-- main.py
|   |-- train_model.py
|   |-- model_metadata.json
|
|-- dataset/
|   |-- fake_job_postings.csv
|
|-- frontend/
|   |-- index.html
|   |-- style.css
|   |-- script.js
|
|-- requirements.txt
|-- README.md

Dataset
This project uses the Fake Job Posting Dataset.

Place the dataset file inside the dataset folder:

dataset/fake_job_postings.csv
Important columns used:

description
fraudulent
The training script can also use additional columns if available, such as:

title
company_profile
requirements
benefits
industry
function
Installation
Clone the repository:

git clone https://github.com/YOUR_USERNAME/jobshield-ai.git
Go to the project folder:

cd jobshield-ai
Install dependencies:

py -m pip install -r requirements.txt
Train the Machine Learning Model
Before running the backend, place fake_job_postings.csv inside the dataset folder.

Then run:

py backend/train_model.py
This will create:

backend/jobshield_model.pkl
backend/vectorizer.pkl
backend/model_metadata.json
Run the Backend
Start the FastAPI server:

py -m uvicorn backend.main:app --reload
Backend will run at:

http://127.0.0.1:8000
Run the Frontend
Open this file in your browser:

frontend/index.html
Make sure the backend server is running before analyzing job descriptions.

API Endpoint
POST /analyze
Request body:

{
  "job_text": "Urgent hiring work from home job. Pay registration fee now for guaranteed selection."
}
Example response:

{
  "verdict": "Fraudulent",
  "fraud_score": 82,
  "risk_level": "High",
  "confidence_score": 53,
  "explanation": "The model found this posting similar to known fraudulent job descriptions. It also detected suspicious signals in the text.",
  "red_flags": [
    "Asks for a registration fee",
    "Uses urgent hiring pressure",
    "Promises guaranteed selection"
  ]
}
Machine Learning Workflow
Load the dataset
Clean missing values
Combine useful text columns
Split data into training and testing sets
Convert text into numerical features using TF-IDF
Train Logistic Regression model
Calibrate fraud probability
Evaluate model performance
Save model and vectorizer using Joblib
Use saved model in FastAPI backend

=> Future Improvements

Add user login
Store analysis history in a database
Export analysis reports as PDF
Verify company websites and email domains
Add admin dashboard
Deploy backend and frontend online
Retrain model with newer scam examples

=>Conclusion

JobShield AI demonstrates how machine learning can be used to solve a real-world problem. The project helps job seekers identify suspicious job postings by combining NLP, machine learning, and a simple web interface.
