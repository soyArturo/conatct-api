from fastapi import FastAPI, Form
from email_validator import validate_email, EmailNotValidError
from dotenv import load_dotenv
import resend
import os
import requests

load_dotenv()

app = FastAPI()

# Configuración de Resend
resend.api_key = os.getenv("RESEND_API_KEY")
DESTINATARIO = os.getenv("DESTINATARIO")
RECAPTCHA_SECRET = os.getenv("RECAPTCHA_SECRET")


@app.post("/enviar-correo/")
async def enviar_correo(
    nombre: str = Form(...),
    correo: str = Form(...),
    telefono: str = Form(...),
    motivo: str = Form(...),
    captcha_token: str = Form(...),
):
    """Envía correo usando Resend API"""

    recaptcha_response = requests.post(
        "https://www.google.com/recaptcha/api/siteverify",
        data={
            "secret": RECAPTCHA_SECRET,
            "response": captcha_token
        }
    )
    result = recaptcha_response.json()

    if not result.get("success", False):
        return {"status": "error", "message": "CAPTCHA inválido. Intenta de nuevo."}

    # Validar correo
    try:
        validate_email(correo)
    except EmailNotValidError as e:
        return {"status": "error", "message": f"Correo inválido: {str(e)}"}

    html_content = f"""
    <html>
        <body style="font-family: Arial, sans-serif; color: #333;">
            <h2>Nuevo mensaje de contacto</h2>
            <p><strong>Nombre:</strong> {nombre}</p>
            <p><strong>Correo:</strong> {correo}</p>
            <p><strong>Teléfono:</strong> {telefono}</p>
            <p><strong>Motivo:</strong></p>
            <blockquote style="border-left: 3px solid #ccc; padding-left: 10px;">
                {motivo}
            </blockquote>
        </body>
    </html>
    """

    try:
        params = {
            "from": "Formulario Natzen <servicios@natzen.mx>",
            "to": [DESTINATARIO],
            "reply_to": correo,
            "subject": f"Nuevo contacto de {nombre}",
            "html": html_content
        }

        resend.Emails.send(params)
        return {"status": "success", "message": "Correo enviado correctamente"}

    except Exception as e:
        return {"status": "error", "message": str(e)}
