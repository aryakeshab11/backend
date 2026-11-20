TRAINING_CONFIG = {
    "dataset_path": "data/training/health_agent_dataset.csv",
    "models_to_test": ["logreg", "svm", "nb"],
    "random_state": 42,
    "test_size": 0.2,
    "languages": ["en", "ne", "hi", "es", "fr", "de"],
    "allowed_labels": [
        "tuna",
        "muna",
        "suna",
        "safety_triage",
        "general_wellness",
    ],
}
