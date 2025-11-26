from fastapi import FastAPI, Form
from fastapi.middleware.cors import CORSMiddleware
from email_validator import validate_email, EmailNotValidError
from dotenv import load_dotenv
from pydantic import BaseModel
import resend
import os
import requests

load_dotenv()

app = FastAPI()

origins = [
    "http://localhost:5173",
    "https://natzen.mx",
    "https://natzen.vercel.app",
    "https://www.natzen.mx"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],   # permite POST, GET, OPTIONS, etc.
    allow_headers=["*"],   # permite todos los headers, incluidos Authorization
)

# Configuración de Resend
resend.api_key = os.getenv("RESEND_API_KEY")
DESTINATARIO = os.getenv("DESTINATARIO")
RECAPTCHA_SECRET = os.getenv("RECAPTCHA_SECRET")


class Contacto(BaseModel):
    nombre: str
    correo: str
    telefono: str
    motivo: str
    captcha_token: str


@app.post("/enviar-correo/")
async def enviar_correo(data: Contacto):
    """Envía correo usando Resend API"""

    nombre = data.nombre
    correo = data.correo
    telefono = data.telefono
    motivo = data.motivo
    captcha_token = data.captcha_token

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
