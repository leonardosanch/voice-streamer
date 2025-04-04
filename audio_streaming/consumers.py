# Nombre del archivo: consumers.py

import json
import logging
import base64
import traceback

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.exceptions import StopConsumer
from elevenlabs.client import ElevenLabs
from django.conf import settings
from channels.db import database_sync_to_async

logger = logging.getLogger(__name__)

class AudioStreamConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_streaming = False
        self.client_id = None
        self.client = self._init_elevenlabs_client()

    def _init_elevenlabs_client(self):
        try:
            client = ElevenLabs(api_key=settings.ELEVENLABS_API_KEY)
            logger.info("✅ Cliente ElevenLabs inicializado")
            return client
        except Exception as e:
            logger.error(f"❌ Error al inicializar ElevenLabs: {str(e)}")
            return None

    async def connect(self):
        await self.accept()
        self.client_id = str(id(self))

        if not self.client:
            await self._send_error('init_error', 'Cliente ElevenLabs no inicializado')
            await self.close()
            return

        logger.info(f"🔗 Cliente conectado (ID: {self.client_id})")
        await self.send_json({
            'event': 'connection_established',
            'message': 'Conexión WebSocket establecida',
            'client_id': self.client_id
        })

    async def disconnect(self, close_code):
        logger.info(f"❌ Cliente {self.client_id} desconectado (código {close_code})")
        self.is_streaming = False
        raise StopConsumer()

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            event = data.get('event', '')

            match event:
                case 'start':
                    await self._handle_start_stream()
                case 'stop':
                    await self._handle_stop_stream()
                case 'media':
                    await self._handle_media_data(data)
                case 'connected':
                    await self.send_json({
                        'event': 'ready',
                        'message': 'Listo para streaming',
                        'client_id': self.client_id
                    })
                case _:
                    logger.warning(f"❓ Evento desconocido: {event}")
                    await self._send_error('unknown_event', f'Evento no reconocido: {event}')

        except json.JSONDecodeError:
            logger.error("❌ Formato JSON inválido")
            await self._send_error('json_error', 'Formato JSON inválido')
        except Exception as e:
            error_traceback = traceback.format_exc()
            logger.error(f"❌ Error al procesar el mensaje: {str(e)}\n{error_traceback}")
            await self._send_error('internal_error', str(e))

    async def _handle_start_stream(self):
        self.is_streaming = True
        logger.info(f"▶️ Stream iniciado para cliente {self.client_id}")
        await self.send_json({
            'event': 'started',
            'message': 'Streaming iniciado',
            'status': 'streaming'
        })

    async def _handle_stop_stream(self):
        self.is_streaming = False
        logger.info(f"⏹️ Stream detenido para cliente {self.client_id}")
        await self.send_json({
            'event': 'stopped',
            'message': 'Streaming detenido',
            'status': 'stopped'
        })

    async def _handle_media_data(self, data):
        if not self.is_streaming:
            logger.warning(f"⚠️ Datos recibidos sin stream activo para cliente {self.client_id}")
            return

        try:
            media_data = data.get('media')
            if not media_data:
                logger.warning("⚠️ Campo 'media' vacío o faltante")
                return

            response_text = "Mensaje recibido correctamente"

            # 🎙️ Generar audio con ElevenLabs
            try:
                response = self.client.text_to_speech.convert(
                    text=response_text,
                    voice_id="9BWtsMINqrJLrRacOk9x",
                    model_id="eleven_multilingual_v2"
                )
                
                logger.info(f"Tipo de respuesta: {type(response)}")
                
                # Verificar qué contiene realmente la respuesta
                if hasattr(response, 'read'):
                    # Probablemente es un objeto tipo archivo
                    audio_bytes = response.read()
                elif hasattr(response, '__iter__'):
                    # Es un iterable, pero seamos más cuidadosos
                    try:
                        audio_bytes = b''.join(chunk for chunk in response)
                    except Exception as e:
                        logger.error(f"❌ Error al unir fragmentos de audio: {str(e)}")
                        await self._send_error('audio_error', f'Error al procesar fragmentos de audio: {str(e)}')
                        return
                else:
                    # Podría ser ya bytes
                    audio_bytes = response if isinstance(response, bytes) else bytes(response)
                
                # Registrar la longitud para confirmar que tenemos datos
                audio_length = len(audio_bytes) / 1000.0  # Convertir a kilobytes como aproximación
                logger.info(f"Longitud de bytes de audio: {len(audio_bytes)}")
                
                audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")

                # 📤 Enviar audio al cliente
                await self.send(bytes_data=audio_bytes)
                logger.info(f"🎵 Audio enviado para cliente {self.client_id}")

                # 💾 Guardar log en la base de datos
                await self._save_audio_log(response_text, audio_length)
                
            except Exception as audio_error:
                error_traceback = traceback.format_exc()
                logger.error(f"❌ Error específico al generar audio: {str(audio_error)}\n{error_traceback}")
                await self._send_error('audio_generation_error', str(audio_error))

        except Exception as e:
            # Añadir información de error más detallada
            error_traceback = traceback.format_exc()
            logger.error(f"❌ Error procesando datos de audio: {str(e)}\n{error_traceback}")
            await self._send_error('audio_error', str(e))

    async def _save_audio_log(self, response_text, audio_length):
        try:
            from .models import AudioLog  # Importación *dentro* del método
            
            # Creamos el registro usando los campos correctos del modelo
            await database_sync_to_async(AudioLog.objects.create)(
                event="media_processed",  # Un evento descriptivo
                response_text=response_text,
                audio_length=audio_length,
                ip_address=self.scope.get('client')[0] if 'client' in self.scope else None
                # twilio_sid se deja como None ya que no parece relevante para este caso
            )
            
            logger.info(f"📝 Log guardado para cliente {self.client_id}")
        except Exception as e:
            error_traceback = traceback.format_exc()
            logger.error(f"❌ Error al guardar log: {str(e)}\n{error_traceback}")

    async def _send_error(self, code, message):
        await self.send_json({
            'event': 'error',
            'code': code,
            'message': message
        })

    async def send_json(self, content: dict):
        """Envoltura para enviar mensajes JSON"""
        await self.send(text_data=json.dumps(content))