import os
from groq import Groq

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
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

Always be friendly and professional. If someone wants to book an appointment ask for their name, preferred date and time, and what service they need.
"""

conversation_history = []

print("Bright Smile Dental - AI Receptionist")
print("Type 'quit' to exit")
print("-" * 40)

while True:
    user_input = input("You: ")

    if user_input.lower() == "quit":
        print("Goodbye! Have a great day!")
        break

    conversation_history.append({
        "role": "user",
        "content": user_input
    })

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        max_tokens=1000,
        messages=[
            {"role": "system", "content": system_prompt}
        ] + conversation_history
    )

    reply = response.choices[0].message.content

    conversation_history.append({
        "role": "assistant",
        "content": reply
    })

    print(f"Receptionist: {reply}")
    print()