import json

import pandas as pd
from backend.ml.config import TRAINING_CONFIG
from backend.ml.preprocessing import normalize_text
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.svm import LinearSVC

DATASET_PATH = TRAINING_CONFIG["dataset_path"]


def load_dataset(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    required = ["text", "label", "agent_name", "language", "source_type", "urgency_flag"]
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"Missing columns: {missing}")
    return df


def clean_dataset(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["text"] = df["text"].fillna("").astype(str)
    df["text"] = df["text"].apply(normalize_text)
    df["label"] = df["label"].str.lower().str.strip()
    return df


def split_data(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    y = df["label"]
    X = df["text"]

    X_train, X_temp, y_train, y_temp = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y,
    )

    X_val, X_test, y_val, y_test = train_test_split(
        X_temp,
        y_temp,
        test_size=0.5,
        random_state=42,
        stratify=y_temp,
    )

    train_df = pd.DataFrame({"text": X_train, "label": y_train})
    val_df = pd.DataFrame({"text": X_val, "label": y_val})
    test_df = pd.DataFrame({"text": X_test, "label": y_test})

    return train_df, val_df, test_df


def build_model(name: str):
    if name == "logreg":
        return Pipeline([
            ("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=2)),
            ("clf", LogisticRegression(max_iter=1000, class_weight="balanced")),
        ])
    if name == "svm":
        return Pipeline([
            ("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=2)),
            ("clf", LinearSVC(class_weight="balanced")),
        ])
    if name == "nb":
        return Pipeline([
            ("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=2)),
            ("clf", MultinomialNB()),
        ])
    raise ValueError(f"Unknown model: {name}")


def evaluate_model(model, X_test: pd.Series, y_test: pd.Series) -> dict[str, float]:
    preds = model.predict(X_test)

    metrics = {
        "accuracy": accuracy_score(y_test, preds),
        "precision_macro": precision_score(y_test, preds, average="macro", zero_division=0),
        "recall_macro": recall_score(y_test, preds, average="macro", zero_division=0),
        "f1_macro": f1_score(y_test, preds, average="macro", zero_division=0),
    }

    return metrics


def train_and_eval():
    df = load_dataset(DATASET_PATH)
    df = clean_dataset(df)
    train_df, _val_df, test_df = split_data(df)

    X_train, y_train = train_df["text"], train_df["label"]
    X_test, y_test = test_df["text"], test_df["label"]

    for model_name in TRAINING_CONFIG["models_to_test"]:
        model = build_model(model_name)
        model.fit(X_train, y_train)
        metrics = evaluate_model(model, X_test, y_test)
        print(f"\nModel: {model_name}")
        print(json.dumps(metrics, indent=2, default=str))

        preds = model.predict(X_test)
        print(classification_report(y_test, preds))
        print("Confusion Matrix:")
        print(confusion_matrix(y_test, preds, labels=sorted(y_test.unique())))

        # Do not save the model here. Keep this as a validation-only step until
        # review passes and the model is approved for production use.


if __name__ == "__main__":
    train_and_eval()
