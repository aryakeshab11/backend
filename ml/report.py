import json


def generate_validation_report(results: list[dict[str, float]]) -> str:
    report = {
        "summary": {
            "best_model": max(results, key=lambda r: r["f1_macro"]),
            "models_evaluated": len(results),
        },
        "results": results,
    }
    return json.dumps(report, indent=2)
