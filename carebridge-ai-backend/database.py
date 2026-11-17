"""
CareBridge AI — In-Memory Mock Data Store
No database needed — all data lives in Python dicts/lists.
Replace these with SQLAlchemy / MongoDB calls when ready to go live.
"""

from datetime import datetime, timezone
from models import (
    UserOut, UserRole, Language,
    DoctorOut, AvailableSlot, DoctorReview,
    AppointmentOut, AppointmentStatus,
    PrescriptionOut, PrescriptionStatus, PrescriptionMedicine,
    ConsultationNoteOut, TriageResponse,
)

# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------
_NOW = datetime(2026, 11, 17, tzinfo=timezone.utc)
_FMT = "%Y-%m-%dT%H:%M:%SZ"

def now_str() -> str:
    return datetime.now(timezone.utc).isoformat()


# ---------------------------------------------------------------------------
# USERS
# ---------------------------------------------------------------------------
# Passwords are stored as plain strings here (demo only).
# In production use passlib hash: pwd_context.hash(password)

USERS: dict[str, dict] = {
    "u001": {
        "id": "u001",
        "full_name": "Ahmed Raza",
        "email": "patient@carebridge.ai",
        "phone": "+92-300-1234567",
        "role": UserRole.patient,
        "language": Language.en,
        "avatar_url": "https://api.dicebear.com/7.x/avataaars/svg?seed=Ahmed",
        "password": "demo1234",
        "created_at": _NOW,
    },
    "u002": {
        "id": "u002",
        "full_name": "Dr. Sarah Khan",
        "email": "doctor@carebridge.ai",
        "phone": "+92-321-9876543",
        "role": UserRole.doctor,
        "language": Language.en,
        "avatar_url": "https://api.dicebear.com/7.x/avataaars/svg?seed=Sarah",
        "password": "demo1234",
        "created_at": _NOW,
    },
    "u003": {
        "id": "u003",
        "full_name": "Fatima Malik",
        "email": "fatima@carebridge.ai",
        "phone": "+92-333-5551234",
        "role": UserRole.patient,
        "language": Language.ur,
        "avatar_url": "https://api.dicebear.com/7.x/avataaars/svg?seed=Fatima",
        "password": "demo1234",
        "created_at": _NOW,
    },
}

# ---------------------------------------------------------------------------
# DOCTORS
# ---------------------------------------------------------------------------

DOCTORS: dict[str, dict] = {
    "d001": {
        "id": "d001",
        "full_name": "Dr. Sarah Khan",
        "specialization": "General Physician",
        "bio": "Dr. Sarah Khan is a compassionate general physician with 10 years of experience in primary care and telemedicine.",
        "education": ["MBBS — Aga Khan University", "FCPS — College of Physicians and Surgeons Pakistan"],
        "experience_years": 10,
        "languages": ["English", "Urdu", "Punjabi"],
        "consultation_fee": 1500.0,
        "rating": 4.9,
        "total_reviews": 312,
        "avatar_url": "https://api.dicebear.com/7.x/avataaars/svg?seed=Sarah",
        "is_available": True,
        "next_available": "Today, 3:00 PM",
        "available_slots": [
            {"date": "2026-11-17", "times": ["15:00", "16:00", "17:00"]},
            {"date": "2026-11-18", "times": ["09:00", "10:00", "11:00", "14:00"]},
            {"date": "2026-11-19", "times": ["10:00", "12:00", "15:00"]},
        ],
        "reviews": [
            {"reviewer_name": "Ahmed R.", "rating": 5.0, "comment": "Very thorough and caring doctor!", "date": "2026-11-10"},
            {"reviewer_name": "Zara K.", "rating": 4.9, "comment": "Explained everything clearly. Highly recommend.", "date": "2026-11-05"},
        ],
    },
    "d002": {
        "id": "d002",
        "full_name": "Dr. Bilal Hassan",
        "specialization": "Cardiologist",
        "bio": "Dr. Bilal Hassan specializes in cardiac care with 15 years of expertise in heart disease management and prevention.",
        "education": ["MBBS — King Edward Medical University", "MRCP (UK)", "Fellowship in Cardiology — Mayo Clinic"],
        "experience_years": 15,
        "languages": ["English", "Urdu"],
        "consultation_fee": 3000.0,
        "rating": 4.8,
        "total_reviews": 198,
        "avatar_url": "https://api.dicebear.com/7.x/avataaars/svg?seed=Bilal",
        "is_available": True,
        "next_available": "Tomorrow, 9:00 AM",
        "available_slots": [
            {"date": "2026-11-18", "times": ["09:00", "11:00"]},
            {"date": "2026-11-20", "times": ["14:00", "15:00"]},
        ],
        "reviews": [
            {"reviewer_name": "Omar S.", "rating": 5.0, "comment": "Saved my life. Brilliant cardiologist.", "date": "2026-11-01"},
        ],
    },
    "d003": {
        "id": "d003",
        "full_name": "Dr. Nadia Hussain",
        "specialization": "Dermatologist",
        "bio": "Dr. Nadia Hussain is a certified dermatologist with expertise in skin disorders, cosmetic dermatology, and trichology.",
        "education": ["MBBS — Dow University of Health Sciences", "FCPS Dermatology"],
        "experience_years": 8,
        "languages": ["English", "Urdu", "Sindhi"],
        "consultation_fee": 2000.0,
        "rating": 4.7,
        "total_reviews": 156,
        "avatar_url": "https://api.dicebear.com/7.x/avataaars/svg?seed=Nadia",
        "is_available": True,
        "next_available": "Today, 5:00 PM",
        "available_slots": [
            {"date": "2026-11-17", "times": ["17:00", "18:00"]},
            {"date": "2026-11-19", "times": ["09:00", "10:00", "11:00"]},
        ],
        "reviews": [],
    },
    "d004": {
        "id": "d004",
        "full_name": "Dr. Tariq Mehmood",
        "specialization": "Pediatrician",
        "bio": "Dr. Tariq Mehmood is a dedicated pediatrician with 12 years of experience caring for newborns, children, and adolescents.",
        "education": ["MBBS — Allama Iqbal Medical College", "FCPS Pediatrics"],
        "experience_years": 12,
        "languages": ["English", "Urdu", "Punjabi"],
        "consultation_fee": 1800.0,
        "rating": 4.9,
        "total_reviews": 405,
        "avatar_url": "https://api.dicebear.com/7.x/avataaars/svg?seed=Tariq",
        "is_available": False,
        "next_available": "Nov 20, 2026",
        "available_slots": [
            {"date": "2026-11-20", "times": ["10:00", "11:00", "14:00", "15:00"]},
        ],
        "reviews": [],
    },
    "d005": {
        "id": "d005",
        "full_name": "Dr. Amina Siddiqui",
        "specialization": "Mental Health",
        "bio": "Dr. Amina Siddiqui is a licensed psychiatrist and psychotherapist specializing in anxiety, depression, and trauma-informed care.",
        "education": ["MBBS — University of Health Sciences", "FCPS Psychiatry", "CBT Certification — Beck Institute"],
        "experience_years": 9,
        "languages": ["English", "Urdu"],
        "consultation_fee": 2500.0,
        "rating": 5.0,
        "total_reviews": 89,
        "avatar_url": "https://api.dicebear.com/7.x/avataaars/svg?seed=Amina",
        "is_available": True,
        "next_available": "Today, 7:00 PM",
        "available_slots": [
            {"date": "2026-11-17", "times": ["19:00", "20:00"]},
            {"date": "2026-11-18", "times": ["18:00", "19:00"]},
        ],
        "reviews": [],
    },
}

# ---------------------------------------------------------------------------
# APPOINTMENTS
# ---------------------------------------------------------------------------

APPOINTMENTS: dict[str, dict] = {
    "a001": {
        "id": "a001",
        "patient_id": "u001",
        "doctor_id": "d001",
        "date": "2026-11-18",
        "time": "10:00",
        "chief_complaint": "Persistent headache and mild fever for 3 days",
        "status": AppointmentStatus.upcoming,
        "doctor_name": "Dr. Sarah Khan",
        "doctor_specialization": "General Physician",
        "patient_name": "Ahmed Raza",
        "created_at": _NOW,
        "video_room_id": "room-a001",
    },
    "a002": {
        "id": "a002",
        "patient_id": "u001",
        "doctor_id": "d002",
        "date": "2026-11-10",
        "time": "14:00",
        "chief_complaint": "Chest discomfort after exercise",
        "status": AppointmentStatus.completed,
        "doctor_name": "Dr. Bilal Hassan",
        "doctor_specialization": "Cardiologist",
        "patient_name": "Ahmed Raza",
        "created_at": _NOW,
        "video_room_id": "room-a002",
    },
    "a003": {
        "id": "a003",
        "patient_id": "u003",
        "doctor_id": "d005",
        "date": "2026-11-19",
        "time": "19:00",
        "chief_complaint": "Anxiety and sleep issues",
        "status": AppointmentStatus.upcoming,
        "doctor_name": "Dr. Amina Siddiqui",
        "doctor_specialization": "Mental Health",
        "patient_name": "Fatima Malik",
        "created_at": _NOW,
        "video_room_id": "room-a003",
    },
}

# ---------------------------------------------------------------------------
# PRESCRIPTIONS
# ---------------------------------------------------------------------------

PRESCRIPTIONS: dict[str, dict] = {
    "rx001": {
        "id": "rx001",
        "patient_id": "u001",
        "doctor_id": "d002",
        "appointment_id": "a002",
        "medicines": [
            {"name": "Aspirin", "dosage": "75 mg", "frequency": "Once daily", "duration": "30 days", "instructions": "Take after food"},
            {"name": "Atorvastatin", "dosage": "20 mg", "frequency": "Once at night", "duration": "30 days", "instructions": "Avoid grapefruit juice"},
        ],
        "doctor_notes": "Patient advised to reduce salt intake and exercise moderately. Follow up in 4 weeks.",
        "follow_up_date": "2026-12-10",
        "status": PrescriptionStatus.approved,
        "issued_at": _NOW,
        "approved_at": _NOW,
        "doctor_name": "Dr. Bilal Hassan",
        "patient_name": "Ahmed Raza",
    },
}

# ---------------------------------------------------------------------------
# AI TRIAGE SUMMARIES
# ---------------------------------------------------------------------------

TRIAGE_SUMMARIES: dict[str, dict] = {}

# ---------------------------------------------------------------------------
# CONSULTATION NOTES
# ---------------------------------------------------------------------------

CONSULTATION_NOTES: dict[str, dict] = {}

# ---------------------------------------------------------------------------
# CHAT MESSAGES
# ---------------------------------------------------------------------------

CHAT_MESSAGES: dict[str, list] = {}   # keyed by appointment_id

# ---------------------------------------------------------------------------
# ID Counters (simple auto-increment)
# ---------------------------------------------------------------------------
_counters: dict[str, int] = {
    "user": 10,
    "appointment": 10,
    "prescription": 10,
    "triage": 10,
    "note": 10,
    "chat": 10,
}

def next_id(entity: str) -> str:
    _counters[entity] += 1
    prefixes = {
        "user": "u",
        "appointment": "a",
        "prescription": "rx",
        "triage": "tr",
        "note": "cn",
        "chat": "cm",
    }
    return f"{prefixes[entity]}{_counters[entity]:03d}"
