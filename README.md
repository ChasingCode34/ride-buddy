# SMS (Emory Email + OTP)

This is a minimal FastAPI backend that:

- Receives SMS via Twilio
- Uses the sender's phone number as identity
- Verifies that the user is an Emory student via `@emory.edu` email
- Sends a 6-digit verification code to their Emory email
- After verification, allows them to text ride requests (Emory → ATL airport)

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Environment Variables

Create a `.env` file in the project root with your Twilio credentials:

```
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
DATABASE_URL=sqlite:///./trypsync.db  # Optional, defaults to SQLite
```

### 3. Run the server

```bash
uvicorn main:app --reload
```

### 4. Configure Twilio Webhook

In your Twilio Console, set the webhook URL for incoming SMS to:
```
http://your-domain.com/sms
```

#### For Local Development (ngrok)

**Install ngrok on Windows:**

1. **Option A: Download directly**
   - Visit https://ngrok.com/download
   - Download the Windows version
   - Extract the `ngrok.exe` file
   - Add it to your PATH, or run it from the extracted folder

2. **Option B: Using Chocolatey (if installed)**
   ```powershell
   choco install ngrok
   ```

3. **Option C: Using Scoop (if installed)**
   ```powershell
   scoop install ngrok
   ```

**After installing ngrok:**

1. Start your FastAPI server:
   ```bash
   uvicorn main:app --reload
   ```

2. In a new terminal, start ngrok:
   ```bash
   ngrok http 8000
   ```

3. Copy the HTTPS URL from ngrok (e.g., `https://abc123.ngrok.io`)

4. In Twilio Console → Phone Numbers → Your Number → Messaging Configuration:
   - Set the webhook URL to: `https://abc123.ngrok.io/sms`
   - Set HTTP method to: `POST`

**Alternative: Use Twilio CLI (if you prefer)**
```bash
twilio phone-numbers:update +1234567890 --sms-url http://localhost:8000/sms
```

## Usage Flow

1. User texts the Twilio number
2. System prompts for Emory email (@emory.edu)
3. System sends OTP code to the email (currently stubbed - prints to console)
4. User replies with the OTP code
5. User is verified and can send ride requests

## Development Notes

- Email sending is currently stubbed (prints to console). Replace `send_verification_email()` in `main.py` with actual email sending logic.
- The database defaults to SQLite for local development. Set `DATABASE_URL` for production PostgreSQL.
- Ride request parsing is a placeholder - implement parsing logic in the verified user flow.

