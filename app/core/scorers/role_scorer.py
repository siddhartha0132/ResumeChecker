"""
Role-specific scoring weights for 6 EV roles.
Plugs into the ensemble scorer to apply domain-aware weighting.
"""

from typing import Dict

# ── Role weight profiles ──────────────────────────────────────────────────────

ROLE_WEIGHTS: Dict[str, Dict] = {
    "battery_engineer": {
        "technical_skills": 0.45,
        "experience_years": 0.25,
        "certifications": 0.15,
        "domain_papers": 0.10,
        "soft_skills": 0.05,
        "min_pass_score": 70,
        "key_skills": [
            "BMS", "Battery Management", "Lithium-ion", "Thermal Management",
            "Cell Balancing", "State of Charge", "ISO 26262", "MATLAB",
        ],
    },
    "powertrain_engineer": {
        "technical_skills": 0.50,
        "experience_years": 0.20,
        "certifications": 0.15,
        "soft_skills": 0.15,
        "min_pass_score": 65,
        "key_skills": [
            "Electric Motor", "Inverter", "Powertrain", "Regenerative Braking",
            "MATLAB", "Simulink", "CAN Bus", "AUTOSAR", "dSPACE",
        ],
    },
    "charging_infrastructure": {
        "technical_skills": 0.40,
        "certifications": 0.25,
        "experience_years": 0.20,
        "soft_skills": 0.15,
        "min_pass_score": 60,
        "key_skills": [
            "EV Charging", "CCS", "CHAdeMO", "OCPP", "ISO 15118",
            "V2G", "Fast Charging", "Grid Integration",
        ],
    },
    "adas_autonomy": {
        "technical_skills": 0.55,
        "experience_years": 0.20,
        "education": 0.15,
        "certifications": 0.10,
        "min_pass_score": 75,
        "key_skills": [
            "ADAS", "Sensor Fusion", "LIDAR", "Radar", "Camera Systems",
            "Path Planning", "Autonomous Driving", "C++", "Python", "ROS",
        ],
    },
    "embedded_software": {
        "technical_skills": 0.50,
        "certifications": 0.20,
        "experience_years": 0.15,
        "education": 0.15,
        "min_pass_score": 70,
        "key_skills": [
            "Embedded C", "AUTOSAR", "CAN Bus", "RTOS", "ISO 26262",
            "ASPICE", "Microcontroller", "STM32", "Firmware",
        ],
    },
    "testing_validation": {
        "certifications": 0.30,
        "technical_skills": 0.30,
        "experience_years": 0.25,
        "soft_skills": 0.15,
        "min_pass_score": 55,
        "key_skills": [
            "HIL Testing", "SIL Testing", "dSPACE", "Vector CANoe",
            "ISO 26262", "ASPICE", "NI LabVIEW", "Test Automation",
        ],
    },
    "general": {
        "technical_skills": 0.40,
        "experience_years": 0.25,
        "education": 0.15,
        "certifications": 0.10,
        "soft_skills": 0.10,
        "min_pass_score": 60,
        "key_skills": [
            "Python", "EV", "Battery", "Motor Control", "Embedded Systems",
            "Arduino", "Raspberry Pi", "CAD", "MATLAB",
        ],
    },
}


def get_role_weights(role_type: str) -> Dict:
    """Return weight profile for a role, defaulting to 'general'."""
    return ROLE_WEIGHTS.get(role_type.lower().replace(" ", "_"), ROLE_WEIGHTS["general"])


def get_role_key_skills(role_type: str) -> list:
    """Return the key skills list for a role."""
    return get_role_weights(role_type).get("key_skills", [])


def apply_role_weights(
    gemini_score: float,
    tfidf_score: float,
    rule_score: float,
    role_type: str,
) -> float:
    """
    Combine the three scorer outputs using role-aware weights.
    Gemini always gets the highest weight; role profile adjusts the blend.
    """
    profile = get_role_weights(role_type)
    tech_w = profile.get("technical_skills", 0.40)

    # Map role technical weight → Gemini weight (0.50–0.70)
    gemini_w = 0.50 + (tech_w - 0.40) * 1.0   # 0.40→0.50, 0.55→0.65
    gemini_w = min(max(gemini_w, 0.50), 0.70)
    tfidf_w  = (1.0 - gemini_w) * 0.75
    rule_w   = (1.0 - gemini_w) * 0.25

    return gemini_score * gemini_w + tfidf_score * tfidf_w + rule_score * rule_w
