from pathlib import Path

import joblib


def save_model(model, model_name: str, version: str):
    directory = Path("models")
    directory.mkdir(exist_ok=True)
    path = directory / f"{model_name}_{version}.joblib"
    joblib.dump(model, path)
    print(f"Saved model: {path}")
