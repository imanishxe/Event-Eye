# Event Eye — Certificate Generator

A small Flask app that generates event certificates from a CSV of participants, embeds a QR for verification, and optionally emails the certificate to participants.

## Demo & sending emails

- GitHub: https://github.com/<your-username>/<repo-name>
- Live (Render): https://event-eye-mvfg.onrender.com

On the upload page you can optionally enter the sending email and an "App Password" (for Gmail) — these credentials are used only for that request and are NOT stored in the server.

How to create a Gmail App Password:
1. Go to Google Account → Security → App passwords.
2. Create a password for Mail (choose "Other" for device) and copy the 16-character string.
3. Paste the 16-character app password into the "App password" field on the upload page.

Security note: prefer using a dedicated app password and do not commit credentials to the repo. You can also set SENDER_EMAIL and SENDER_PASSWORD as environment variables on your host (Render) if you want server-global sending without entering credentials each upload.

## Features
- Upload a CSV (Name, Email) to generate certificates using a template image.
- QR code on each certificate that links to a verification route.
- Download generated certificate PDFs from the dashboard.
- (Optional) Email certificates to participants using SMTP.
- Responsive, themed UI (blue/purple/white) and branded header.

## Files of interest
- `app.py` — Flask app and core logic (certificate generation, QR, email sending).
- `template.png` — Certificate template (modify as needed).
- `templates/index.html` — UI for uploading participant lists.
- `templates/dashboard.html` — Delivery status dashboard.
- `static/logo.png` — Branding logo used in the header.
- `certificates/` — Output folder (ignored by `.gitignore`).

## Quick start (Windows / PowerShell)
1. Create a virtual environment and activate it (recommended):

```powershell
python -m venv venv
& .\venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
pip install -r requirements.txt
```

3. Set SMTP credentials (optional if you want to email certificates):

```powershell
# for current PowerShell session
$env:SENDER_EMAIL = 'youremail@gmail.com'
$env:SENDER_PASSWORD = 'your_app_password'
```

> If you use Gmail with 2FA enabled you must create an App Password and use that as `SENDER_PASSWORD`.

4. Run the app:

```powershell
python .\app.py
```

5. Open the site in your browser: http://127.0.0.1:5000 (or use your PC LAN IP if testing QR scanning on a phone).

## Sample CSV format
Create a CSV with headers exactly `Name,Email`:

```csv
Name,Email
Alice Johnson,alice@example.com
Bob Singh,bob@example.com
```

## Notes for demos
- To scan QR codes from your phone, run the server bound to your LAN IP (the app already binds to 0.0.0.0:5000). Use `http://<YOUR_PC_IP>:5000` in the phone's browser.
- If you want to expose the app publicly for remote judges, use a tunneling tool like `ngrok` and pass the public URL when generating certificates.

## Security
- Do NOT commit real credentials to source control. Use environment variables during demos.
- The sample app stores certificates on disk in `certificates/`. Remove sensitive files before sharing the repo publicly.

## License
This project is released under the MIT License — see `LICENSE`.

---

Happy demoing! If you want, I can create a GitHub-friendly `README` screenshot and a short demo GIF next.
