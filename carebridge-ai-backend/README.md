# CareBridge AI — Python Backend

> ⚠️ **Medical Disclaimer:** CareBridge AI does not diagnose or replace a qualified doctor. For emergencies, contact local emergency services immediately (1122 / 115 / 112).

---

## 📁 File Structure

```
carebridge-ai-backend/
├── main.py          ← FastAPI app + all API routes
├── models.py        ← Pydantic data models (mirrors TypeScript types)
├── database.py      ← In-memory mock data store
├── triage.py        ← AI triage engine (red-flag detection + summary)
├── requirements.txt ← Python dependencies
└── README.md        ← This file
```

---

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.10 or later
- pip

### 2. Install dependencies

```bash
cd carebridge-ai-backend
pip install -r requirements.txt
```

### 3. Run the development server

```bash
uvicorn main:app --reload --port 8000
```

### 4. Open API docs

- **Swagger UI:** http://localhost:8000/docs  
- **ReDoc:** http://localhost:8000/redoc  
- **Health check:** http://localhost:8000/health

---

## 🔑 Demo Credentials

| Role    | Email                       | Password   |
|---------|-----------------------------|------------|
| Patient | patient@carebridge.ai       | demo1234   |
| Doctor  | doctor@carebridge.ai        | demo1234   |

---

## 📡 API Endpoints

### Auth
| Method | Route | Description |
|--------|-------|-------------|
| POST | `/api/auth/login` | Login → returns mock token + user |
| POST | `/api/auth/register` | Register new patient |

### Users
| Method | Route | Description |
|--------|-------|-------------|
| GET | `/api/users` | List all users (filter by role) |
| GET | `/api/users/{id}` | Get user profile |

### Doctors
| Method | Route | Description |
|--------|-------|-------------|
| GET | `/api/doctors` | List doctors (filter: spec, language, available, rating, fee) |
| GET | `/api/doctors/{id}` | Full doctor profile + slots + reviews |

### Appointments
| Method | Route | Description |
|--------|-------|-------------|
| GET | `/api/appointments` | List appointments (filter: patient_id, doctor_id, status) |
| POST | `/api/appointments` | Book a new appointment |
| GET | `/api/appointments/{id}` | Single appointment detail |
| PATCH | `/api/appointments/{id}/cancel` | Cancel appointment |
| PATCH | `/api/appointments/{id}/start` | Mark as in-progress |
| PATCH | `/api/appointments/{id}/complete` | Mark as completed |

### AI Triage
| Method | Route | Description |
|--------|-------|-------------|
| POST | `/api/ai/triage` | Submit symptoms → get red-flag check + Doctor-Ready Summary |
| GET | `/api/ai/summary/{patient_id}` | All summaries for a patient |
| GET | `/api/ai/summary/detail/{summary_id}` | Single summary |

### Prescriptions
| Method | Route | Description |
|--------|-------|-------------|
| GET | `/api/prescriptions` | List prescriptions (filter: patient_id, doctor_id, status) |
| POST | `/api/prescriptions` | Doctor creates draft prescription |
| GET | `/api/prescriptions/{id}` | Single prescription |
| PATCH | `/api/prescriptions/{id}/approve` | Doctor approves → visible to patient |
| PATCH | `/api/prescriptions/{id}/share` | Mark as shared |

### Consultation Notes (SOAP)
| Method | Route | Description |
|--------|-------|-------------|
| POST | `/api/notes` | Doctor creates SOAP note |
| GET | `/api/notes` | List notes (filter: appointment_id, patient_id, doctor_id) |
| PATCH | `/api/notes/{id}/approve` | Doctor approves note |

### Chat
| Method | Route | Description |
|--------|-------|-------------|
| POST | `/api/chat` | Send a chat message in a consultation |
| GET | `/api/chat/{appointment_id}` | Get all messages for an appointment |

### Statistics
| Method | Route | Description |
|--------|-------|-------------|
| GET | `/api/stats/doctor/{doctor_id}` | Doctor dashboard stats |
| GET | `/api/stats/patient/{patient_id}` | Patient dashboard stats |

---

## 🔗 Connect to Next.js Frontend

In your Next.js project, update `.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Then replace `mockData.ts` calls with `fetch()` or `axios` calls to the API.

---

## 🏗️ Production Upgrade Path

| Feature | Current (Demo) | Production Recommendation |
|---------|----------------|--------------------------|
| Database | Python dict (in-memory) | PostgreSQL + SQLAlchemy |
| Auth | Mock token string | JWT with RS256, refresh tokens |
| Passwords | Plain text | bcrypt hashed via passlib |
| AI Triage | Rule-based keyword match | Gemini Pro / GPT-4 API |
| Video Calls | Frontend placeholder | Twilio / Daily.co WebRTC API |
| File Storage | None | GCS / S3 for prescriptions |
| Deployment | Local uvicorn | Docker + Cloud Run / Railway |

---

## 🛡️ Safety Notes

- The AI triage endpoint **never** returns a diagnosis or prescription.
- Red-flag symptoms trigger an emergency message with local emergency numbers (1122, 115, 112).
- Prescriptions require **explicit doctor approval** before they become patient-visible.
- All consultation notes require **doctor sign-off** before sharing.
