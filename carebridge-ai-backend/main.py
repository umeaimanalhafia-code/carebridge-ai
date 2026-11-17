"""
CareBridge AI — FastAPI Application (main.py)
==============================================
Run with:
    uvicorn main:app --reload --port 8000

Swagger UI available at:
    http://localhost:8000/docs

DISCLAIMER: This is a demo backend. Do NOT use with real patient data.
            No real authentication or database is included.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Local modules
import database as db
from models import (
    # Auth
    UserCreate, UserLogin, UserOut, TokenResponse, UserRole,
    # Doctor
    DoctorOut,
    # Appointment
    AppointmentCreate, AppointmentOut, AppointmentStatus,
    # Prescription
    PrescriptionCreate, PrescriptionOut, PrescriptionStatus,
    # AI
    TriageRequest, TriageResponse,
    # Notes
    ConsultationNoteCreate, ConsultationNoteOut,
    # Chat
    ChatMessageCreate, ChatMessageOut,
)
from triage import run_triage

# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------

app = FastAPI(
    title="CareBridge AI — Backend API",
    description=(
        "REST API for the CareBridge AI telemedicine platform. "
        "Provides doctor discovery, appointment booking, AI triage, "
        "prescription management, and consultation notes.\n\n"
        "**⚠️ Medical Disclaimer:** CareBridge AI does not diagnose or replace "
        "a qualified doctor. For emergencies, contact local emergency services immediately."
    ),
    version="1.0.0",
    contact={"name": "CareBridge AI Team", "email": "support@carebridge.ai"},
    license_info={"name": "MIT"},
)

# ---------------------------------------------------------------------------
# CORS — allow the Next.js frontend on port 3000
# ---------------------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5500",   # VS Code Live Server
        "http://127.0.0.1:5500",
        "*",  # Remove in production!
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _now() -> datetime:
    return datetime.now(timezone.utc)

def _user_out(u: dict) -> UserOut:
    return UserOut(**{k: v for k, v in u.items() if k != "password"})

def _404(entity: str, eid: str):
    raise HTTPException(status_code=404, detail=f"{entity} '{eid}' not found.")


# ===========================================================================
# HEALTH CHECK
# ===========================================================================

@app.get("/", tags=["Health"])
async def root():
    return {
        "status": "ok",
        "service": "CareBridge AI Backend",
        "version": "1.0.0",
        "disclaimer": (
            "CareBridge AI does not diagnose or replace a qualified doctor. "
            "For emergencies, contact local emergency services immediately."
        ),
        "docs": "/docs",
    }

@app.get("/health", tags=["Health"])
async def health():
    return {"status": "healthy", "timestamp": _now()}


# ===========================================================================
# AUTH
# ===========================================================================

@app.post("/api/auth/login", response_model=TokenResponse, tags=["Auth"])
async def login(payload: UserLogin):
    """
    Mock login endpoint.
    Demo credentials:
      Patient — patient@carebridge.ai / demo1234
      Doctor  — doctor@carebridge.ai  / demo1234
    """
    user = next(
        (u for u in db.USERS.values() if u["email"] == payload.email),
        None,
    )
    if not user or user["password"] != payload.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )
    # In production: return a signed JWT token here
    mock_token = f"mock-jwt-token-{user['id']}-{uuid.uuid4().hex[:8]}"
    return TokenResponse(access_token=mock_token, user=_user_out(user))


@app.post("/api/auth/register", response_model=UserOut, status_code=201, tags=["Auth"])
async def register(payload: UserCreate):
    """Register a new patient account (mock)."""
    if any(u["email"] == payload.email for u in db.USERS.values()):
        raise HTTPException(status_code=409, detail="Email already registered.")
    uid = db.next_id("user")
    new_user = {
        **payload.model_dump(),
        "id": uid,
        "avatar_url": f"https://api.dicebear.com/7.x/avataaars/svg?seed={uid}",
        "created_at": _now(),
    }
    db.USERS[uid] = new_user
    return _user_out(new_user)


# ===========================================================================
# USERS
# ===========================================================================

@app.get("/api/users/{user_id}", response_model=UserOut, tags=["Users"])
async def get_user(user_id: str):
    """Get a user's public profile."""
    if user_id not in db.USERS:
        _404("User", user_id)
    return _user_out(db.USERS[user_id])


@app.get("/api/users", response_model=List[UserOut], tags=["Users"])
async def list_users(role: Optional[UserRole] = None):
    """List all users, optionally filtered by role."""
    users = db.USERS.values()
    if role:
        users = [u for u in users if u["role"] == role]
    return [_user_out(u) for u in users]


# ===========================================================================
# DOCTORS
# ===========================================================================

@app.get("/api/doctors", response_model=List[DoctorOut], tags=["Doctors"])
async def list_doctors(
    specialization: Optional[str] = Query(None, description="Filter by specialization"),
    language: Optional[str] = Query(None, description="Filter by language"),
    available: Optional[bool] = Query(None, description="Filter by availability"),
    min_rating: Optional[float] = Query(None, ge=0, le=5, description="Minimum rating"),
    max_fee: Optional[float] = Query(None, description="Maximum consultation fee"),
):
    """
    Return a list of doctors with optional filters.
    All filters are case-insensitive substring matches.
    """
    docs = list(db.DOCTORS.values())

    if specialization:
        docs = [d for d in docs if specialization.lower() in d["specialization"].lower()]
    if language:
        docs = [d for d in docs if any(language.lower() in lang.lower() for lang in d["languages"])]
    if available is not None:
        docs = [d for d in docs if d["is_available"] == available]
    if min_rating is not None:
        docs = [d for d in docs if d["rating"] >= min_rating]
    if max_fee is not None:
        docs = [d for d in docs if d["consultation_fee"] <= max_fee]

    return [DoctorOut(**d) for d in docs]


@app.get("/api/doctors/{doctor_id}", response_model=DoctorOut, tags=["Doctors"])
async def get_doctor(doctor_id: str):
    """Get a single doctor's full profile including slots and reviews."""
    if doctor_id not in db.DOCTORS:
        _404("Doctor", doctor_id)
    return DoctorOut(**db.DOCTORS[doctor_id])


# ===========================================================================
# APPOINTMENTS
# ===========================================================================

@app.get("/api/appointments", response_model=List[AppointmentOut], tags=["Appointments"])
async def list_appointments(
    patient_id: Optional[str] = None,
    doctor_id: Optional[str] = None,
    appointment_status: Optional[AppointmentStatus] = Query(None, alias="status"),
):
    """
    List appointments.
    Filter by patient_id, doctor_id, or status.
    """
    appts = list(db.APPOINTMENTS.values())
    if patient_id:
        appts = [a for a in appts if a["patient_id"] == patient_id]
    if doctor_id:
        appts = [a for a in appts if a["doctor_id"] == doctor_id]
    if appointment_status:
        appts = [a for a in appts if a["status"] == appointment_status]
    return [AppointmentOut(**a) for a in appts]


@app.post("/api/appointments", response_model=AppointmentOut, status_code=201, tags=["Appointments"])
async def book_appointment(payload: AppointmentCreate):
    """Book a new appointment."""
    # Validate patient and doctor exist
    if payload.patient_id not in db.USERS:
        _404("Patient", payload.patient_id)
    if payload.doctor_id not in db.DOCTORS:
        _404("Doctor", payload.doctor_id)

    doctor = db.DOCTORS[payload.doctor_id]
    patient = db.USERS[payload.patient_id]

    aid = db.next_id("appointment")
    new_appt = {
        **payload.model_dump(),
        "id": aid,
        "status": AppointmentStatus.upcoming,
        "doctor_name": doctor["full_name"],
        "doctor_specialization": doctor["specialization"],
        "patient_name": patient["full_name"],
        "created_at": _now(),
        "video_room_id": f"room-{aid}",
    }
    db.APPOINTMENTS[aid] = new_appt
    return AppointmentOut(**new_appt)


@app.get("/api/appointments/{appointment_id}", response_model=AppointmentOut, tags=["Appointments"])
async def get_appointment(appointment_id: str):
    if appointment_id not in db.APPOINTMENTS:
        _404("Appointment", appointment_id)
    return AppointmentOut(**db.APPOINTMENTS[appointment_id])


@app.patch("/api/appointments/{appointment_id}/cancel", response_model=AppointmentOut, tags=["Appointments"])
async def cancel_appointment(appointment_id: str):
    """Cancel an upcoming appointment."""
    if appointment_id not in db.APPOINTMENTS:
        _404("Appointment", appointment_id)
    appt = db.APPOINTMENTS[appointment_id]
    if appt["status"] not in (AppointmentStatus.upcoming, AppointmentStatus.in_progress):
        raise HTTPException(400, detail="Only upcoming or in-progress appointments can be cancelled.")
    appt["status"] = AppointmentStatus.cancelled
    return AppointmentOut(**appt)


@app.patch("/api/appointments/{appointment_id}/start", response_model=AppointmentOut, tags=["Appointments"])
async def start_appointment(appointment_id: str):
    """Mark appointment as in-progress (doctor joins the call)."""
    if appointment_id not in db.APPOINTMENTS:
        _404("Appointment", appointment_id)
    appt = db.APPOINTMENTS[appointment_id]
    appt["status"] = AppointmentStatus.in_progress
    return AppointmentOut(**appt)


@app.patch("/api/appointments/{appointment_id}/complete", response_model=AppointmentOut, tags=["Appointments"])
async def complete_appointment(appointment_id: str):
    """Mark appointment as completed (end of video call)."""
    if appointment_id not in db.APPOINTMENTS:
        _404("Appointment", appointment_id)
    appt = db.APPOINTMENTS[appointment_id]
    appt["status"] = AppointmentStatus.completed
    return AppointmentOut(**appt)


# ===========================================================================
# AI TRIAGE
# ===========================================================================

@app.post("/api/ai/triage", response_model=TriageResponse, tags=["AI Triage"])
async def ai_triage(payload: TriageRequest):
    """
    Run AI triage on patient symptom data.
    
    Returns:
    - Red-flag detection result with emergency message if triggered
    - Doctor-Ready Summary with suggested specialty and questions
    
    ⚠️ This AI does NOT diagnose or prescribe treatment.
    """
    result = run_triage(payload)
    return result


@app.get("/api/ai/summary/{patient_id}", response_model=List[TriageResponse], tags=["AI Triage"])
async def get_patient_summaries(patient_id: str):
    """Get all AI triage summaries for a patient."""
    summaries = [
        TriageResponse(**s)
        for s in db.TRIAGE_SUMMARIES.values()
        if s["patient_id"] == patient_id
    ]
    return summaries


@app.get("/api/ai/summary/detail/{summary_id}", response_model=TriageResponse, tags=["AI Triage"])
async def get_summary_detail(summary_id: str):
    """Get a single AI triage summary by ID."""
    if summary_id not in db.TRIAGE_SUMMARIES:
        _404("Triage Summary", summary_id)
    return TriageResponse(**db.TRIAGE_SUMMARIES[summary_id])


# ===========================================================================
# PRESCRIPTIONS
# ===========================================================================

@app.get("/api/prescriptions", response_model=List[PrescriptionOut], tags=["Prescriptions"])
async def list_prescriptions(
    patient_id: Optional[str] = None,
    doctor_id: Optional[str] = None,
    prescription_status: Optional[PrescriptionStatus] = Query(None, alias="status"),
):
    """List prescriptions with optional filters."""
    rxs = list(db.PRESCRIPTIONS.values())
    if patient_id:
        rxs = [r for r in rxs if r["patient_id"] == patient_id]
    if doctor_id:
        rxs = [r for r in rxs if r["doctor_id"] == doctor_id]
    if prescription_status:
        rxs = [r for r in rxs if r["status"] == prescription_status]
    return [PrescriptionOut(**r) for r in rxs]


@app.post("/api/prescriptions", response_model=PrescriptionOut, status_code=201, tags=["Prescriptions"])
async def create_prescription(payload: PrescriptionCreate):
    """
    Doctor creates a prescription draft (status = pending).
    Must be explicitly approved via the /approve endpoint.
    """
    if payload.patient_id not in db.USERS:
        _404("Patient", payload.patient_id)
    if payload.doctor_id not in db.DOCTORS:
        _404("Doctor", payload.doctor_id)
    if payload.appointment_id not in db.APPOINTMENTS:
        _404("Appointment", payload.appointment_id)

    doctor = db.DOCTORS[payload.doctor_id]
    patient = db.USERS[payload.patient_id]
    rxid = db.next_id("prescription")

    new_rx = {
        **payload.model_dump(),
        "id": rxid,
        "status": PrescriptionStatus.pending,
        "issued_at": _now(),
        "approved_at": None,
        "doctor_name": doctor["full_name"],
        "patient_name": patient["full_name"],
    }
    db.PRESCRIPTIONS[rxid] = new_rx
    return PrescriptionOut(**new_rx)


@app.get("/api/prescriptions/{prescription_id}", response_model=PrescriptionOut, tags=["Prescriptions"])
async def get_prescription(prescription_id: str):
    if prescription_id not in db.PRESCRIPTIONS:
        _404("Prescription", prescription_id)
    return PrescriptionOut(**db.PRESCRIPTIONS[prescription_id])


@app.patch("/api/prescriptions/{prescription_id}/approve", response_model=PrescriptionOut, tags=["Prescriptions"])
async def approve_prescription(prescription_id: str):
    """
    Doctor explicitly approves the prescription.
    Only after approval is it visible to the patient.
    """
    if prescription_id not in db.PRESCRIPTIONS:
        _404("Prescription", prescription_id)
    rx = db.PRESCRIPTIONS[prescription_id]
    if rx["status"] == PrescriptionStatus.approved:
        raise HTTPException(400, detail="Prescription already approved.")
    rx["status"] = PrescriptionStatus.approved
    rx["approved_at"] = _now()
    return PrescriptionOut(**rx)


@app.patch("/api/prescriptions/{prescription_id}/share", response_model=PrescriptionOut, tags=["Prescriptions"])
async def share_prescription(prescription_id: str):
    """Mark prescription as shared with the patient."""
    if prescription_id not in db.PRESCRIPTIONS:
        _404("Prescription", prescription_id)
    rx = db.PRESCRIPTIONS[prescription_id]
    if rx["status"] != PrescriptionStatus.approved:
        raise HTTPException(400, detail="Only approved prescriptions can be shared.")
    rx["status"] = PrescriptionStatus.shared
    return PrescriptionOut(**rx)


# ===========================================================================
# CONSULTATION NOTES
# ===========================================================================

@app.post("/api/notes", response_model=ConsultationNoteOut, status_code=201, tags=["Consultation Notes"])
async def create_note(payload: ConsultationNoteCreate):
    """Doctor creates a SOAP consultation note."""
    if payload.appointment_id not in db.APPOINTMENTS:
        _404("Appointment", payload.appointment_id)
    nid = db.next_id("note")
    note = {
        **payload.model_dump(),
        "id": nid,
        "created_at": _now(),
        "approved_at": None,
    }
    db.CONSULTATION_NOTES[nid] = note
    return ConsultationNoteOut(**note)


@app.get("/api/notes", response_model=List[ConsultationNoteOut], tags=["Consultation Notes"])
async def list_notes(
    appointment_id: Optional[str] = None,
    patient_id: Optional[str] = None,
    doctor_id: Optional[str] = None,
):
    notes = list(db.CONSULTATION_NOTES.values())
    if appointment_id:
        notes = [n for n in notes if n["appointment_id"] == appointment_id]
    if patient_id:
        notes = [n for n in notes if n["patient_id"] == patient_id]
    if doctor_id:
        notes = [n for n in notes if n["doctor_id"] == doctor_id]
    return [ConsultationNoteOut(**n) for n in notes]


@app.patch("/api/notes/{note_id}/approve", response_model=ConsultationNoteOut, tags=["Consultation Notes"])
async def approve_note(note_id: str):
    """Doctor approves the consultation note — makes it visible to patient."""
    if note_id not in db.CONSULTATION_NOTES:
        _404("Consultation Note", note_id)
    note = db.CONSULTATION_NOTES[note_id]
    note["is_approved"] = True
    note["approved_at"] = _now()
    return ConsultationNoteOut(**note)


# ===========================================================================
# CONSULTATION CHAT
# ===========================================================================

@app.post("/api/chat", response_model=ChatMessageOut, status_code=201, tags=["Chat"])
async def send_chat_message(payload: ChatMessageCreate):
    """Send a message in a consultation's chat room."""
    if payload.appointment_id not in db.APPOINTMENTS:
        _404("Appointment", payload.appointment_id)
    mid = db.next_id("chat")
    msg = {
        **payload.model_dump(),
        "id": mid,
        "timestamp": _now(),
    }
    if payload.appointment_id not in db.CHAT_MESSAGES:
        db.CHAT_MESSAGES[payload.appointment_id] = []
    db.CHAT_MESSAGES[payload.appointment_id].append(msg)
    return ChatMessageOut(**msg)


@app.get("/api/chat/{appointment_id}", response_model=List[ChatMessageOut], tags=["Chat"])
async def get_chat(appointment_id: str):
    """Get all chat messages for an appointment."""
    if appointment_id not in db.APPOINTMENTS:
        _404("Appointment", appointment_id)
    msgs = db.CHAT_MESSAGES.get(appointment_id, [])
    return [ChatMessageOut(**m) for m in msgs]


# ===========================================================================
# STATISTICS (Doctor Dashboard)
# ===========================================================================

@app.get("/api/stats/doctor/{doctor_id}", tags=["Statistics"])
async def doctor_stats(doctor_id: str):
    """Return appointment statistics for a doctor's dashboard."""
    if doctor_id not in db.DOCTORS:
        _404("Doctor", doctor_id)
    appts = [a for a in db.APPOINTMENTS.values() if a["doctor_id"] == doctor_id]
    return {
        "doctor_id": doctor_id,
        "total_appointments": len(appts),
        "upcoming": sum(1 for a in appts if a["status"] == AppointmentStatus.upcoming),
        "in_progress": sum(1 for a in appts if a["status"] == AppointmentStatus.in_progress),
        "completed": sum(1 for a in appts if a["status"] == AppointmentStatus.completed),
        "cancelled": sum(1 for a in appts if a["status"] == AppointmentStatus.cancelled),
        "total_prescriptions": sum(1 for r in db.PRESCRIPTIONS.values() if r["doctor_id"] == doctor_id),
        "pending_prescriptions": sum(
            1 for r in db.PRESCRIPTIONS.values()
            if r["doctor_id"] == doctor_id and r["status"] == PrescriptionStatus.pending
        ),
    }


@app.get("/api/stats/patient/{patient_id}", tags=["Statistics"])
async def patient_stats(patient_id: str):
    """Return health statistics for a patient's dashboard."""
    if patient_id not in db.USERS:
        _404("Patient", patient_id)
    appts = [a for a in db.APPOINTMENTS.values() if a["patient_id"] == patient_id]
    rxs = [r for r in db.PRESCRIPTIONS.values() if r["patient_id"] == patient_id]
    summaries = [s for s in db.TRIAGE_SUMMARIES.values() if s["patient_id"] == patient_id]
    return {
        "patient_id": patient_id,
        "upcoming_appointments": sum(1 for a in appts if a["status"] == AppointmentStatus.upcoming),
        "completed_consultations": sum(1 for a in appts if a["status"] == AppointmentStatus.completed),
        "active_prescriptions": sum(1 for r in rxs if r["status"] in (PrescriptionStatus.approved, PrescriptionStatus.shared)),
        "ai_triage_sessions": len(summaries),
    }


# ===========================================================================
# GLOBAL EXCEPTION HANDLER
# ===========================================================================

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc),
            "disclaimer": "CareBridge AI — For emergencies call 1122 or 115.",
        },
    )
