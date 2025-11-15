import os

import random
from datetime import datetime
from fastapi import FastAPI, Depends, Form
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session
from twilio.twiml.messaging_response import MessagingResponse
from database import Base, engine, get_db
from models import User

# -----------------------
# DB setup: create tables
# -----------------------
Base.metadata.create_all(bind=engine)

app = FastAPI()

# -----------------------
# Helpers
# -----------------------


def generate_otp() -> str:
    """Generate a 6-digit zero-padded OTP as a string."""
    return f"{random.randint(0, 999999):06d}"


def send_verification_email(emory_email: str, code: str):
    """
    Stub for sending the email containing the OTP code.
    Replace this with real email sending (SMTP, SendGrid, SES, etc.).
    For now, just log it so you can see it in dev.
    """
    print(f"[DEBUG] Would send verification email to {emory_email} with code: {code}")
    # Example (pseudo):
    # import smtplib
    # smtp = smtplib.SMTP(os.getenv("SMTP_HOST"), 587)
    # smtp.login(os.getenv("SMTP_USER"), os.getenv("SMTP_PASS"))
    # msg = f"Subject: TrypSync Verification Code\n\nYour code is {code}"
    # smtp.sendmail(os.getenv("FROM_EMAIL"), [emory_email], msg)
    # smtp.quit()


# -----------------------
# Twilio SMS webhook
# -----------------------


@app.post("/sms", response_class=PlainTextResponse)
async def sms_webhook(
    From: str = Form(...),   # Twilio sends "From" as the sender's phone number
    Body: str = Form(""),    # Twilio sends "Body" as the message text
    db: Session = Depends(get_db),
):
    from_number = From.strip()
    body = (Body or "").strip()
    resp = MessagingResponse()

    # 1) Get or create user by phone number.
    user = db.query(User).filter(User.phone_number == from_number).one_or_none()
    if user is None:
        user = User(
            phone_number=from_number,
            is_verified=False,
            emory_email=None,
            otp_code=None,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    # 2) Onboarding / verification flow
    if not user.is_verified:
        # CASE A: We don't know their Emory email yet → treat this message as the email "keyword"
        if user.emory_email is None:
            em = body.strip().lower()
            if not em.endswith("@emory.edu"):
                resp.message(
                    "Welcome to TrypSync! To use this service, reply with your "
                    "Emory email ending in @emory.edu.\n"
                    "Example: akhil.arularasu@emory.edu"
                )
                return str(resp)

            # Save email & generate OTP
            user.emory_email = em
            code = generate_otp()
            user.otp_code = code
            db.commit()

            # Send the verification code to their Emory email (NOT via SMS)
            send_verification_email(user.emory_email, code)

            resp.message(
                f"Thanks! We sent a 6-digit code to {user.emory_email}. "
                "Reply with that code here to verify your account."
            )
            return str(resp)

        # CASE B (simplified): Email is known, expecting this SMS to be the OTP.
        # No separate regeneration branch; this keeps state logic tight.
        if body == (user.otp_code or ""):
            user.is_verified = True
            user.otp_code = None  # clear OTP after success
            db.commit()
            resp.message(
                "You're verified ✅ as an Emory student. From now on, just text us "
                "your ride requests from Emory to ATL airport.\n\n"
                "Example: '8:30pm, 3 people'."
            )
            return str(resp)
        else:
            resp.message(
                "That code is incorrect. Please reply with the 6-digit code we sent "
                f"to {user.emory_email}."
            )
            return str(resp)

    # 3) Already verified → treat SMS as ride request (for now: placeholder)
    #    Later, you'll parse `body` into requested_time + party_size and write a RideRequest row.
    resp.message(
        "You're already verified ✅. "
        "Send your ride request like: '8:30pm, 3 people' and we'll match you."
    )
    return str(resp)

