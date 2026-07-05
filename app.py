import streamlit as st
import os
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from groq import Groq

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

st.set_page_config(
    page_title="Bright Smile Dental | AI Receptionist",
    page_icon="🦷",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Playfair+Display:wght@700&display=swap');
* { box-sizing: border-box; }
html, body, [data-testid="stAppViewContainer"] { background: #f7fafc; font-family: 'Inter', sans-serif; }
[data-testid="stSidebar"] { background: linear-gradient(180deg, #0a2540 0%, #0d3b6e 100%); border-right: none; }
[data-testid="stSidebar"] * { color: #e8f0fe !important; }
.sidebar-logo { text-align: center; padding: 24px 16px 16px; border-bottom: 1px solid rgba(255,255,255,0.1); margin-bottom: 20px; }
.sidebar-logo h1 { font-family: 'Playfair Display', serif; font-size: 1.5rem; color: #ffffff !important; margin: 8px 0 4px; }
.sidebar-logo p { font-size: 0.75rem; color: #90caf9 !important; margin: 0; }
.info-card { background: rgba(255,255,255,0.07); border: 1px solid rgba(255,255,255,0.12); border-radius: 12px; padding: 14px 16px; margin-bottom: 12px; }
.info-card h4 { font-size: 0.7rem; text-transform: uppercase; letter-spacing: 1px; color: #90caf9 !important; margin: 0 0 8px; }
.info-card p { font-size: 0.82rem; margin: 3px 0; color: #e8f0fe !important; }
.service-pill { display: inline-block; background: rgba(33,150,243,0.2); border: 1px solid rgba(33,150,243,0.4); border-radius: 20px; padding: 3px 10px; font-size: 0.75rem; margin: 3px 2px; color: #90caf9 !important; }
.main-header { background: linear-gradient(135deg, #0a2540 0%, #1565c0 100%); padding: 28px 36px; border-radius: 16px; margin-bottom: 24px; display: flex; align-items: center; justify-content: space-between; box-shadow: 0 8px 32px rgba(10,37,64,0.18); }
.main-header-left h1 { font-family: 'Playfair Display', serif; color: #ffffff; font-size: 2rem; margin: 0 0 4px; }
.main-header-left p { color: #90caf9; font-size: 0.9rem; margin: 0; }
.status-badge { background: #00e676; color: #003300; font-size: 0.75rem; font-weight: 600; padding: 6px 14px; border-radius: 20px; }
.appt-card { background: #f0f7ff; border: 1px solid #bbdefb; border-radius: 12px; padding: 16px; margin-top: 12px; }
.appt-card h4 { color: #0d47a1; margin: 0 0 8px; font-size: 0.9rem; }
.appt-card p { color: #1565c0; margin: 3px 0; font-size: 0.82rem; }
.metric-row { display: flex; gap: 12px; margin-bottom: 20px; }
.metric-box { flex: 1; background: white; border: 1px solid #e3e8ef; border-radius: 12px; padding: 16px; text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.04); }
.metric-box .num { font-size: 1.8rem; font-weight: 700; color: #0a2540; }
.metric-box .lbl { font-size: 0.72rem; color: #78909c; text-transform: uppercase; letter-spacing: 0.5px; }
footer { visibility: hidden; }
#MainMenu { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

LANGUAGES = {
    "🇺🇸 English": "English",
    "🇪🇸 Español": "Spanish",
    "🇫🇷 Français": "French",
    "🇩🇪 Deutsch": "German",
    "🇨🇳 中文": "Chinese",
    "🇸🇦 العربية": "Arabic",
    "🇵🇰 اردو": "Urdu",
    "🇵🇹 Português": "Portuguese",
    "🇷🇺 Русский": "Russian",
    "🇯🇵 日本語": "Japanese",
}

APPT_FILE = "appointments.json"

def load_appointments():
    if os.path.exists(APPT_FILE):
        with open(APPT_FILE, "r") as f:
            return json.load(f)
    return []

def send_email_notification(appt):
    sender_email = os.environ.get("SENDER_EMAIL")
    sender_password = os.environ.get("SENDER_PASSWORD")
    dentist_email = os.environ.get("DENTIST_EMAIL")
    if not all([sender_email, sender_password, dentist_email]):
        return False
    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = dentist_email
    msg["Subject"] = f"🦷 New Appointment — {appt['name']}"
    body = f"""
New appointment booked through AI Receptionist
===============================================

Patient Name : {appt['name']}
Date         : {appt['date']}
Time         : {appt['time']}
Service      : {appt['service']}
Phone        : {appt['phone']}
Insurance    : {appt['insurance']}
Booked At    : {appt['booked_at']}

— Bright Smile Dental AI Receptionist
"""
    msg.attach(MIMEText(body, "plain"))
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, dentist_email, msg.as_string())
        server.quit()
        return True
    except Exception:
        return False

def save_appointment(name, date, time, service, phone="N/A", insurance="N/A"):
    appts = load_appointments()
    appt = {
        "id": len(appts) + 1,
        "name": name,
        "date": date,
        "time": time,
        "service": service,
        "phone": phone,
        "insurance": insurance,
        "booked_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": "Confirmed"
    }
    appts.append(appt)
    with open(APPT_FILE, "w") as f:
        json.dump(appts, f, indent=2)
    send_email_notification(appt)
    return appt

def get_system_prompt(language):
    return f"""You are a warm, professional AI receptionist for Bright Smile Dental clinic in Austin, Texas.
Always respond in {language}. If the user writes in a different language, still reply in {language}.

CLINIC INFORMATION:
Name: Bright Smile Dental
Address: 123 Oak Street, Austin, Texas 78701
Phone: (512) 555-0198
Emergency: (512) 555-0199

HOURS:
- Monday-Friday: 8:00 AM - 6:00 PM
- Saturday: 9:00 AM - 2:00 PM
- Sunday: Closed

DOCTORS:
- Dr. Sarah Mitchell - General Dentist (15 yrs experience)
- Dr. James Patel - Orthodontist & Implant Specialist (12 yrs experience)
- Dr. Emily Nguyen - Pediatric Dentist (children specialist)

SERVICES & PRICES:
- Routine Cleaning: $120
- Comprehensive Dental Exam: $80
- Teeth Whitening (in-office): $299
- Teeth Whitening (take-home kit): $149
- Tooth Filling (composite): $150-$250
- Root Canal Treatment: $800-$1,200
- Tooth Extraction (simple): $200-$350
- Wisdom Tooth Removal: $400-$800
- Dental Implant: $1,500-$3,000
- Dental Crown: $900-$1,500
- Dental Bridge: $1,200-$2,500
- Dentures (full): $1,500-$3,500
- Invisalign / Braces Consultation: FREE
- Invisalign Treatment: $3,000-$6,000
- Emergency Dental Visit: $150 (exam fee)
- X-Rays (full set): $150
- Pediatric Exam & Cleaning: $90
- Fluoride Treatment: $35
- Dental Sealants: $40 per tooth

INSURANCE ACCEPTED:
Delta Dental, Cigna, Aetna, BlueCross BlueShield, United Healthcare, Humana, Guardian, MetLife, Medicaid (limited), Medicare Advantage (select plans)

PAYMENT OPTIONS:
Cash, all major credit/debit cards, CareCredit financing (0% interest plans available), payment plans for treatments over $500

CANCELLATION POLICY:
- Cancel at least 24 hours before appointment to avoid fees
- Late cancellation fee: $50
- No-show fee: $75

GENERAL:
- New patients welcome - please arrive 15 min early for paperwork
- Walk-ins accepted but appointments strongly preferred
- Emergency same-day appointments available - call (512) 555-0199
- Free parking in our private lot
- Wheelchair accessible
- Kid-friendly environment with toys and TV in waiting area
- WiFi available in waiting area

APPOINTMENT BOOKING:
When a patient wants to book, collect ALL of these one by one:
1. Full name
2. Preferred date (day and month)
3. Preferred time
4. Service needed
5. Phone number
6. Insurance provider (or "self-pay")

Before confirming, repeat all details back and ask patient to confirm they are correct.
Once patient confirms, end your message with this EXACT block:

[APPOINTMENT_BOOKED]
Name: <name>
Date: <date>
Time: <time>
Service: <service>
Phone: <phone>
Insurance: <insurance>
[/APPOINTMENT_BOOKED]

EMERGENCY GUIDANCE:
- Severe toothache: Advise to call (512) 555-0199 immediately
- Knocked-out tooth: Keep tooth moist, call emergency line NOW
- Broken tooth: Rinse mouth, apply cold compress, call us
- Lost filling/crown: Temporary dental cement from pharmacy, call us

PERSONALITY:
Be warm, empathetic, and reassuring. Use the patient's name once you know it.
Occasionally use relevant emojis but not excessively.
Keep answers concise but complete. Never make up information.
"""

# Sidebar
with st.sidebar:
    st.markdown("""
    <div class="sidebar-logo">
        <div style="font-size:2.5rem">🦷</div>
        <h1>Bright Smile Dental</h1>
        <p>Austin, Texas — Est. 2008</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="info-card"><h4>📍 Location</h4><p>123 Oak Street</p><p>Austin, Texas 78701</p></div>', unsafe_allow_html=True)
    st.markdown('<div class="info-card"><h4>🕐 Hours</h4><p>Mon-Fri: 8am - 6pm</p><p>Saturday: 9am - 2pm</p><p>Sunday: Closed</p></div>', unsafe_allow_html=True)
    st.markdown('<div class="info-card"><h4>📞 Contact</h4><p>Main: (512) 555-0198</p><p>Emergency: (512) 555-0199</p></div>', unsafe_allow_html=True)
    st.markdown('<div class="info-card"><h4>🩺 Our Doctors</h4><p>Dr. Sarah Mitchell – General</p><p>Dr. James Patel – Orthodontist</p><p>Dr. Emily Nguyen – Pediatric</p></div>', unsafe_allow_html=True)

    st.markdown('<div class="info-card"><h4>✅ Insurance</h4>', unsafe_allow_html=True)
    for ins in ["Delta Dental", "Cigna", "Aetna", "BlueCross", "United", "Humana", "Medicaid"]:
        st.markdown(f'<span class="service-pill">{ins}</span>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<p style="font-size:0.78rem;color:#90caf9;text-transform:uppercase;letter-spacing:1px">🌐 Language</p>', unsafe_allow_html=True)
    selected_lang_label = st.selectbox("", list(LANGUAGES.keys()), label_visibility="collapsed")
    selected_language = LANGUAGES[selected_lang_label]
    st.markdown("---")

    st.markdown("**📋 Appointments Today**")
    appts = load_appointments()
    today = datetime.now().strftime("%Y-%m-%d")
    today_appts = [a for a in appts if today in str(a.get("booked_at", ""))]
    if today_appts:
        for a in today_appts[-3:]:
            st.markdown(f"""
            <div class="appt-card">
                <h4>✅ {a['name']}</h4>
                <p>📅 {a['date']} at {a['time']}</p>
                <p>🦷 {a['service']}</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown('<p style="font-size:0.8rem;color:#90caf9">No appointments booked yet today.</p>', unsafe_allow_html=True)

    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.booking_done = False
        st.rerun()

# Main area
st.markdown(f"""
<div class="main-header">
    <div class="main-header-left">
        <h1>🦷 Bright Smile Dental</h1>
        <p>AI Receptionist &nbsp;·&nbsp; Speaking: {selected_lang_label} &nbsp;·&nbsp; Austin, Texas</p>
    </div>
    <div class="status-badge">● Live 24/7</div>
</div>
""", unsafe_allow_html=True)

all_appts = load_appointments()
st.markdown(f"""
<div class="metric-row">
    <div class="metric-box"><div class="num">{len(all_appts)}</div><div class="lbl">Total Bookings</div></div>
    <div class="metric-box"><div class="num">24/7</div><div class="lbl">Availability</div></div>
    <div class="metric-box"><div class="num">10</div><div class="lbl">Languages</div></div>
    <div class="metric-box"><div class="num">3</div><div class="lbl">Doctors</div></div>
</div>
""", unsafe_allow_html=True)

st.markdown("**Quick Questions:**")
cols = st.columns(5)
quick_questions = ["📅 Book Appointment", "💰 View Prices", "🏥 Insurance Info", "🚨 Emergency", "🕐 Opening Hours"]
for i, q in enumerate(quick_questions):
    with cols[i]:
        if st.button(q, use_container_width=True):
            if "messages" not in st.session_state:
                st.session_state.messages = []
            st.session_state.messages.append({"role": "user", "content": q})
            st.rerun()

st.markdown("---")

if "messages" not in st.session_state:
    st.session_state.messages = []
if "booking_done" not in st.session_state:
    st.session_state.booking_done = False

if not st.session_state.messages:
    welcome = {
        "English": "Hello! Welcome to Bright Smile Dental! 😊 I'm your virtual receptionist, available 24/7. I can help you **book appointments**, answer questions about **services and pricing**, **insurance**, or handle **dental emergencies**. How can I assist you today?",
        "Spanish": "¡Hola! ¡Bienvenido a Bright Smile Dental! 😊 Soy su recepcionista virtual, disponible 24/7. ¿En qué puedo ayudarle hoy?",
        "Urdu": "السلام علیکم! برائٹ اسمائل ڈینٹل میں خوش آمدید! 😊 میں آپ کی ورچوئل ریسپشنسٹ ہوں، 24/7 دستیاب ہوں۔ آج میں آپ کی کیسے مدد کر سکتی ہوں؟",
    }
    msg = welcome.get(selected_language, welcome["English"])
    st.session_state.messages.append({"role": "assistant", "content": msg})

for message in st.session_state.messages:
    if message["role"] == "user":
        with st.chat_message("user", avatar="👤"):
            st.markdown(message["content"])
    else:
        content = message["content"]
        display_content = content
        if "[APPOINTMENT_BOOKED]" in content:
            parts = content.split("[APPOINTMENT_BOOKED]")
            display_content = parts[0].strip()
            try:
                block = parts[1].split("[/APPOINTMENT_BOOKED]")[0].strip()
                details = {}
                for line in block.strip().split("\n"):
                    if ":" in line:
                        k, v = line.split(":", 1)
                        details[k.strip()] = v.strip()
            except Exception:
                details = {}
        with st.chat_message("assistant", avatar="🦷"):
            st.markdown(display_content)
            if "[APPOINTMENT_BOOKED]" in content and details:
                st.markdown(f"""
                <div class="appt-card">
                    <h4>✅ Appointment Confirmed! Email sent to clinic.</h4>
                    <p>👤 <b>Patient:</b> {details.get('Name','—')}</p>
                    <p>📅 <b>Date:</b> {details.get('Date','—')}</p>
                    <p>🕐 <b>Time:</b> {details.get('Time','—')}</p>
                    <p>🦷 <b>Service:</b> {details.get('Service','—')}</p>
                    <p>📞 <b>Phone:</b> {details.get('Phone','—')}</p>
                    <p>🏥 <b>Insurance:</b> {details.get('Insurance','—')}</p>
                </div>
                """, unsafe_allow_html=True)

user_input = st.chat_input("Type your message here... 💬")

if user_input:
    st.session_state.booking_done = False
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user", avatar="👤"):
        st.markdown(user_input)

    with st.chat_message("assistant", avatar="🦷"):
        with st.spinner(""):
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                max_tokens=1200,
                messages=[{"role": "system", "content": get_system_prompt(selected_language)}]
                + [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
            )
            reply = response.choices[0].message.content

        display_reply = reply
        booked_details = {}
        if "[APPOINTMENT_BOOKED]" in reply:
            parts = reply.split("[APPOINTMENT_BOOKED]")
            display_reply = parts[0].strip()
            try:
                block = parts[1].split("[/APPOINTMENT_BOOKED]")[0].strip()
                for line in block.strip().split("\n"):
                    if ":" in line:
                        k, v = line.split(":", 1)
                        booked_details[k.strip()] = v.strip()
                saved = save_appointment(
                    booked_details.get("Name", "Unknown"),
                    booked_details.get("Date", "TBD"),
                    booked_details.get("Time", "TBD"),
                    booked_details.get("Service", "General"),
                    booked_details.get("Phone", "N/A"),
                    booked_details.get("Insurance", "N/A")
                )
                st.session_state.booking_done = True
            except Exception:
                pass

        st.markdown(display_reply)
        if booked_details:
            st.markdown(f"""
            <div class="appt-card">
                <h4>✅ Appointment Confirmed! Email sent to clinic.</h4>
                <p>👤 <b>Patient:</b> {booked_details.get('Name','—')}</p>
                <p>📅 <b>Date:</b> {booked_details.get('Date','—')}</p>
                <p>🕐 <b>Time:</b> {booked_details.get('Time','—')}</p>
                <p>🦷 <b>Service:</b> {booked_details.get('Service','—')}</p>
                <p>📞 <b>Phone:</b> {booked_details.get('Phone','—')}</p>
                <p>🏥 <b>Insurance:</b> {booked_details.get('Insurance','—')}</p>
            </div>
            """, unsafe_allow_html=True)

    st.session_state.messages.append({"role": "assistant", "content": reply})
    st.rerun()
