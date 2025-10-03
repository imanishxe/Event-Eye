# STEP 1: ALL IMPORTS GO AT THE TOP 
from flask import Flask, render_template, request, send_from_directory, url_for
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import os
import qrcode
import re
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import uuid

# STEP 2: INITIALIZE THE FLASK WEB APP 
app = Flask(__name__)

# Create a folder to save the certificates if it doesn't exist
if not os.path.exists('certificates'):
    os.makedirs('certificates')

# Utility: sanitize filenames
def _safe_filename(name: str) -> str:
    # Replace spaces and non-filesystem-safe chars
    safe = re.sub(r'[^A-Za-z0-9_.-]', '_', name.strip())
    # Add a short uuid suffix to avoid collisions
    return f"{safe}_{uuid.uuid4().hex[:8]}"


# STEP 3: DEFINE THE CERTIFICATE GENERATION FUNCTION 
def generate_certificate(name: str, event_name: str, date: str, base_url: str = 'http://127.0.0.1:5000') -> str:
    """Generates a single certificate with a QR code and returns the output path.

    Expects `template.png` to exist in the project root. The function will try to
    use common Windows fonts if available; otherwise it will fall back to the default PIL font.
    """
    template_path = 'template.png'

    # Font choices (try common Windows fonts, otherwise revert)
    name_font_path = r"C:\Windows\Fonts\timesbd.ttf"
    other_font_path = r"C:\Windows\Fonts\times.ttf"

    # Create a safe filename
    safe_name = _safe_filename(name)
    output_path = os.path.join('certificates', f"{safe_name}.pdf")

    # Open template
    if not os.path.exists(template_path):
        raise FileNotFoundError(f"Template not found: {template_path}")

    img = Image.open(template_path).convert('RGB')
    draw = ImageDraw.Draw(img)

    # Load fonts with graceful fallback
    try:
        name_font = ImageFont.truetype(name_font_path, 80)
    except Exception:
        try:
            name_font = ImageFont.truetype(other_font_path, 72)
        except Exception:
            name_font = ImageFont.load_default()

    try:
        event_font = ImageFont.truetype(other_font_path, 60)
    except Exception:
        event_font = ImageFont.load_default()

    try:
        date_font = ImageFont.truetype(other_font_path, 45)
    except Exception:
        date_font = ImageFont.load_default()

    # Calculate text widths for centering; support older Pillow versions
    def text_width(text, font):
        try:
            return draw.textlength(text, font=font)
        except Exception:
            w, _ = draw.textsize(text, font=font)
            return w

    img_width, img_height = img.size

    # Center event name near the top
    event_w = text_width(event_name, event_font)
    event_x = int((img_width - event_w) / 2)
    event_y = 140
    draw.text((event_x, event_y), event_name, font=event_font, fill='black')

    # Center participant name (y coordinate tuned for typical templates)
    name_w = text_width(name, name_font)
    name_x = int((img_width - name_w) / 2)
    name_y = 620
    draw.text((name_x, name_y), name, font=name_font, fill='black')

    # Date at fixed coordinates requested by user
    draw.text((1285, 825), date, font=date_font, fill='black')

    # --- QR Code Generation ---
    # base_url should be something like 'http://example.com' or 'http://192.168.1.10:5000'
    if base_url.endswith('/'):
        base_url = base_url[:-1]
    qr_data = f"{base_url}/verify/{safe_name}"
    qr_img = qrcode.make(qr_data)
    # Ensure QR is RGB and appropriately sized
    qr_img = qr_img.convert('RGB').resize((140, 140))

    # Paste QR in the bottom-right corner with some padding
    qr_x = img_width - qr_img.width - 60
    qr_y = img_height - qr_img.height - 40
    img.paste(qr_img, (qr_x, qr_y))

    # Save as PDF (Pillow supports saving an RGB image as PDF)
    img.save(output_path)
    print(f"Generated certificate for {name} -> {output_path}")
    return output_path


# --- Verification route ---
@app.route('/verify/<token>')
def verify(token):
    # token is the safe filename prefix; in a real app you'd map this to a DB record
    participant_name = token.replace('_', ' ')
    return f"<h1>Certificate Verified!</h1><p>This certifies that {participant_name} successfully attended the event.</p>"


# Serve generated certificates (download)
@app.route('/certificates/<path:filename>')
def serve_certificate(filename):
    return send_from_directory('certificates', filename, as_attachment=True)


# Email settings - prefer environment variables for secrets
SENDER_EMAIL = os.getenv('SENDER_EMAIL')
SENDER_PASSWORD = os.getenv('SENDER_PASSWORD')

if not SENDER_EMAIL or not SENDER_PASSWORD:
    print("Warning: SENDER_EMAIL or SENDER_PASSWORD not set as environment variables. Email sending will fail unless these are provided.")


def send_email(recipient_email: str, certificate_path: str) -> str:
    """Sends an email with the certificate attached. Returns 'Sent' or 'Failed'."""
    # Preflight: check credentials
    if not SENDER_EMAIL or not SENDER_PASSWORD:
        msg = f'Failed: missing SMTP credentials (set SENDER_EMAIL and SENDER_PASSWORD environment variables)'
        print(msg)
        return msg

    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = recipient_email
    msg['Subject'] = 'Your Certificate of Completion!'

    body = "Congratulations! Please find your certificate attached."
    msg.attach(MIMEText(body, 'plain'))

    # Attach the file
    try:
        with open(certificate_path, 'rb') as attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename={os.path.basename(certificate_path)}')
        msg.attach(part)
    except Exception as e:
        err = f'Failed: attachment error: {e}'
        print(err)
        return err

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587, timeout=30)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, recipient_email, msg.as_string())
        server.quit()
        print(f"Email sent to {recipient_email}")
        return 'Sent'
    except Exception as e:
        err = f'Failed: SMTP error: {e}'
        print(err)
        return err


# --- Web routes ---
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files.get('participant_file')
    if not file or not file.filename.lower().endswith('.csv'):
        return "Please upload a valid CSV file."

    try:
        participants = pd.read_csv(file)
    except Exception as e:
        return f"Failed to read CSV: {e}"

    required_cols = {'Name', 'Email'}
    if not required_cols.issubset(set(participants.columns)):
        return f"CSV must contain the columns: {', '.join(required_cols)}"

    results = []
    for index, row in participants.iterrows():
        try:
            name = str(row['Name'])
            email = str(row['Email'])
        except Exception as e:
            results.append({'name': None, 'email': None, 'status': f'Row read error: {e}'})
            continue

        # 1) Generate certificate
        try:
            cert_path = generate_certificate(name, 'Hackathon 2025', 'Oct 3, 2025', base_url=request.host_url)
            cert_filename = os.path.basename(cert_path)
            cert_status = 'Generated'
        except Exception as e:
            results.append({'name': name, 'email': email, 'cert_filename': None, 'cert_status': f'Certificate error: {e}', 'email_status': 'Skipped'})
            continue

        # 2) Send email (synchronous). For large batches consider background jobs.
        email_status = send_email(email, cert_path)

        results.append({'name': name, 'email': email, 'cert_filename': cert_filename, 'cert_status': cert_status, 'email_status': email_status})

    return render_template('dashboard.html', results=results)


# --- STEP 4: RUN THE WEB SERVER ---
if __name__ == '__main__':
    # Bind to 0.0.0.0 so mobile devices on the same network can reach the server.
    app.run(host='0.0.0.0', port=5000, debug=True)

