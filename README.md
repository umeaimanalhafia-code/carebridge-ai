# 🏥 CareBridge AI — Complete Project Package

> **"Your Doctor, One Video Call Away."**

⚠️ **Medical Disclaimer:** CareBridge AI does not diagnose or replace a qualified doctor.
For emergencies, contact local emergency services immediately (1122 / 115 / 112).

---

## 📦 What's Inside This ZIP

```
CareBridge-AI-COMPLETE/
│
├── 📁 frontend-standalone-HTML-CSS-JS/
│   ├── index.html      ← Main app (open this in any browser — no install needed)
│   ├── styles.css      ← All styling
│   └── app.js          ← All JavaScript / app logic
│
└── 📁 backend-python-FastAPI/
    ├── main.py         ← FastAPI server + all 25 API routes
    ├── models.py       ← Pydantic data models
    ├── database.py     ← In-memory mock data + sample doctors/patients
    ├── triage.py       ← AI triage engine (red-flag detection)
    ├── requirements.txt← Python dependencies
    └── README.md       ← Backend documentation
```

---

## 🚀 HOW TO RUN

### Option 1 — Frontend Only (No install needed!)
1. Open `frontend-standalone-HTML-CSS-JS/` folder
2. Double-click `index.html`
3. App opens in your browser ✅

### Option 2 — With Python Backend
```bash
# Step 1: Install Python from python.org

# Step 2: Go to backend folder
cd backend-python-FastAPI

# Step 3: Install dependencies
pip install -r requirements.txt

# Step 4: Start the server
uvicorn main:app --reload --port 8000

# Step 5: API docs open in browser:
# http://localhost:8000/docs
```

---

## 🔑 Demo Login Credentials

| Role    | Email                   | Password |
|---------|-------------------------|----------|
| Patient | patient@carebridge.ai   | demo1234 |
| Doctor  | doctor@carebridge.ai    | demo1234 |

---

## 📱 App Pages & Features

| Page | Description |
|------|-------------|
| 🏠 Landing Page | Hero section, doctors preview, how-it-works, testimonials |
| 🔐 Login / Sign Up | Patient authentication forms |
| 📊 Patient Dashboard | Appointments, prescriptions, quick actions |
| 👨‍⚕️ Find Doctors | Search & filter, doctor cards, booking flow |
| 🤖 AI Health Assistant | Symptom checker chatbot (EN/Urdu/Roman Urdu) |
| 📹 Video Consultation | Video call room with AI live notes & chat |
| 🩺 Doctor Dashboard | Today's patients, notes editor, prescription builder |
| 💊 Prescriptions | Digital prescriptions with doctor-approved badge |

---

## 🛡️ Safety Features Built-In

- ✅ Emergency disclaimer always visible
- ✅ AI never diagnoses or prescribes — only organizes symptoms
- ✅ Red-flag symptom detection → Emergency alert card shown
- ✅ Prescriptions need explicit doctor approval before patient can see them

---

Built with ❤️ using HTML5, CSS3, JavaScript (Frontend) + FastAPI Python (Backend)
