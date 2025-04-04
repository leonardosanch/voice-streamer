"""
CLI to set ngrok URLs in an available Twilio phone number, for testing.

Requirements:
- Twilio CLI (https://www.twilio.com/docs/twilio-cli/general-usage)
- Environment variables:
    - `TWILIO_ACCOUNT_SID`
    - `TWILIO_AUTH_TOKEN`
    - `NGROK_AUTHTOKEN`
"""

import logging
import subprocess
import time
import os
from pyngrok import ngrok
import click
from dotenv import load_dotenv
from rich.logging import RichHandler
from rich.console import Console

# Configuración inicial
load_dotenv()
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler()],
)
logger = logging.getLogger("rich")
console = Console()

# Constantes
DEFAULT_PROD_URL: str = ""  # Puede quedar vacío para desarrollo
VOICE_ENDPOINT: str = "/twilio/stream/"  # Actualizado según el requerimiento
TESTING_PHONE_NUMBER: str = "+18125625570"  # Tu número de Twilio

def parse_duration(duration_str: str) -> int:
    """Convert duration string to seconds"""
    unit = duration_str[-1].lower()
    value = int(duration_str[:-1])
    
    if unit == 'h':
        return value * 3600
    elif unit == 'm':
        return value * 60
    else:
        return value

def run_command(description: str, command: str, verbose: bool = False) -> None:
    """Run shell command."""
    res = subprocess.run(command.split(), capture_output=True, text=True)
    if res.returncode:
        logger.error("%s\nStderr: %s", description, res.stderr)
        return
    if verbose:
        logger.info("%s\n%s", description, res.stdout)
    return

def show_phone_numbers():
    """Show the voice call URL for all the Twilio phone numbers."""
    run_command(
        description="AVAILABLE PHONE NUMBERS",
        command=(
            "twilio phone-numbers:list "
            "--properties=phoneNumber,friendlyName,voiceUrl"
        ),
        verbose=True,
    )

def set_voice_url(url: str):
    """Update the voice call URL for the Twilio phone number."""
    desc = "SETTING VOICE CALL URL: " + url
    command = (
        f"twilio phone-numbers:update {TESTING_PHONE_NUMBER} "
        f"--voice-url {url + VOICE_ENDPOINT}"
    )
    run_command(desc, command)

def create_ngrok_tunnel(port: int = 8000) -> str:
    """Start a ngrok tunnel to localhost:8000 and return the public URL."""
    logger.info("STARTING NGROK TUNNEL!")
    
    auth_token = os.getenv('NGROK_AUTHTOKEN')
    ngrok.set_auth_token(auth_token)
    
    try:
        ngrok.kill()
        tunnel = ngrok.connect(port)
        public_url = tunnel.public_url
        
        if public_url.startswith('http://'):
            public_url = 'https://' + public_url[7:]
        
        logger.info(f"Tunnel created successfully: {public_url}")
        return public_url
    
    except Exception as e:
        logger.error(f"Error creating tunnel: {str(e)}")
        raise e

@click.group()
def program():
    """CLI to Manage Twilio Voice Services"""

@program.command(name="status")
def twilio_services_status():
    """Show URL currently set in twilio voice service"""
    show_phone_numbers()

@program.command(name="stop")
def twilio_services_stop():
    """Set prod URL back to twilio services"""
    logger.info("SETTING DEFAULT URLS IN TWILIO")
    set_voice_url(DEFAULT_PROD_URL)
    logger.info("DONE!")

@program.command(name="start")
@click.argument("server", nargs=1, default="")
@click.option('--duration', '-d', default='5m', 
              help='Duration with unit (e.g., 1h, 30m, 300s). Default: 5m')
def start_session(server: str, duration: str):
    """
    Create ngrok tunnel and set URL in Twilio voice service.
    Keep session running until Ctrl+C is pressed.
    
    Options:
        --duration, -d: Duration with unit (e.g., 1h, 30m, 300s). Default: 5m
    """
    try:
        ngrok_url = create_ngrok_tunnel() if not server else server
        set_voice_url(ngrok_url)
        show_phone_numbers()
        duration_seconds = parse_duration(duration)
        while True:
            logger.info(f"KEEPING THE TUNNEL OPEN FOR {duration_seconds/60:.1f} MINUTES!")
            time.sleep(duration_seconds)
    except KeyboardInterrupt:
        logger.info("SETTING DEFAULT URLS IN TWILIO")
        set_voice_url(DEFAULT_PROD_URL)
        logger.info("CLOSING NGROK TUNNEL")
        ngrok.disconnect()
        show_phone_numbers()
        logger.info("DONE!")

if __name__ == "__main__":
    program()
