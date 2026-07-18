import streamlit as st
import os
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, date
import gspread
from google.oauth2.service_account import Credentials
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
[data-testid="stSidebar"] * { color: #ffffff !important; }
[data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] { background: white !important; }
[data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] * { color: #000000 !important; }
[data-testid="stSidebar"] .stButton button { background: rgba(255,255,255,0.15) !important; color: #ffffff !important; border: 1px solid rgba(255,255,255,0.3) !important; }
[data-testid="stSidebar"] .stButton button * { color: #ffffff !important; }
[data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] div { color: #ffffff !important; }
.sidebar-logo { text-align: center; padding: 24px 16px 16px; border-bottom: 1px solid rgba(255,255,255,0.2); margin-bottom: 20px; }
.sidebar-logo h1 { font-family: 'Playfair Display', serif; font-size: 1.5rem; color: #ffffff !important; margin: 8px 0 4px; }
.sidebar-logo p { font-size: 0.75rem; color: #90caf9 !important; margin: 0; }
.info-card { background: rgba(255,255,255,0.1); border: 1px solid rgba(255,255,255,0.2); border-radius: 12px; padding: 14px 16px; margin-bottom: 12px; }
.info-card h4 { font-size: 0.7rem; text-transform: uppercase; letter-spacing: 1px; color: #90caf9 !important; margin: 0 0 8px; }
.info-card p { font-size: 0.82rem; margin: 3px 0; color: #ffffff !important; }
.service-pill { display: inline-block; background: rgba(33,150,243,0.3); border: 1px solid rgba(33,150,243,0.5); border-radius: 20px; padding: 3px 10px; font-size: 0.75rem; margin: 3px 2px; color: #ffffff !important; }
.appt-card-sidebar { background: rgba(255,255,255,0.15); border: 1px solid rgba(255,255,255,0.25); border-radius: 10px; padding: 12px; margin-bottom: 8px; }
.appt-card-sidebar h4 { color: #ffffff !important; margin: 0 0 6px; font-size: 0.85rem; }
.appt-card-sidebar p { color: #e0e0e0 !important; margin: 2px 0; font-size: 0.78rem; }
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
.receipt { background: white; border: 2px solid #0a2540; border-radius: 12px; padding: 24px; margin-top: 12px; }
.receipt h3 { color: #0a2540; border-bottom: 1px solid #e3e8ef; padding-bottom: 8px; margin-bottom: 12px; }
.receipt p { color: #333; margin: 4px 0; font-size: 0.85rem; }
footer { visibility: hidden; }
#MainMenu { visibility: hidden; }
@media (prefers-color-scheme: dark) {
    [data-testid="stAppViewContainer"] { background: #1a1a2e !important; }
    .main-header { background: linear-gradient(135deg, #0a2540 0%, #1565c0 100%) !important; }
    .metric-box { background: #16213e !important; border-color: #0f3460 !important; }
    .metric-box .num { color: #e0e0e0 !important; }
    .metric-box .lbl { color: #90caf9 !important; }
    .appt-card { background: #16213e !important; border-color: #0f3460 !important; }
    .appt-card h4 { color: #90caf9 !important; }
    .appt-card p { color: #e0e0e0 !important; }
    .receipt { background: #16213e !important; border-color: #0f3460 !important; }
    .receipt h3 { color: #90caf9 !important; }
    .receipt p { color: #e0e0e0 !important; }
    [data-testid="stChatMessage"] { background: #16213e !important; }
    .stChatInputContainer { background: #16213e !important; border-color: #0f3460 !important; }
    p, span, div, h1, h2, h3, h4 { color: #e0e0e0; }
}
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

def check_double_booking(date_str, time_str):
    appts = load_appointments()
    for a in appts:
        if a.get("status","") != "Cancelled" and a.get("date","").lower() == date_str.lower() and a.get("time","").lower() == time_str.lower():
            return True
    return False

def send_email_notification(appt):
    sender_email = os.environ.get("SENDER_EMAIL")
    sender_password = os.environ.get("SENDER_PASSWORD")
    dentist_email = os.environ.get("DENTIST_EMAIL")
    if not all([sender_email, sender_password, dentist_email]):
        return False
    try:
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
Receipt ID   : BSDA-{appt['id']:04d}
— Bright Smile Dental AI Receptionist
"""
        msg.attach(MIMEText(body, "plain"))
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, dentist_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        st.warning(f"Email note: {str(e)}")
        return False

def send_cancellation_email(appt):
    sender_email = os.environ.get("SENDER_EMAIL")
    sender_password = os.environ.get("SENDER_PASSWORD")
    dentist_email = os.environ.get("DENTIST_EMAIL")
    if not all([sender_email, sender_password, dentist_email]):
        return False
    try:
        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = dentist_email
        msg["Subject"] = f"❌ Appointment Cancelled — {appt['name']}"
        body = f"""
Appointment Cancellation Notice
================================
Patient Name : {appt['name']}
Date         : {appt['date']}
Time         : {appt['time']}
Service      : {appt['service']}
Phone        : {appt['phone']}
Cancelled At : {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
— Bright Smile Dental AI Receptionist
"""
        msg.attach(MIMEText(body, "plain"))
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, dentist_email, msg.as_string())
        server.quit()
        return True
    except Exception:
        return False

def save_to_sheets(appt):
    try:
        creds_json = os.environ.get("GOOGLE_SHEETS_CREDS")
        sheet_id = os.environ.get("GOOGLE_SHEET_ID")
        if not creds_json or not sheet_id:
            return False
        import json as json_module
        creds_dict = json_module.loads(creds_json)
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
        gc = gspread.authorize(creds)
        sh = gc.open_by_key(sheet_id)
        ws = sh.sheet1
        if ws.cell(1,1).value != "ID":
            headers = ["ID","Patient Name","Date","Time","Service","Phone","Insurance","Booked At","Status"]
            ws.update('A1:I1', [headers])
            ws.format('A1:I1', {
                "backgroundColor": {"red": 0.04, "green": 0.15, "blue": 0.25},
                "textFormat": {"foregroundColor": {"red": 1, "green": 1, "blue": 1}, "bold": True, "fontSize": 11},
                "horizontalAlignment": "CENTER"
            })
            requests = {"requests": [
                {"updateDimensionProperties": {"range": {"sheetId": 0, "dimension": "COLUMNS", "startIndex": i, "endIndex": i+1}, "properties": {"pixelSize": s}, "fields": "pixelSize"}}
                for i, s in enumerate([50,160,120,100,180,130,150,160,100])
            ]}
            sh.batch_update(requests)
        row_num = len(ws.get_all_values()) + 1
        ws.append_row([appt['id'], appt['name'], appt['date'], appt['time'], appt['service'], appt['phone'], appt['insurance'], appt['booked_at'], appt['status']])
        if row_num % 2 == 0:
            ws.format(f'A{row_num}:I{row_num}', {"backgroundColor": {"red": 0.9, "green": 0.95, "blue": 1.0}})
        ws.format(f'I{row_num}', {"backgroundColor": {"red": 0.7, "green": 0.95, "blue": 0.7}, "textFormat": {"bold": True, "foregroundColor": {"red": 0, "green": 0.4, "blue": 0}}})
        return True
    except Exception:
        return False

def update_sheet_cancelled(appt):
    try:
        creds_json = os.environ.get("GOOGLE_SHEETS_CREDS")
        sheet_id = os.environ.get("GOOGLE_SHEET_ID")
        if not creds_json or not sheet_id:
            return False
        import json as json_module
        creds_dict = json_module.loads(creds_json)
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
        gc = gspread.authorize(creds)
        sh = gc.open_by_key(sheet_id)
        ws = sh.sheet1
        cell = ws.find(appt['name'])
        if cell:
            row = cell.row
            ws.update_cell(row, 9, "Cancelled")
            ws.format(f'I{row}', {"backgroundColor": {"red": 1.0, "green": 0.7, "blue": 0.7}, "textFormat": {"bold": True, "foregroundColor": {"red": 0.6, "green": 0, "blue": 0}}})
            ws.format(f'A{row}:H{row}', {"backgroundColor": {"red": 1.0, "green": 0.9, "blue": 0.9}})
        return True
    except Exception:
        return False

def save_appointment(name, date_str, time_str, service, phone="N/A", insurance="N/A"):
    appts = load_appointments()
    appt = {
        "id": len(appts) + 1,
        "name": name,
        "date": date_str,
        "time": time_str,
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
    save_to_sheets(appt)
    return appt

def cancel_appointment(name, date_str):
    appts = load_appointments()
    cancelled = False
    cancelled_appt = None
    for a in appts:
        if a.get("name","").lower() == name.lower() and a.get("status","") != "Cancelled":
            a["status"] = "Cancelled"
            cancelled = True
            cancelled_appt = a
            break
    if cancelled and cancelled_appt:
        with open(APPT_FILE, "w") as f:
            json.dump(appts, f, indent=2)
        send_cancellation_email(cancelled_appt)
        update_sheet_cancelled(cancelled_appt)
    return cancelled

def generate_receipt(appt):
    return f"""
BRIGHT SMILE DENTAL
123 Oak Street, Austin, Texas 78701
Phone: (512) 555-0198
=====================================
APPOINTMENT RECEIPT
Receipt ID : BSDA-{appt['id']:04d}
=====================================
Patient    : {appt['name']}
Date       : {appt['date']}
Time       : {appt['time']}
Service    : {appt['service']}
Phone      : {appt['phone']}
Insurance  : {appt['insurance']}
Booked At  : {appt['booked_at']}
Status     : CONFIRMED
=====================================
Please arrive 15 minutes early.
Bring your insurance card and ID.
Cancellation: 24hrs notice required.
Thank you for choosing Bright Smile!
=====================================
"""

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
- Sunday: CLOSED

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
- Invisalign Consultation: FREE
- Invisalign Treatment: $3,000-$6,000
- Emergency Dental Visit: $150
- X-Rays (full set): $150
- Pediatric Exam & Cleaning: $90
- Fluoride Treatment: $35
- Dental Sealants: $40 per tooth

INSURANCE ACCEPTED:
Delta Dental, Cigna, Aetna, BlueCross BlueShield, United Healthcare, Humana, Guardian, MetLife, Medicaid (limited)

PAYMENT OPTIONS:
Cash, all major credit/debit cards, CareCredit financing (0% interest), payment plans for treatments over $500

CANCELLATION POLICY:
- Cancel at least 24 hours before appointment
- Late cancellation fee: $50
- No-show fee: $75

GENERAL:
- New patients welcome - arrive 15 min early
- Walk-ins accepted but appointments preferred
- Emergency same-day appointments available
- Free parking, wheelchair accessible, kid-friendly, WiFi

APPOINTMENT BOOKING RULES:
- Clinic is CLOSED on Sundays - never book Sunday appointments
- Saturday hours end at 2:00 PM - no bookings after that
- Do not book appointments in the past
- If a date/time is unavailable due to double booking, suggest alternatives
- Collect: full name, date, time, service, phone number, insurance
- After collecting ALL 6 details, summarize them and ask patient "Is all this information correct? Please reply YES to confirm or NO to make changes."
- ONLY after patient replies YES, output the booking block
- If patient says NO, ask what they want to change
- Once patient confirms with YES, end message with EXACT block:

[APPOINTMENT_BOOKED]
Name: <name>
Date: <date>
Time: <time>
Service: <service>
Phone: <phone>
Insurance: <insurance>
[/APPOINTMENT_BOOKED]

APPOINTMENT CANCELLATION:
- If patient wants to cancel, ask for their full name
- Confirm the cancellation with patient before proceeding
- Once patient confirms, output this EXACT block:

[APPOINTMENT_CANCELLED]
Name: <name>
Date: <date>
[/APPOINTMENT_CANCELLED]

- After cancellation inform patient of $50 late cancellation fee if less than 24hrs notice
- Be empathetic and offer to rebook for another time

EMERGENCY GUIDANCE:
- Severe toothache: call (512) 555-0199 immediately
- Knocked-out tooth: keep moist, call emergency line NOW
- Broken tooth: rinse, cold compress, call us
- Lost filling/crown: temporary cement from pharmacy, call us

PERSONALITY:
Warm, empathetic, professional. Use patient name once known.
Emojis occasionally. Concise but complete. Never make up info.
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
    st.markdown('<div class="info-card"><h4>🕐 Hours</h4><p>Mon-Fri: 8am - 6pm</p><p>Saturday: 9am - 2pm</p><p style="color:#ff6b6b !important">Sunday: Closed</p></div>', unsafe_allow_html=True)
    st.markdown('<div class="info-card"><h4>📞 Contact</h4><p>Main: (512) 555-0198</p><p>Emergency: (512) 555-0199</p></div>', unsafe_allow_html=True)
    st.markdown('<div class="info-card"><h4>🩺 Doctors</h4><p>Dr. Sarah Mitchell – General</p><p>Dr. James Patel – Orthodontist</p><p>Dr. Emily Nguyen – Pediatric</p></div>', unsafe_allow_html=True)

    st.markdown('<div class="info-card"><h4>✅ Insurance</h4>', unsafe_allow_html=True)
    for ins in ["Delta Dental", "Cigna", "Aetna", "BlueCross", "United", "Humana", "Medicaid"]:
        st.markdown(f'<span class="service-pill">{ins}</span>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<p style="font-size:0.78rem;color:#90caf9 !important;text-transform:uppercase;letter-spacing:1px">🌐 Language</p>', unsafe_allow_html=True)
    selected_lang_label = st.selectbox("Select Language", list(LANGUAGES.keys()), label_visibility="collapsed", key="lang_select")
    selected_language = LANGUAGES[selected_lang_label]
    st.markdown("---")

    st.markdown('<p style="color:#ffffff !important;font-weight:600">📋 Appointments Today</p>', unsafe_allow_html=True)
    appts = load_appointments()
    today = datetime.now().strftime("%Y-%m-%d")
    today_appts = [a for a in appts if today in str(a.get("booked_at", ""))]
    if today_appts:
        for a in today_appts[-3:]:
            if a.get("status","") == "Cancelled":
                st.markdown(f"""
                <div style="background:rgba(255,100,100,0.2);border:1px solid rgba(255,100,100,0.4);border-radius:10px;padding:12px;margin-bottom:8px">
                    <h4 style="color:#ff6b6b !important;margin:0 0 6px;font-size:0.85rem">❌ {a['name']} (Cancelled)</h4>
                    <p style="color:#ffaaaa !important;margin:2px 0;font-size:0.78rem">📅 {a['date']} at {a['time']}</p>
                    <p style="color:#ffaaaa !important;margin:2px 0;font-size:0.78rem">🦷 {a['service']}</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="appt-card-sidebar">
                    <h4>✅ {a['name']}</h4>
                    <p>📅 {a['date']} at {a['time']}</p>
                    <p>🦷 {a['service']}</p>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.markdown('<p style="font-size:0.8rem;color:#90caf9 !important">No appointments today yet.</p>', unsafe_allow_html=True)

    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.booking_done = False
        st.session_state.last_appt = None
        st.session_state.last_cancelled = None
        st.session_state.pop("trigger_response", None)
        st.rerun()

# Admin Dashboard
if st.sidebar.button("🔐 Admin Dashboard", use_container_width=True):
    st.session_state["show_admin"] = not st.session_state.get("show_admin", False)

if st.session_state.get("show_admin", False):
    admin_pass = st.text_input("Enter admin password:", type="password", key="admin_pw")
    if admin_pass == os.environ.get("ADMIN_PASSWORD", "admin123"):
        st.success("✅ Access granted")
        if st.button("🏠 Go Back to Home"):
            st.session_state["show_admin"] = False
            st.rerun()
        all_appts = load_appointments()
        if all_appts:
            st.subheader("📋 All Appointments")
            import pandas as pd
            df = pd.DataFrame(all_appts)
            st.dataframe(df, use_container_width=True)
            csv = df.to_csv(index=False)
            st.download_button("⬇️ Download CSV", csv, "appointments.csv", "text/csv")
        else:
            st.info("No appointments yet.")
        st.stop()
    elif admin_pass:
        st.error("Wrong password")
        st.stop()
    else:
        st.stop()

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
confirmed_appts = [a for a in all_appts if a.get("status","") != "Cancelled"]
st.markdown(f"""
<div class="metric-row">
    <div class="metric-box"><div class="num">{len(confirmed_appts)}</div><div class="lbl">Total Bookings</div></div>
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
        if st.button(q, use_container_width=True, key=f"quick_{i}"):
            if "messages" not in st.session_state:
                st.session_state.messages = []
            clean_q = q.split(" ", 1)[1] if " " in q else q
            st.session_state["trigger_response"] = clean_q
            st.rerun()

st.markdown("---")

if "messages" not in st.session_state:
    st.session_state.messages = []
if "booking_done" not in st.session_state:
    st.session_state.booking_done = False
if "last_appt" not in st.session_state:
    st.session_state.last_appt = None
if "last_cancelled" not in st.session_state:
    st.session_state.last_cancelled = None

if not st.session_state.messages:
    welcome = {
        "English": "Hello! Welcome to Bright Smile Dental! 😊 I'm your virtual receptionist, available 24/7. I can help you **book appointments**, answer questions about **services and pricing**, **insurance**, or handle **dental emergencies**. How can I assist you today?",
        "Spanish": "¡Hola! ¡Bienvenido a Bright Smile Dental! 😊 Soy su recepcionista virtual, disponible 24/7. ¿En qué puedo ayudarle hoy?",
        "French": "Bonjour! Bienvenue chez Bright Smile Dental! 😊 Je suis votre réceptionniste virtuelle. Comment puis-je vous aider?",
        "Urdu": "السلام علیکم! برائٹ اسمائل ڈینٹل میں خوش آمدید! 😊 میں آپ کی ورچوئل ریسپشنسٹ ہوں۔ آج میں آپ کی کیسے مدد کر سکتی ہوں؟",
        "Arabic": "مرحباً! أهلاً بكم في عيادة برايت سمايل للأسنان! 😊 أنا موظفة الاستقبال الافتراضية، متاحة على مدار الساعة. كيف يمكنني مساعدتك؟",
        "German": "Hallo! Willkommen bei Bright Smile Dental! 😊 Ich bin Ihre virtuelle Empfangsdame. Wie kann ich Ihnen helfen?",
        "Chinese": "您好！欢迎来到Bright Smile牙科诊所！😊 我是您的虚拟接待员，24/7为您服务。今天我能为您做什么？",
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
        booked_details = {}
        cancelled_hist = {}

        if "[APPOINTMENT_BOOKED]" in content:
            parts = content.split("[APPOINTMENT_BOOKED]")
            display_content = parts[0].strip()
            try:
                block = parts[1].split("[/APPOINTMENT_BOOKED]")[0].strip()
                for line in block.strip().split("\n"):
                    if ":" in line:
                        k, v = line.split(":", 1)
                        booked_details[k.strip()] = v.strip()
            except Exception:
                pass

        if "[APPOINTMENT_CANCELLED]" in content:
            display_content = content.split("[APPOINTMENT_CANCELLED]")[0].strip()
            try:
                cblock = content.split("[APPOINTMENT_CANCELLED]")[1].split("[/APPOINTMENT_CANCELLED]")[0].strip()
                for line in cblock.strip().split("\n"):
                    if ":" in line:
                        k, v = line.split(":", 1)
                        cancelled_hist[k.strip()] = v.strip()
            except Exception:
                pass

        with st.chat_message("assistant", avatar="🦷"):
            st.markdown(display_content)
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
            if cancelled_hist:
                st.markdown(f"""
                <div style="background:#fff0f0;border:2px solid #ef9a9a;border-radius:12px;padding:16px;margin-top:12px">
                    <h4 style="color:#c62828;margin:0 0 8px;font-size:1rem">❌ Appointment Cancelled</h4>
                    <p style="color:#b71c1c;margin:3px 0">👤 <b>Patient:</b> {cancelled_hist.get('Name','—')}</p>
                    <p style="color:#b71c1c;margin:3px 0">📅 <b>Date:</b> {cancelled_hist.get('Date','—')}</p>
                    <p style="color:#b71c1c;margin:3px 0">📧 Cancellation email sent to clinic</p>
                    <p style="color:#b71c1c;margin:3px 0">📊 Google Sheet updated to Cancelled</p>
                </div>
                """, unsafe_allow_html=True)

if st.session_state.get("last_appt") and not st.session_state.get("last_cancelled"):
    receipt_text = generate_receipt(st.session_state.last_appt)
    st.download_button(
        label="⬇️ Download Appointment Receipt",
        data=receipt_text,
        file_name=f"receipt_BSDA_{st.session_state.last_appt['id']:04d}.txt",
        mime="text/plain",
        key="receipt_dl"
    )
elif st.session_state.get("last_cancelled"):
    cancel_receipt = f"""
BRIGHT SMILE DENTAL
123 Oak Street, Austin, Texas 78701
Phone: (512) 555-0198
=====================================
CANCELLATION RECEIPT
=====================================
Patient    : {st.session_state.last_cancelled.get('name','—')}
Date       : {st.session_state.last_cancelled.get('date','—')}
Cancelled  : {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Status     : CANCELLED
=====================================
Late cancellation fee may apply ($50).
To rebook call: (512) 555-0198
Thank you for letting us know.
=====================================
"""
    st.download_button(
        label="⬇️ Download Cancellation Receipt",
        data=cancel_receipt,
        file_name="cancellation_receipt.txt",
        mime="text/plain",
        key="cancel_receipt_dl"
    )

user_input = st.chat_input("Type your message here... 💬")
if not user_input and st.session_state.get("trigger_response"):
    user_input = st.session_state.pop("trigger_response")

if user_input:
    st.session_state.booking_done = False
    st.session_state.last_cancelled = None

    if not any(m["content"] == user_input and m["role"] == "user"
               for m in st.session_state.messages[-2:]):
        st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("user", avatar="👤"):
        st.markdown(user_input)

    with st.chat_message("assistant", avatar="🦷"):
        with st.spinner(""):
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                max_tokens=1200,
                messages=[{"role": "system", "content": get_system_prompt(selected_language)}]
                + [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
            )
            reply = response.choices[0].message.content

        display_reply = reply
        booked_details = {}
        cancelled_details = {}

        if "[APPOINTMENT_BOOKED]" in reply:
            parts = reply.split("[APPOINTMENT_BOOKED]")
            display_reply = parts[0].strip()
            try:
                block = parts[1].split("[/APPOINTMENT_BOOKED]")[0].strip()
                for line in block.strip().split("\n"):
                    if ":" in line:
                        k, v = line.split(":", 1)
                        booked_details[k.strip()] = v.strip()
                double_booked = check_double_booking(booked_details.get("Date",""), booked_details.get("Time",""))
                if double_booked:
                    display_reply += "\n\n⚠️ Sorry, that time slot is already taken. Please choose a different time."
                    booked_details = {}
                else:
                    saved = save_appointment(
                        booked_details.get("Name", "Unknown"),
                        booked_details.get("Date", "TBD"),
                        booked_details.get("Time", "TBD"),
                        booked_details.get("Service", "General"),
                        booked_details.get("Phone", "N/A"),
                        booked_details.get("Insurance", "N/A")
                    )
                    st.session_state.last_appt = saved
                    st.session_state.booking_done = True
            except Exception:
                pass

        elif "[APPOINTMENT_CANCELLED]" in reply:
            parts = reply.split("[APPOINTMENT_CANCELLED]")
            display_reply = parts[0].strip()
            try:
                block = parts[1].split("[/APPOINTMENT_CANCELLED]")[0].strip()
                for line in block.strip().split("\n"):
                    if ":" in line:
                        k, v = line.split(":", 1)
                        cancelled_details[k.strip()] = v.strip()
                success = cancel_appointment(
                    cancelled_details.get("Name", ""),
                    cancelled_details.get("Date", "")
                )
                if success:
                    st.session_state.booking_done = False
                    st.session_state.last_appt = None
                    st.session_state.last_cancelled = {
                        "name": cancelled_details.get("Name","—"),
                        "date": cancelled_details.get("Date","—")
                    }
            except Exception:
                pass

        st.markdown(display_reply)
        if booked_details and not check_double_booking(booked_details.get("Date",""), booked_details.get("Time","")):
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
        if cancelled_details:
            st.markdown(f"""
            <div style="background:#fff0f0;border:2px solid #ef9a9a;border-radius:12px;padding:16px;margin-top:12px">
                <h4 style="color:#c62828;margin:0 0 8px;font-size:1rem">❌ Appointment Cancelled</h4>
                <p style="color:#b71c1c;margin:3px 0">👤 <b>Patient:</b> {cancelled_details.get('Name','—')}</p>
                <p style="color:#b71c1c;margin:3px 0">📅 <b>Date:</b> {cancelled_details.get('Date','—')}</p>
                <p style="color:#b71c1c;margin:3px 0">📧 Cancellation email sent to clinic</p>
                <p style="color:#b71c1c;margin:3px 0">📊 Google Sheet updated to Cancelled</p>
            </div>
            """, unsafe_allow_html=True)

    st.session_state.messages.append({"role": "assistant", "content": reply})
    st.rerun()
