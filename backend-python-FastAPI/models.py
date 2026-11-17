"""
CareBridge AI — Pydantic Data Models
Mirrors the TypeScript types from the frontend.
"""

from __future__ import annotations
from datetime import datetime
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class UserRole(str, Enum):
    patient = "patient"
    doctor = "doctor"
    admin = "admin"

class AppointmentStatus(str, Enum):
    upcoming = "upcoming"
    in_progress = "in_progress"
    completed = "completed"
    cancelled = "cancelled"

class PrescriptionStatus(str, Enum):
    pending = "pending"
    approved = "approved"
    shared = "shared"

class Severity(str, Enum):
    low = "low"
    moderate = "moderate"
    high = "high"
    critical = "critical"

class Language(str, Enum):
    en = "en"
    ur = "ur"
    roman_ur = "roman_ur"


# ---------------------------------------------------------------------------
# User / Auth Models
# ---------------------------------------------------------------------------

class UserBase(BaseModel):
    full_name: str
    email: EmailStr
    phone: Optional[str] = None
    role: UserRole = UserRole.patient
    language: Language = Language.en
    avatar_url: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserOut(UserBase):
    id: str
    created_at: datetime

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


# ---------------------------------------------------------------------------
# Doctor Models
# ---------------------------------------------------------------------------

class AvailableSlot(BaseModel):
    date: str          # "YYYY-MM-DD"
    times: List[str]   # ["09:00", "10:00", ...]

class DoctorReview(BaseModel):
    reviewer_name: str
    rating: float
    comment: str
    date: str

class DoctorBase(BaseModel):
    full_name: str
    specialization: str
    bio: str
    education: List[str]
    experience_years: int
    languages: List[str]
    consultation_fee: float
    rating: float = Field(ge=0, le=5)
    total_reviews: int = 0
    avatar_url: Optional[str] = None
    is_available: bool = True
    next_available: Optional[str] = None

class DoctorOut(DoctorBase):
    id: str
    available_slots: List[AvailableSlot] = []
    reviews: List[DoctorReview] = []


# ---------------------------------------------------------------------------
# Appointment Models
# ---------------------------------------------------------------------------

class AppointmentCreate(BaseModel):
    patient_id: str
    doctor_id: str
    date: str          # "YYYY-MM-DD"
    time: str          # "HH:MM"
    chief_complaint: Optional[str] = None

class AppointmentOut(AppointmentCreate):
    id: str
    status: AppointmentStatus = AppointmentStatus.upcoming
    doctor_name: str
    doctor_specialization: str
    patient_name: str
    created_at: datetime
    video_room_id: Optional[str] = None


# ---------------------------------------------------------------------------
# AI / Triage Models
# ---------------------------------------------------------------------------

class TriageRequest(BaseModel):
    patient_id: str
    age_range: str                   # e.g. "25-34"
    main_symptom: str
    duration: str                    # e.g. "3 days"
    severity: int = Field(ge=1, le=10)
    existing_conditions: List[str] = []
    current_medications: List[str] = []
    allergies: List[str] = []
    additional_notes: Optional[str] = None
    language: Language = Language.en

class RedFlagAlert(BaseModel):
    is_red_flag: bool
    matched_keywords: List[str] = []
    emergency_message: str = ""

class DoctorReadySummary(BaseModel):
    main_concern: str
    symptoms: List[str]
    duration: str
    severity_label: Severity
    severity_score: int
    relevant_history: str
    suggested_specialty: str
    questions_to_ask: List[str]

class TriageResponse(BaseModel):
    patient_id: str
    summary_id: str
    red_flag: RedFlagAlert
    doctor_ready_summary: DoctorReadySummary
    language: Language
    generated_at: datetime


# ---------------------------------------------------------------------------
# Prescription Models
# ---------------------------------------------------------------------------

class PrescriptionMedicine(BaseModel):
    name: str
    dosage: str         # e.g. "500 mg"
    frequency: str      # e.g. "Twice daily"
    duration: str       # e.g. "7 days"
    instructions: Optional[str] = None

class PrescriptionCreate(BaseModel):
    patient_id: str
    doctor_id: str
    appointment_id: str
    medicines: List[PrescriptionMedicine]
    doctor_notes: Optional[str] = None
    follow_up_date: Optional[str] = None

class PrescriptionOut(PrescriptionCreate):
    id: str
    status: PrescriptionStatus = PrescriptionStatus.pending
    issued_at: Optional[datetime] = None
    approved_at: Optional[datetime] = None
    doctor_name: str
    patient_name: str


# ---------------------------------------------------------------------------
# Consultation Chat
# ---------------------------------------------------------------------------

class ChatMessageCreate(BaseModel):
    appointment_id: str
    sender_id: str
    sender_role: UserRole
    content: str

class ChatMessageOut(ChatMessageCreate):
    id: str
    timestamp: datetime


# ---------------------------------------------------------------------------
# Consultation Notes
# ---------------------------------------------------------------------------

class ConsultationNoteCreate(BaseModel):
    appointment_id: str
    doctor_id: str
    patient_id: str
    subjective: str    # What the patient reported
    objective: str     # Doctor's findings
    assessment: str    # Diagnosis / impression
    plan: str          # Treatment plan
    is_approved: bool = False

class ConsultationNoteOut(ConsultationNoteCreate):
    id: str
    created_at: datetime
    approved_at: Optional[datetime] = None
