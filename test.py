import asyncio
import websockets
import json
import base64
from gtts import gTTS
from pydub import AudioSegment
import os

async def generar_audio_base64(texto):
    # Paso 1: Generar MP3 desde texto
    tts = gTTS(text=texto, lang='es')
    tts.save("temp.mp3")

    # Paso 2: Convertir a WAV
    audio = AudioSegment.from_mp3("temp.mp3")
    audio.export("sample.wav", format="wav")

    # Paso 3: Leer y codificar en base64
    with open("sample.wav", "rb") as f:
        audio_bytes = f.read()
        audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")

    # Limpieza de archivos temporales
    os.remove("temp.mp3")
    os.remove("sample.wav")

    return audio_b64

async def test_websocket():
    uri = "ws://localhost:8000/ws/audio/stream/"

    async with websockets.connect(uri) as websocket:
        # Evento de conexión
        await websocket.send(json.dumps({"event": "connected"}))
        print("Enviado: evento connected")
        response = await websocket.recv()
        print(f"Recibido: {response}")

        # Iniciar stream
        await websocket.send(json.dumps({"event": "start"}))
        print("Enviado: evento start")
        response = await websocket.recv()
        print(f"Recibido: {response}")

        # Generar y enviar audio codificado
        print("Generando audio...")
        audio_b64 = await generar_audio_base64("Hola, este es un mensaje de prueba desde el script.")
        print(f"📦 Longitud del audio_base64: {len(audio_b64)} caracteres")

        await websocket.send(json.dumps({
            "event": "media",
            "media": audio_b64
        }))
        print("Enviado: evento media con audio")

        # En este punto, el servidor podría enviar una respuesta en bytes (audio)
        # o un mensaje JSON (error)
        try:
            # Esperar respuesta
            print("Esperando respuesta...")
            response = await websocket.recv()
            
            # Determinar si es binario (audio) o texto (mensaje JSON)
            if isinstance(response, bytes):
                # Guardar el audio recibido para verificar
                with open("respuesta_audio.wav", "wb") as f:
                    f.write(response)
                print("🎧 Respuesta de audio recibida y guardada como 'respuesta_audio.wav'")
                print(f"📊 Tamaño del audio recibido: {len(response)} bytes")
            else:
                # Es un mensaje de texto (probablemente JSON)
                print(f"📄 Mensaje recibido: {response}")
                try:
                    json_response = json.loads(response)
                    print(f"JSON decodificado: {json_response}")
                except:
                    print("No es un mensaje JSON válido")
                    
            # Detener stream
            await websocket.send(json.dumps({"event": "stop"}))
            print("Enviado: evento stop")
            
            # Recibir confirmación de stop
            stop_response = await websocket.recv()
            print(f"Respuesta a stop: {stop_response}")
            
        except Exception as e:
            print(f"Error al recibir respuesta: {str(e)}")

asyncio.run(test_websocket())