"""
CareBridge AI — AI Triage Engine
Handles red-flag detection and Doctor-Ready Summary generation.
No real LLM is used — logic is rule-based for demo purposes.
Plug in Gemini / GPT-4 by replacing `generate_summary()`.
"""

from __future__ import annotations
from datetime import datetime, timezone
from typing import List

from models import (
    TriageRequest, TriageResponse, RedFlagAlert,
    DoctorReadySummary, Severity, Language,
)
from database import TRIAGE_SUMMARIES, next_id

# ---------------------------------------------------------------------------
# Red-flag keyword bank (English + common Urdu transliterations)
# ---------------------------------------------------------------------------

RED_FLAG_KEYWORDS: List[str] = [
    # Cardiac
    "chest pain", "chest pressure", "chest tightness", "heart attack",
    "dil mein dard", "seene mein dard",
    # Breathing
    "difficulty breathing", "can't breathe", "shortness of breath",
    "saans nahi aa raha", "sans rok",
    # Stroke
    "stroke", "facial drooping", "arm weakness", "sudden confusion",
    "sudden headache", "loss of vision", "slurred speech",
    "chehra tedha", "haath kamzor",
    # Unconsciousness
    "unconscious", "fainted", "not responding", "behosh",
    # Bleeding
    "heavy bleeding", "uncontrolled bleeding", "khoon nahi ruk raha",
    "bleeding profusely",
    # Suicidal / Mental crisis
    "suicidal", "want to die", "end my life", "marna chahta",
    "marna chahti", "khud kushi",
    # Allergic shock
    "anaphylaxis", "severe allergic", "throat swelling", "gala band",
    # Seizure
    "seizure", "fit", "convulsion", "mirgi",
    # Severe infection
    "high fever", "stiff neck", "rash with fever", "meningitis",
]

SPECIALTY_MAP: dict[str, str] = {
    "headache": "General Physician / Neurologist",
    "fever": "General Physician",
    "cough": "General Physician / Pulmonologist",
    "chest": "Cardiologist",
    "heart": "Cardiologist",
    "skin": "Dermatologist",
    "rash": "Dermatologist",
    "acne": "Dermatologist",
    "child": "Pediatrician",
    "baby": "Pediatrician",
    "depression": "Psychiatrist",
    "anxiety": "Psychiatrist",
    "mental": "Psychiatrist",
    "stress": "Psychiatrist",
    "joint": "Orthopedic Specialist",
    "bone": "Orthopedic Specialist",
    "stomach": "Gastroenterologist",
    "digestion": "Gastroenterologist",
    "eye": "Ophthalmologist",
    "vision": "Ophthalmologist",
    "ear": "ENT Specialist",
    "throat": "ENT Specialist",
    "kidney": "Nephrologist",
    "urine": "Urologist / Nephrologist",
    "diabetes": "Endocrinologist",
    "thyroid": "Endocrinologist",
}

SEVERITY_LABELS = {
    range(1, 4): Severity.low,
    range(4, 7): Severity.moderate,
    range(7, 9): Severity.high,
    range(9, 11): Severity.critical,
}

DOCTOR_QUESTIONS: dict[str, list[str]] = {
    "General Physician": [
        "What tests do you recommend based on my symptoms?",
        "Should I be concerned about any serious underlying condition?",
        "What lifestyle changes would help?",
        "When should I return if symptoms persist?",
    ],
    "Cardiologist": [
        "Do I need an ECG or echo?",
        "Are my symptoms cardiac in origin?",
        "What cardiac risk factors should I address?",
        "Should I monitor my blood pressure at home?",
    ],
    "Dermatologist": [
        "Is this contagious?",
        "Should I avoid any foods or products?",
        "Will this resolve on its own or needs treatment?",
        "Do I need a biopsy?",
    ],
    "Psychiatrist": [
        "What therapy approach would you recommend?",
        "Will I need long-term medication?",
        "How do I manage acute anxiety episodes?",
        "Are there any support groups you recommend?",
    ],
}

DEFAULT_QUESTIONS = [
    "What is causing my symptoms?",
    "What investigations should I get done?",
    "What is the expected recovery time?",
    "Are there any warning signs I should watch for?",
    "What medications or treatments do you recommend?",
]

EMERGENCY_MESSAGES = {
    Language.en: (
        "⚠️ EMERGENCY: Your symptoms may require IMMEDIATE medical attention. "
        "Please call 1122 (Pakistan), 115 (Rescue), or go to your nearest Emergency Room NOW. "
        "Do NOT wait for a telemedicine consultation."
    ),
    Language.ur: (
        "⚠️ ایمرجنسی: آپ کی علامات فوری طبی توجہ کی ضرورت ہو سکتی ہیں۔ "
        "فوری طور پر 1122 یا 115 پر کال کریں یا قریبی ایمرجنسی روم جائیں۔"
    ),
    Language.roman_ur: (
        "⚠️ Emergency: Aap ki alamaat ko FORI tibbi imdaad ki zaroorat hai. "
        "Abhi 1122 ya 115 par call karein ya qareeb emergency room jayein."
    ),
}

# ---------------------------------------------------------------------------
# Core logic
# ---------------------------------------------------------------------------

def detect_red_flags(text: str) -> tuple[bool, List[str]]:
    """Return (is_red_flag, matched_keywords)."""
    lower = text.lower()
    matched = [kw for kw in RED_FLAG_KEYWORDS if kw in lower]
    return bool(matched), matched


def guess_specialty(symptom: str, existing: List[str]) -> str:
    combined = (symptom + " " + " ".join(existing)).lower()
    for keyword, spec in SPECIALTY_MAP.items():
        if keyword in combined:
            return spec
    return "General Physician"


def severity_label(score: int) -> Severity:
    for r, label in SEVERITY_LABELS.items():
        if score in r:
            return label
    return Severity.moderate


def build_summary_text(req: TriageRequest) -> DoctorReadySummary:
    spec = guess_specialty(req.main_symptom, req.existing_conditions)
    sev_label = severity_label(req.severity)

    history_parts = []
    if req.existing_conditions:
        history_parts.append("Existing conditions: " + ", ".join(req.existing_conditions))
    if req.current_medications:
        history_parts.append("Current medications: " + ", ".join(req.current_medications))
    if req.allergies:
        history_parts.append("Allergies: " + ", ".join(req.allergies))
    history_text = ". ".join(history_parts) if history_parts else "No significant past history reported."

    questions = DOCTOR_QUESTIONS.get(spec.split(" / ")[0], DEFAULT_QUESTIONS)

    return DoctorReadySummary(
        main_concern=req.main_symptom,
        symptoms=[req.main_symptom] + (req.existing_conditions or []),
        duration=req.duration,
        severity_label=sev_label,
        severity_score=req.severity,
        relevant_history=history_text,
        suggested_specialty=spec,
        questions_to_ask=questions,
    )


def run_triage(req: TriageRequest) -> TriageResponse:
    """Entry point called by the API route."""
    # Combine all text for red-flag scan
    combined_text = " ".join([
        req.main_symptom,
        req.additional_notes or "",
        " ".join(req.existing_conditions),
    ])
    is_rf, matched = detect_red_flags(combined_text)

    red_flag = RedFlagAlert(
        is_red_flag=is_rf,
        matched_keywords=matched,
        emergency_message=EMERGENCY_MESSAGES.get(req.language, EMERGENCY_MESSAGES[Language.en]) if is_rf else "",
    )

    summary = build_summary_text(req)
    summary_id = next_id("triage")
    now = datetime.now(timezone.utc)

    result = {
        "patient_id": req.patient_id,
        "summary_id": summary_id,
        "red_flag": red_flag.model_dump(),
        "doctor_ready_summary": summary.model_dump(),
        "language": req.language,
        "generated_at": now,
    }
    TRIAGE_SUMMARIES[summary_id] = result

    return TriageResponse(**result)
