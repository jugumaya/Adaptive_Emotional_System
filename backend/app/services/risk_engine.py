"""
Rule-Based Risk Engine
Matches: RiskAnalysis class + Activity Diagram decision node "Risk Detected?"
Assignment reference: Non-Functional Req (rule-based, non-clinical)
"""


def analyze_risk(mood_score: int) -> str:
    """Map mood score (1-10) to risk level."""
    if mood_score <= 3:
        return "HIGH"
    elif mood_score <= 6:
        return "MODERATE"
    else:
        return "LOW"


INTERVENTIONS = {
    "HIGH": {
        "suggestion": (
            "We noticed you're having a tough time right now. "
            "Try box breathing: inhale 4s, hold 4s, exhale 4s, hold 4s. Repeat 3 times. "
            "Consider reaching out to your university counselor for additional support."
        ),
        "type": "BREATHING",
    },
    "MODERATE": {
        "suggestion": (
            "You seem a bit stressed. Take a 5-minute break — stand up, stretch, drink water. "
            "Breaking tasks into smaller steps can help reduce overwhelm. You've got this!"
        ),
        "type": "FOCUS",
    },
    "LOW": {
        "suggestion": (
            "Great emotional balance today! Keep it up by maintaining healthy sleep, "
            "staying connected with friends, and taking short breaks during study sessions."
        ),
        "type": "MOTIVATIONAL",
    },
}


def get_intervention(risk_level: str) -> dict:
    return INTERVENTIONS.get(risk_level, INTERVENTIONS["LOW"])
