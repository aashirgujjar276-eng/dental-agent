import streamlit as st
from groq import Groq

import os
client = Groq(api_key=os.environ.get("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"))
system_prompt = """
You are a friendly receptionist for Bright Smile Dental clinic located at 123 Oak Street, Austin, Texas.

HOURS:
- Monday to Friday: 8am - 6pm
- Saturday: 9am - 2pm
- Sunday: Closed

SERVICES AND PRICES:
- Routine Cleaning: $120
- Dental Exam: $80
- Teeth Whitening: $299
- Tooth Filling: $150-250
- Root Canal: $800-1200
- Tooth Extraction: $200-350
- Dental Implant: $1500-3000
- Braces Consultation: Free

DOCTORS:
- Dr. Sarah Mitchell - General Dentist
- Dr. James Patel - Orthodontist

INSURANCE ACCEPTED:
- Delta Dental, Cigna, Aetna, BlueCross BlueShield, United Healthcare, Medicaid (limited)

CANCELLATION POLICY:
- Cancel at least 24 hours before appointment
- Late cancellation fee: $50

GENERAL INFO:
- Walk ins accepted but appointments preferred
- Emergency appointments available
- Free parking on site
- Phone: (512) 555-0198

Always be friendly and professional. If someone wants to book an appointment ask for their name, preferred date and time, and what service they need. After collecting all details say "Your appointment has been booked successfully!"
"""

st.set_page_config(page_title="Bright Smile Dental", page_icon="🦷")

st.title("🦷 Bright Smile Dental")
st.caption("AI Receptionist - Available 24/7")

if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({
        "role": "assistant",
        "content": "Hello! Welcome to Bright Smile Dental! 😊 How can I help you today? I can help you book an appointment, answer questions about our services, or provide information about our clinic."
    })

for message in st.session_state.messages:
    if message["role"] == "user":
        with st.chat_message("user"):
            st.write(message["content"])
    else:
        with st.chat_message("assistant", avatar="🦷"):
            st.write(message["content"])

user_input = st.chat_input("Type your message here...")

if user_input:
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    with st.chat_message("user"):
        st.write(user_input)

    conversation = [m for m in st.session_state.messages if m["role"] != "system"]

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        max_tokens=1000,
        messages=[
            {"role": "system", "content": system_prompt}
        ] + conversation
    )

    reply = response.choices[0].message.content

    st.session_state.messages.append({
        "role": "assistant",
        "content": reply
    })

    with st.chat_message("assistant", avatar="🦷"):
        st.write(reply)