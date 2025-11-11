from fastapi import FastAPI, Form
from aiosmtplib import SMTP
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr
from dotenv import load_dotenv
from email_validator import validate_email, EmailNotValidError
import os

load_dotenv()

app = FastAPI()

# Configuración del correo saliente
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")
DESTINATARIO = os.getenv("DESTINATARIO")


@app.post("/enviar-correo/")
async def enviar_correo(
    nombre: str = Form(...),
    correo: str = Form(...),
    telefono: str = Form(...),
    motivo: str = Form(...)
):
    """
    Endpoint que recibe los datos del formulario de contacto y
    envía un correo
    """

    try:
        valid = validate_email(correo)
        correo_normalizado = valid.email
    except EmailNotValidError as e:
        return {"status": "error", "message": f"Correo inválido: {str(e)}"}

    # Crear el mensaje de correo
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"Nuevo contacto de {nombre}"
    msg["From"] = formataddr(("Formulario de contacto - Natzen", SMTP_USER))
    msg["To"] = DESTINATARIO
    msg["Reply-To"] = correo_normalizado

    # Plantilla HTML del correo
    html_content = f"""
    <html>
        <body style="font-family: Arial, sans-serif; color: #333;">
            <h2>Nuevo mensaje de contacto</h2>
            <p><strong>Nombre:</strong> {nombre}</p>
            <p><strong>Correo:</strong> {correo_normalizado}</p>
            <p><strong>Teléfono:</strong> {telefono}</p>
            <p><strong>Motivo de contacto:</strong></p>
            <blockquote style="border-left: 3px solid #ccc; padding-left: 10px;">
                {motivo}
            </blockquote>
        </body>
    </html>
    """

    msg.attach(MIMEText(html_content, "html"))

    # Enviar el correo
    try:
        async with SMTP(hostname=SMTP_SERVER, port=SMTP_PORT, use_tls=True) as smtp:
            await smtp.login(SMTP_USER, SMTP_PASS)
            await smtp.send_message(msg)
        return {"status": "success", "message": "Correo enviado correctamente"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
