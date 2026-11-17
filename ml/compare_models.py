from dataclasses import dataclass


@dataclass
class ModelResult:
    model_name: str
    accuracy: float
    precision_macro: float
    recall_macro: float
    f1_macro: float
    latency_ms: float
    model_size_mb: float
    multilingual_support: bool
    notes: str = ""
