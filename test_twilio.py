from dotenv import load_dotenv
import os
from twilio.rest import Client

# Cargar variables de entorno
load_dotenv()

# Obtener credenciales
account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
twilio_number = "+18125625570"

# Crear cliente de Twilio
client = Client(account_sid, auth_token)

# Verificar la cuenta
try:
    account = client.api.accounts(account_sid).fetch()
    print(f"✅ Conexión exitosa con Twilio")
    print(f"Tipo de cuenta: {account.type}")
    print(f"Estado: {account.status}")

    # Obtener información del número
    number = client.incoming_phone_numbers.list(phone_number=twilio_number)[0]
    print(f"\nInformación del número:")
    print(f"Número: {number.phone_number}")
    print(f"Capacidades: {number.capabilities}")

except Exception as e:
    print(f"❌ Error: {str(e)}")
