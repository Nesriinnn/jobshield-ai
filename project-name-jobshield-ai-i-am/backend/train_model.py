from pathlib import Path
import json

import joblib
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    classification_report,
    precision_recall_curve,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split


BASE_DIR = Path(__file__).resolve().parent.parent
DATASET_PATH = BASE_DIR / "dataset" / "fake_job_postings.csv"
MODEL_PATH = Path(__file__).resolve().parent / "jobshield_model.pkl"
VECTORIZER_PATH = Path(__file__).resolve().parent / "vectorizer.pkl"
METADATA_PATH = Path(__file__).resolve().parent / "model_metadata.json"

TEXT_COLUMNS = [
    "title",
    "company_profile",
    "description",
    "requirements",
    "benefits",
    "employment_type",
    "required_experience",
    "required_education",
    "industry",
    "function",
]


def load_dataset() -> pd.DataFrame:
    """Load and validate the Kaggle fake job postings dataset."""
    if not DATASET_PATH.exists():
        raise FileNotFoundError(
            f"Dataset not found at {DATASET_PATH}. "
            "Place fake_job_postings.csv inside the dataset folder."
        )

    data = pd.read_csv(DATASET_PATH)
    required_columns = {"description", "fraudulent"}
    missing_columns = required_columns.difference(data.columns)

    if missing_columns:
        raise ValueError(f"Dataset is missing required columns: {missing_columns}")

    return data


def prepare_data(data: pd.DataFrame) -> tuple[pd.Series, pd.Series]:
    """Create one rich text field from useful job-post columns."""
    available_text_columns = [column for column in TEXT_COLUMNS if column in data.columns]
    cleaned = data[available_text_columns + ["fraudulent"]].copy()

    for column in available_text_columns:
        cleaned[column] = cleaned[column].fillna("").astype(str)

    cleaned["combined_text"] = cleaned[available_text_columns].agg(" ".join, axis=1)
    cleaned["fraudulent"] = cleaned["fraudulent"].fillna(0).astype(int)

    cleaned = cleaned[cleaned["combined_text"].str.strip().astype(bool)]
    return cleaned["combined_text"], cleaned["fraudulent"]


def find_best_threshold(labels: pd.Series, fraud_probabilities: list[float]) -> float:
    """Pick a threshold that balances precision and recall for fake-job detection."""
    precisions, recalls, thresholds = precision_recall_curve(labels, fraud_probabilities)
    f1_scores = (2 * precisions * recalls) / (precisions + recalls + 1e-9)
    best_index = int(f1_scores[:-1].argmax())
    return float(thresholds[best_index])


def train_model() -> None:
    data = load_dataset()
    texts, labels = prepare_data(data)

    x_train, x_test, y_train, y_test = train_test_split(
        texts,
        labels,
        test_size=0.2,
        random_state=42,
        stratify=labels,
    )

    vectorizer = TfidfVectorizer(
        lowercase=True,
        stop_words="english",
        max_features=30000,
        ngram_range=(1, 3),
        min_df=2,
        max_df=0.92,
        sublinear_tf=True,
    )

    x_train_vectors = vectorizer.fit_transform(x_train)
    x_test_vectors = vectorizer.transform(x_test)

    base_model = LogisticRegression(
        class_weight="balanced",
        C=2.0,
        max_iter=2000,
        random_state=42,
    )
    model = CalibratedClassifierCV(base_model, method="sigmoid", cv=3)
    model.fit(x_train_vectors, y_train)

    fraud_class_index = list(model.classes_).index(1)
    fraud_probabilities = model.predict_proba(x_test_vectors)[:, fraud_class_index]
    best_threshold = find_best_threshold(y_test, fraud_probabilities)
    predictions = (fraud_probabilities >= best_threshold).astype(int)
    accuracy = accuracy_score(y_test, predictions)
    roc_auc = roc_auc_score(y_test, fraud_probabilities)
    average_precision = average_precision_score(y_test, fraud_probabilities)

    print(f"Training complete. Accuracy: {accuracy:.4f}")
    print(f"ROC-AUC: {roc_auc:.4f}")
    print(f"Average precision: {average_precision:.4f}")
    print(f"Best fraud threshold: {best_threshold:.4f}")
    print("\nClassification report:")
    print(classification_report(y_test, predictions, target_names=["Real", "Fraudulent"]))

    joblib.dump(model, MODEL_PATH)
    joblib.dump(vectorizer, VECTORIZER_PATH)
    METADATA_PATH.write_text(
        json.dumps(
            {
                "fraud_threshold": round(best_threshold, 4),
                "accuracy": round(accuracy, 4),
                "roc_auc": round(roc_auc, 4),
                "average_precision": round(average_precision, 4),
                "text_columns": [column for column in TEXT_COLUMNS if column in data.columns],
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    print(f"\nSaved model to: {MODEL_PATH}")
    print(f"Saved vectorizer to: {VECTORIZER_PATH}")
    print(f"Saved metadata to: {METADATA_PATH}")


if __name__ == "__main__":
    train_model()
