from __future__ import annotations
from backend.app.agents.router import build_agent_response


def test_routes_diabetes_message():
    agent_name, _ = build_agent_response("How do I manage blood sugar after dinner?", user_profile={"health_focus": "diabetes"})
    assert agent_name == "diabetes"


def test_routes_heart_health_message():
    agent_name, _ = build_agent_response("What improves heart health with high blood pressure?", user_profile={"health_focus": "general_wellness"})
    assert agent_name == "heart_health"


def test_routes_general_wellness_when_unmatched():
    agent_name, _ = build_agent_response("How can I sleep better and reduce stress?", user_profile={"health_focus": "general_wellness"})
    assert agent_name == "general_wellness"


def test_urgent_symptom_routes_to_safety_triage():
    agent_name, response = build_agent_response("I have chest pain and trouble breathing", user_profile={"health_focus": "general_wellness"})
    assert agent_name == "safety_triage"
    assert "seek immediate medical attention" in response.lower()
