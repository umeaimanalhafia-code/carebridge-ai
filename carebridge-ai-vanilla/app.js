/* ==========================================================================
   CareBridge AI - Vanilla JS Core Engine
   Single Page Application with State Management, AI Triage & Telemedicine Call
   ========================================================================== */

// --- Global Application State ---
const AppState = {
  theme: 'light',
  currentRole: 'patient', // 'patient' or 'doctor'
  currentView: 'home',
  aiLanguage: 'en', // 'en', 'ur', 'ur-Latn'
  aiStep: 0,
  aiData: {
    age: '',
    symptom: '',
    duration: '',
    severity: 5,
    conditions: '',
    meds: ''
  },
  selectedDoctorForBooking: null,
  bookingDate: 'Today, Nov 17',
  bookingSlot: '02:30 PM',
  doctors: [
    {
      id: 'doc_1',
      name: 'Dr. Sarah Jenkins, MD',
      specialty: 'Cardiologist',
      avatar: 'https://images.unsplash.com/photo-1559839734-2b71ea197ec2?auto=format&fit=crop&q=80&w=400',
      rating: 4.95,
      reviews: 184,
      experience: 14,
      languages: ['English', 'Spanish'],
      fee: 75,
      hospital: 'Johns Hopkins Medical Center',
      nextSlot: 'Today, 2:30 PM',
      slots: ['02:30 PM', '03:15 PM', '04:00 PM', '05:30 PM'],
      isOnline: true,
      bio: 'Board-certified cardiologist specializing in hypertension, arrhythmias, and heart wellness teleconsultations.'
    },
    {
      id: 'doc_2',
      name: 'Dr. Arshad Khan, MBBS, FCPS',
      specialty: 'General Physician',
      avatar: 'https://images.unsplash.com/photo-1622253692010-333f2da6031d?auto=format&fit=crop&q=80&w=400',
      rating: 4.92,
      reviews: 260,
      experience: 16,
      languages: ['English', 'Urdu', 'Hindi'],
      fee: 45,
      hospital: 'Aga Khan University Hospital',
      nextSlot: 'Today, 4:00 PM',
      slots: ['04:00 PM', '04:45 PM', '06:00 PM'],
      isOnline: true,
      bio: 'Family physician focusing on diabetes, infections, seasonal flus, and holistic preventive checkups.'
    },
    {
      id: 'doc_3',
      name: 'Dr. Elena Rostova, MD',
      specialty: 'Dermatologist',
      avatar: 'https://images.unsplash.com/photo-1594824813568-19e34927b2c0?auto=format&fit=crop&q=80&w=400',
      rating: 4.88,
      reviews: 142,
      experience: 11,
      languages: ['English', 'Russian'],
      fee: 65,
      hospital: 'St. Louis Dermatology Institute',
      nextSlot: 'Tomorrow, 10:00 AM',
      slots: ['10:00 AM', '11:15 AM', '02:00 PM'],
      isOnline: false,
      bio: 'Expert in eczema, psoriasis, acne management, and hair loss tele-triaging.'
    },
    {
      id: 'doc_4',
      name: 'Dr. Marcus Vance, MD',
      specialty: 'Pediatrician',
      avatar: 'https://images.unsplash.com/photo-1537368910025-700350fe46c7?auto=format&fit=crop&q=80&w=400',
      rating: 4.96,
      reviews: 310,
      experience: 18,
      languages: ['English'],
      fee: 60,
      hospital: 'Boston Children’s Health',
      nextSlot: 'Today, 5:00 PM',
      slots: ['05:00 PM', '05:45 PM', '06:30 PM'],
      isOnline: true,
      bio: 'Pediatrician caring for infants, fevers, allergies, and childhood wellness.'
    },
    {
      id: 'doc_5',
      name: 'Dr. Ayla Siddiqui, PsyD',
      specialty: 'Mental Health',
      avatar: 'https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?auto=format&fit=crop&q=80&w=400',
      rating: 4.98,
      reviews: 220,
      experience: 12,
      languages: ['English', 'Urdu'],
      fee: 80,
      hospital: 'MindWell Behavioral Health',
      nextSlot: 'Tomorrow, 3:00 PM',
      slots: ['03:00 PM', '04:00 PM'],
      isOnline: true,
      bio: 'Specialist focusing on workplace burnout, anxiety, depression, and cognitive resilience.'
    }
  ],
  medications: [
    { name: 'Metoprolol Succinate ER 25mg', dosage: '1 tablet (25mg)', frequency: 'Once daily morning', duration: '14 days' },
    { name: 'Magnesium Glycinate 200mg', dosage: '1 capsule (200mg)', frequency: 'Once daily bedtime', duration: '30 days' }
  ]
};

// --- View Router ---
function switchView(viewName) {
  AppState.currentView = viewName;
  document.querySelectorAll('.app-view').forEach(view => view.classList.remove('active'));
  
  const targetView = document.getElementById(`view-${viewName}`);
  if (targetView) targetView.classList.add('active');

  // Update navbar active button
  document.querySelectorAll('.nav-menu li button').forEach(btn => {
    btn.classList.remove('active');
    if (btn.innerText.toLowerCase().includes(viewName.replace('-', ' '))) {
      btn.classList.add('active');
    }
  });

  window.scrollTo({ top: 0, behavior: 'smooth' });
  refreshIcons();
}

// --- Theme Switcher ---
function toggleTheme() {
  const current = document.documentElement.getAttribute('data-theme') || 'light';
  const next = current === 'light' ? 'dark' : 'light';
  document.documentElement.setAttribute('data-theme', next);
  AppState.theme = next;
  
  const icon = document.getElementById('theme-icon');
  if (icon) {
    icon.setAttribute('data-lucide', next === 'dark' ? 'sun' : 'moon');
    refreshIcons();
  }
  showToast(`Switched to ${next} mode`, 'info');
}

// --- Role Switcher (Patient vs Doctor) ---
function toggleUserRole() {
  AppState.currentRole = AppState.currentRole === 'patient' ? 'doctor' : 'patient';
  const isDoc = AppState.currentRole === 'doctor';
  
  document.getElementById('role-label').innerText = isDoc ? 'Doctor View' : 'Patient View';
  document.getElementById('role-dot').style.background = isDoc ? 'var(--accent-teal)' : 'var(--primary-blue)';
  
  showToast(`Switched view to ${isDoc ? 'Dr. Sarah Jenkins' : 'Sarah Ahmed (Patient)'}`, 'info');
}

// --- Modals ---
function openModal(id) {
  const m = document.getElementById(id);
  if (m) m.classList.add('active');
}
function closeModal(id) {
  const m = document.getElementById(id);
  if (m) m.classList.remove('active');
}
function openEmergencyModal(reason) {
  openModal('modal-emergency');
}

// --- Toast Notifications ---
function showToast(message, type = 'info') {
  const container = document.getElementById('toast-container');
  if (!container) return;

  const toast = document.createElement('div');
  toast.className = 'toast';
  toast.innerHTML = `
    <span style="color: ${type === 'danger' ? '#ef4444' : type === 'success' ? '#10b981' : '#2563eb'}; font-weight: bold;">●</span>
    <span>${message}</span>
  `;
  container.appendChild(toast);
  setTimeout(() => toast.remove(), 4000);
}

// --- Doctor Directory & Filtering ---
function renderDoctors(list = AppState.doctors) {
  const container = document.getElementById('doctors-container');
  if (!container) return;

  container.innerHTML = list.map(doc => `
    <div class="doctor-card">
      <div>
        <div class="doc-header">
          <img src="${doc.avatar}" class="doc-avatar" alt="${doc.name}">
          <div>
            <h4 style="font-size: 1.05rem; font-weight: 800;">${doc.name}</h4>
            <span class="badge badge-teal" style="margin: 4px 0;">${doc.specialty}</span>
            <p style="font-size: 0.75rem; color: var(--text-muted);">${doc.hospital}</p>
            <div style="font-size: 0.8rem; margin-top: 4px;">
              <span style="color: #f59e0b; font-weight: 700;">★ ${doc.rating}</span>
              <span style="color: var(--text-muted);">(${doc.reviews} reviews) • ${doc.experience} yrs exp</span>
            </div>
          </div>
        </div>

        <p style="font-size: 0.8rem; color: var(--text-muted); margin: 14px 0; line-height: 1.5;">${doc.bio}</p>

        <div style="display: flex; justify-content: space-between; font-size: 0.8rem; border-top: 1px solid var(--border-color); padding-top: 10px;">
          <span>Fee: <strong style="font-size: 0.95rem;">$${doc.fee}</strong></span>
          <span style="color: var(--success-green); font-weight: 600;">${doc.nextSlot}</span>
        </div>
      </div>

      <div style="margin-top: 18px; display: grid; grid-template-columns: 1fr 1fr; gap: 8px;">
        <button class="btn btn-secondary" onclick="showToast('Profile: ${doc.name}', 'info')">View Profile</button>
        <button class="btn btn-primary" onclick="openBookingFlow('${doc.id}')">Book Visit</button>
      </div>
    </div>
  `).join('');
  refreshIcons();
}

function filterDoctors() {
  const query = document.getElementById('doc-search-input')?.value.toLowerCase() || '';
  const spec = document.getElementById('doc-specialty-filter')?.value || 'All';
  const lang = document.getElementById('doc-lang-filter')?.value || 'All';
  const avail = document.getElementById('doc-avail-filter')?.value || 'All';

  const filtered = AppState.doctors.filter(d => {
    const matchesQ = !query || d.name.toLowerCase().includes(query) || d.specialty.toLowerCase().includes(query);
    const matchesSpec = spec === 'All' || d.specialty === spec;
    const matchesLang = lang === 'All' || d.languages.includes(lang);
    const matchesAvail = avail === 'All' || (avail === 'Online' && d.isOnline) || (avail === 'Today' && d.nextSlot.startsWith('Today'));
    return matchesQ && matchesSpec && matchesLang && matchesAvail;
  });

  renderDoctors(filtered);
}

// --- Appointment Booking Flow ---
function openBookingFlow(docId) {
  const doc = AppState.doctors.find(d => d.id === docId);
  if (!doc) return;
  AppState.selectedDoctorForBooking = doc;

  document.getElementById('booking-modal-title').innerText = `Book ${doc.name}`;
  document.getElementById('booking-step-form').style.display = 'block';
  document.getElementById('booking-step-success').style.display = 'none';

  // Render slots
  const slotsContainer = document.getElementById('booking-slots-chips');
  slotsContainer.innerHTML = doc.slots.map((s, idx) => `
    <button class="chat-pill ${idx === 0 ? 'active' : ''}" onclick="setBookingSlot(this, '${s}')">${s}</button>
  `).join('');

  AppState.bookingSlot = doc.slots[0];
  openModal('modal-booking');
}

function setBookingDate(el, date) {
  document.querySelectorAll('#booking-date-chips .chat-pill').forEach(b => b.classList.remove('active'));
  el.classList.add('active');
  AppState.bookingDate = date;
}

function setBookingSlot(el, slot) {
  document.querySelectorAll('#booking-slots-chips .chat-pill').forEach(b => b.classList.remove('active'));
  el.classList.add('active');
  AppState.bookingSlot = slot;
}

function confirmAppointmentBooking() {
  document.getElementById('booking-step-form').style.display = 'none';
  document.getElementById('booking-step-success').style.display = 'block';
  showToast(`Appointment confirmed with ${AppState.selectedDoctorForBooking?.name}!`, 'success');
}

// --- AI Health Assistant Interactive Engine ---
const AILocales = {
  en: {
    welcome: "Welcome to CareBridge AI Health Assistant. I can help organize your symptoms before your doctor visit. I cannot diagnose or prescribe treatment.\n\nTo begin, what is your age range?",
    ageOptions: ['Under 18', '18 - 35', '36 - 55', '56+'],
    qSymptom: "What is your main symptom or health concern?",
    symptomOptions: ['Chest tightness & palpitations', 'Persistent migraine', 'Skin rash / eczema', 'Seasonal fever'],
    qDuration: "How long have you been experiencing this symptom?",
    durationOptions: ['Under 24 hours', '2 to 4 days', '1 to 2 weeks', 'Over a month'],
    qSeverity: "On a scale of 1 to 10, how severe is your discomfort?",
    severityOptions: ['2 - Mild', '4 - Moderate', '7 - Severe', '9 - Extreme'],
    qHistory: "Do you have any existing medical conditions (e.g. Hypertension, Diabetes)?",
    historyOptions: ['None reported', 'Hypertension (High BP)', 'Type 2 Diabetes', 'Asthma'],
    summaryReady: "Thank you! I have organized your health notes into a Doctor-Ready Clinical Summary card below:"
  },
  ur: {
    welcome: "کیئر برج اے آئی میں خوش آمدید۔ میں ڈاکٹر کے معائنے سے قبل آپ کی علامات کو منظم کرتا ہوں۔ میں تشخیص یا علاج تجویز نہیں کرتا۔\n\nشروع کرنے کے لیے، آپ کا عمر کا گروپ کیا ہے؟",
    ageOptions: ['18 سے کم', '18 - 35', '36 - 55', '56+'],
    qSymptom: "آپ کی بنیادی تکلیف یا علامات کیا ہیں؟",
    symptomOptions: ['سینے میں دباؤ اور دھڑکن', 'شدید سر درد (درد شقیقہ)', 'جلد کی الرجی یا خارش', 'موسمی بخار اور کھانسی'],
    qDuration: "یہ تکلیف کتنے عرصے سے ہے؟",
    durationOptions: ['24 گھنٹے سے کم', '2 سے 4 دن', '1 سے 2 ہفتے', 'ایک ماہ سے زیادہ'],
    qSeverity: "1 سے 10 کے پیمانے پر تکلیف کی شدت کتنی ہے؟",
    severityOptions: ['2 - ہلکی', '4 - درمیانی', '7 - شدید', '9 - انتہائی شدید'],
    qHistory: "کیا آپ کو پہلے سے کوئی بیماری ہے (جیسے شوگر یا بلڈ پریشر)؟",
    historyOptions: ['کوئی نہیں', 'ہائی بلڈ پریشر', 'شوگر (ذیابیطس)', 'دمہ'],
    summaryReady: "بہت شکریہ! آپ کی علامات کا خلاصہ نیچے تیار ہے:"
  },
  'ur-Latn': {
    welcome: "CareBridge AI Assistant me khushamdeed. Main doctor visit se pehle aapki alamaat summarize kar sakta hoon. Main dawai prescribe ya diagnose nahi karta.\n\nAapki umar ka bracket kya hai?",
    ageOptions: ['Under 18', '18 - 35', '36 - 55', '56+'],
    qSymptom: "Aapko kya takleef ya symptoms mehsoos ho rahe hain?",
    symptomOptions: ['Seene me dabao / palpitations', 'Sar dard / migraine', 'Skin rash / allergy', 'Bukhar aur gala kharab'],
    qDuration: "Yeh takleef kitne time se hai?",
    durationOptions: ['24 ghante se kam', '2 se 4 din', '1 se 2 hafte', '1 maah se zyada'],
    qSeverity: "1 se 10 ke scale par takleef kitni shaded hai?",
    severityOptions: ['2 - Halki', '4 - Normal', '7 - Shaded', '9 - Bohat shaded'],
    qHistory: "Kya aapko pehle se koi bimari hai (Sugar, BP vagera)?",
    historyOptions: ['Koi nahi', 'Hypertension (High BP)', 'Sugar (Diabetes)', 'Asthma'],
    summaryReady: "Shukriya! Aapka Doctor-Ready Summary tayyar hai:"
  }
};

const RED_FLAGS = ['chest pain', 'heart attack', 'can’t breathe', 'cannot breathe', 'stroke', 'unconscious', 'bleeding', 'suicide', 'seene me dard', 'saans me dushwari'];

function setAILanguage(lang) {
  AppState.aiLanguage = lang;
  document.querySelectorAll('.chat-pill').forEach(b => b.classList.remove('active'));
  if (lang === 'en') document.getElementById('btn-lang-en')?.classList.add('active');
  if (lang === 'ur') document.getElementById('btn-lang-ur')?.classList.add('active');
  if (lang === 'ur-Latn') document.getElementById('btn-lang-roman')?.classList.add('active');

  initAIChat();
}

function initAIChat() {
  AppState.aiStep = 0;
  const container = document.getElementById('chat-messages-container');
  if (!container) return;

  const loc = AILocales[AppState.aiLanguage] || AILocales.en;
  container.innerHTML = `
    <div class="message-row">
      <div class="msg-avatar ai"><i data-lucide="bot" style="width: 18px; height: 18px;"></i></div>
      <div>
        <div class="msg-bubble">${loc.welcome.replace(/\n/g, '<br>')}</div>
        <div class="chat-options-pills">
          ${loc.ageOptions.map(opt => `<button class="chat-pill" onclick="handleAIOption('${opt}')">${opt}</button>`).join('')}
        </div>
      </div>
    </div>
  `;
  refreshIcons();
}

function handleAIOption(text) {
  sendUserAIMessage(text);
}

function sendUserAIMessage(customText) {
  const input = document.getElementById('ai-chat-input');
  const text = customText || input?.value.trim();
  if (!text) return;
  if (input) input.value = '';

  const container = document.getElementById('chat-messages-container');
  
  // Append user bubble
  container.innerHTML += `
    <div class="message-row user">
      <div class="msg-avatar user">You</div>
      <div class="msg-bubble">${text}</div>
    </div>
  `;

  // Check Red Flag Emergency Keywords
  const isEmergency = RED_FLAGS.some(flag => text.toLowerCase().includes(flag));
  if (isEmergency) {
    container.innerHTML += `
      <div class="message-row">
        <div class="msg-avatar ai" style="background: var(--danger-red);"><i data-lucide="alert-octagon"></i></div>
        <div class="msg-bubble" style="background: rgba(239, 68, 68, 0.15); border: 2px solid var(--danger-red); color: var(--danger-red); font-weight: bold;">
          ⚠️ EMERGENCY DETECTED: The symptoms you described require immediate emergency medical care. Please call 911 / 112 / 1122 right away.
        </div>
      </div>
    `;
    openEmergencyModal(text);
    container.scrollTop = container.scrollHeight;
    refreshIcons();
    return;
  }

  // Conversation State Flow Progression
  const loc = AILocales[AppState.aiLanguage] || AILocales.en;
  AppState.aiStep++;

  setTimeout(() => {
    if (AppState.aiStep === 1) {
      AppState.aiData.age = text;
      appendAIBubble(loc.qSymptom, loc.symptomOptions);
    } else if (AppState.aiStep === 2) {
      AppState.aiData.symptom = text;
      appendAIBubble(loc.qDuration, loc.durationOptions);
    } else if (AppState.aiStep === 3) {
      AppState.aiData.duration = text;
      appendAIBubble(loc.qSeverity, loc.severityOptions);
    } else if (AppState.aiStep === 4) {
      AppState.aiData.severity = text;
      appendAIBubble(loc.qHistory, loc.historyOptions);
    } else {
      AppState.aiData.conditions = text;
      appendAISummaryCard();
    }
    container.scrollTop = container.scrollHeight;
  }, 400);
}

function appendAIBubble(text, options = []) {
  const container = document.getElementById('chat-messages-container');
  container.innerHTML += `
    <div class="message-row">
      <div class="msg-avatar ai"><i data-lucide="bot" style="width: 18px; height: 18px;"></i></div>
      <div>
        <div class="msg-bubble">${text}</div>
        <div class="chat-options-pills">
          ${options.map(opt => `<button class="chat-pill" onclick="handleAIOption('${opt}')">${opt}</button>`).join('')}
        </div>
      </div>
    </div>
  `;
  refreshIcons();
}

function appendAISummaryCard() {
  const container = document.getElementById('chat-messages-container');
  const loc = AILocales[AppState.aiLanguage] || AILocales.en;

  container.innerHTML += `
    <div class="message-row" style="max-width: 90%;">
      <div class="msg-avatar ai"><i data-lucide="file-check"></i></div>
      <div style="width: 100%;">
        <div class="msg-bubble" style="margin-bottom: 8px;">${loc.summaryReady}</div>
        <div style="background: var(--bg-card); border: 2px solid var(--accent-teal); border-radius: var(--radius-md); padding: 18px; font-size: 0.85rem; box-shadow: var(--shadow-md);">
          <div style="display: flex; justify-content: space-between; border-bottom: 1px solid var(--border-color); padding-bottom: 10px; margin-bottom: 10px;">
            <strong style="color: var(--primary-blue);">Doctor-Ready Summary</strong>
            <span class="badge badge-teal">Specialty: Cardiologist</span>
          </div>
          <p><strong>Concern:</strong> ${AppState.aiData.symptom || 'Chest tightness & palpitations'}</p>
          <p><strong>Duration & Severity:</strong> ${AppState.aiData.duration || '2-4 days'} • Severity: ${AppState.aiData.severity || '4'}/10</p>
          <p><strong>History:</strong> ${AppState.aiData.conditions || 'None reported'}</p>
          
          <div style="margin-top: 14px; display: flex; gap: 10px;">
            <button class="btn btn-primary" onclick="switchView('doctors'); showToast('Attached AI summary to booking', 'success');">Book Doctor with Summary</button>
            <button class="btn btn-secondary" onclick="showToast('Summary saved to health profile', 'success')">Save to Records</button>
          </div>
        </div>
      </div>
    </div>
  `;
  refreshIcons();
}

function simulateVoiceInput() {
  showToast('Voice input simulation started...', 'info');
  setTimeout(() => {
    const input = document.getElementById('ai-chat-input');
    if (input) input.value = "I have had mild retrosternal palpitations for 3 days";
    showToast('Voice captured: "I have had mild retrosternal palpitations for 3 days"', 'success');
  }, 1200);
}

// --- Video Consultation Controls ---
function toggleMic(btn) {
  btn.classList.toggle('active');
  showToast(btn.classList.contains('active') ? 'Microphone Muted' : 'Microphone Unmuted', 'info');
}
function toggleCam(btn) {
  btn.classList.toggle('active');
  showToast(btn.classList.contains('active') ? 'Camera Disabled' : 'Camera Enabled', 'info');
}
function toggleShare(btn) {
  btn.classList.toggle('active');
  showToast(btn.classList.contains('active') ? 'Screen Sharing Started' : 'Screen Sharing Stopped', 'info');
}
function switchCallTab(tab) {
  const panel = document.getElementById('call-panel-content');
  if (!panel) return;

  if (tab === 'live-notes') {
    panel.innerHTML = `
      <div style="background: rgba(20,184,166,0.15); border: 1px solid var(--accent-teal); padding: 10px; border-radius: var(--radius-sm); margin-bottom: 12px; color: var(--accent-teal); font-size: 0.75rem;">
        ● Live AI Clinical Note Stream
      </div>
      <div style="display: flex; flex-direction: column; gap: 10px;">
        <div style="background: #1e293b; padding: 10px; border-radius: 8px;">
          <strong style="color: #93c5fd; font-size: 0.75rem;">02:30:15 - Chief Complaint</strong>
          <p style="font-size: 0.8rem; margin-top: 2px;">Patient reports retrosternal chest tightness onset 4 days ago with palpitations on stairs.</p>
        </div>
        <div style="background: #1e293b; padding: 10px; border-radius: 8px;">
          <strong style="color: #93c5fd; font-size: 0.75rem;">02:31:40 - Vitals & Findings</strong>
          <p style="font-size: 0.8rem; margin-top: 2px;">Home BP 128/82 mmHg. Resting pulse 76 bpm regular. No syncope.</p>
        </div>
      </div>
    `;
  } else {
    panel.innerHTML = `
      <div style="display: flex; flex-direction: column; gap: 10px; height: 100%;">
        <div style="background: #1e293b; padding: 10px; border-radius: 8px;">
          <strong style="color: #93c5fd; font-size: 0.75rem;">Dr. Sarah Jenkins</strong>
          <p style="font-size: 0.8rem;">Hello Sarah, I can hear you clearly. Reviewing your AI summary.</p>
        </div>
        <div style="background: #1e3a8a; padding: 10px; border-radius: 8px; align-self: flex-end;">
          <strong style="color: white; font-size: 0.75rem;">You</strong>
          <p style="font-size: 0.8rem;">Thank you doctor, looking forward to your advice.</p>
        </div>
      </div>
    `;
  }
}
function endCall() {
  showToast('Consultation ended. Doctor notes updated.', 'success');
  switchView('prescriptions');
}

// --- Doctor Dashboard & Prescription Builder ---
function renderMedicationRows() {
  const container = document.getElementById('rx-meds-container');
  if (!container) return;

  container.innerHTML = AppState.medications.map((m, idx) => `
    <div style="background: var(--bg-card-subtle); padding: 10px 14px; border-radius: var(--radius-sm); border: 1px solid var(--border-color); display: flex; justify-content: space-between; align-items: center; font-size: 0.8rem;">
      <div>
        <strong>${m.name}</strong> • ${m.dosage}<br>
        <span style="color: var(--text-muted);">${m.frequency} (${m.duration})</span>
      </div>
      <button onclick="removeMedicationRow(${idx})" style="background: transparent; border: none; color: var(--danger-red); cursor: pointer;">✕</button>
    </div>
  `).join('');

  // Update prescription preview table
  const tableBody = document.getElementById('rx-view-meds-table');
  if (tableBody) {
    tableBody.innerHTML = AppState.medications.map(m => `
      <tr style="border-bottom: 1px solid #e2e8f0;">
        <td style="padding: 10px 0; font-weight: 700;">${m.name}</td>
        <td style="padding: 10px;">${m.dosage}</td>
        <td style="padding: 10px;">${m.frequency}</td>
        <td style="padding: 10px; color: var(--primary-blue); font-weight: 600;">${m.duration}</td>
      </tr>
    `).join('');
  }
}

function addMedicationRow() {
  const name = prompt('Medication Name & Strength (e.g. Amoxicillin 500mg):');
  if (!name) return;
  const dosage = prompt('Dosage (e.g. 1 capsule):') || '1 unit';
  const frequency = prompt('Frequency (e.g. Twice daily):') || 'Twice daily';
  const duration = prompt('Duration (e.g. 7 days):') || '7 days';

  AppState.medications.push({ name, dosage, frequency, duration });
  renderMedicationRows();
  showToast(`${name} added to prescription`, 'success');
}

function removeMedicationRow(index) {
  AppState.medications.splice(index, 1);
  renderMedicationRows();
}

function saveDoctorNotes() {
  showToast('SOAP Clinical notes saved successfully', 'success');
}

function issuePrescription() {
  const isApproved = document.getElementById('doctor-sign-checkbox')?.checked;
  if (!isApproved) {
    alert('Please check the Doctor Legal Sign-off checkbox before issuing.');
    return;
  }
  const diag = document.getElementById('rx-diagnosis-input')?.value;
  if (diag) {
    document.getElementById('rx-view-diagnosis').innerText = diag;
  }

  showToast('Prescription officially signed and dispatched to patient!', 'success');
  switchView('prescriptions');
}

function copyRxShareLink() {
  navigator.clipboard?.writeText('https://carebridge.ai/rx/verify/RX-CB-2026-8842');
  showToast('Secure prescription share link copied to clipboard!', 'success');
}

// --- Initialization ---
function refreshIcons() {
  if (window.lucide) {
    window.lucide.createIcons();
  }
}

window.addEventListener('DOMContentLoaded', () => {
  renderDoctors();
  renderMedicationRows();
  initAIChat();
  switchCallTab('live-notes');
  refreshIcons();
});
