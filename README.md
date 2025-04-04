
````markdown
# Voice Streamer: Bidirectional Media Streams con Twilio

![VoiceFlip](https://github.com/leonardosanch/voice-streamer/raw/main/static/voiceflip-logo.png)

Este proyecto implementa una aplicación de streaming de audio bidireccional utilizando Twilio Media Streams. Permite recibir llamadas telefónicas, procesar el audio y devolver respuestas de audio generadas por ElevenLabs en tiempo real.

## 🌟 Características

- 📞 Recepción de llamadas telefónicas a través de Twilio
- 🎤 Procesamiento de audio entrante en tiempo real
- 🔄 Streaming bidireccional de audio
- 🗣️ Generación de respuestas de audio con ElevenLabs
- 📊 Interfaz web para visualizar logs de audio
- 📈 API RESTful para gestionar llamadas

## 📋 Requisitos

- Python 3.10 o superior
- Cuenta de Twilio (puede ser de prueba)
- Cuenta de ElevenLabs
- Cuenta de ngrok
- twilio-cli (para configuración automática)

## 🚀 Instalación

1. Clonar el repositorio:

```bash
git clone https://github.com/leonardosanch/voice-streamer.git
cd voice-streamer
```
````

2. Crear y activar un entorno virtual:

```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. Instalar las dependencias:

```bash
pip install -r requirements.txt
```

4. Crear un archivo `.env` en la raíz del proyecto con las siguientes variables:

```
# Twilio Credentials
TWILIO_ACCOUNT_SID=tu_account_sid
TWILIO_AUTH_TOKEN=tu_auth_token
TWILIO_API_KEY=tu_api_key
TWILIO_API_SECRET=tu_api_secret

# Ngrok Authentication
NGROK_AUTHTOKEN=tu_ngrok_authtoken

# ElevenLabs API
ELEVENLABS_API_KEY=tu_elevenlabs_api_key
```

5. Ejecutar las migraciones de la base de datos:

```bash
python manage.py migrate
```

6. Crear un superusuario (opcional, para acceder al panel de administración):

```bash
python manage.py createsuperuser
```

## ⚙️ Configuración de Twilio

### Configuración Manual

1. Inicia sesión en la [Consola de Twilio](https://www.twilio.com/console)
2. Adquiere un número de teléfono
3. Configura el número para que dirija las llamadas a tu webhook:
   - En la configuración del número, establece la URL de la solicitud de voz como `https://tu-dominio-ngrok.ngrok-free.app/twilio/stream/`

### Configuración Automática (Recomendada)

Este proyecto incluye un script para configurar automáticamente Twilio usando ngrok:

```bash
python main.py start
```

Este comando:

1. Crea un túnel ngrok hacia tu servidor local
2. Configura tu número de Twilio para usar esta URL
3. Mantiene la sesión abierta durante el tiempo especificado (por defecto 5 minutos)

Para ver el estado actual de la configuración:

```bash
python main.py status
```

Para detener y restaurar la configuración predeterminada:

```bash
python main.py stop
```

## 🎮 Ejecución del Proyecto

1. Iniciar el servidor usando Uvicorn (recomendado para WebSockets):

```bash
python -m uvicorn voice_flow.asgi:application --host 0.0.0.0 --port 8000 --reload
```

Deberías ver una salida similar a:

```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [409728] using StatReload
INFO:     Started server process [409730]
INFO:     Waiting for application startup.
INFO:     ASGI 'lifespan' protocol appears unsupported.
INFO:     Application startup complete.
```

2. En otra terminal, configurar Twilio con ngrok (puedes especificar la duración con `-d`):

```bash
python main.py start -d 24h
```

Esto creará un túnel ngrok que durará 24 horas y configurará tu número de Twilio. Verás una salida con la URL del túnel:

```
INFO: Tunnel created successfully: https://xxxx-xxxx-xxxx-xxxx.ngrok-free.app
```

3. Navega a `http://localhost:8000/audio/logs/` para ver la interfaz de logs y probar el audio.

4. Ahora puedes realizar llamadas al número de Twilio configurado para probar la aplicación completa.

## 📱 Endpoints Disponibles

- `/admin/` - Panel de administración de Django
- `/audio/logs/` - Interfaz para visualizar logs de audio
- `/audio/api/logs/` - API para obtener los logs de audio en formato JSON

## 🏗️ Arquitectura del Proyecto

Este proyecto está construido siguiendo una arquitectura moderna de aplicaciones web en tiempo real, combinando varias tecnologías:

### Componentes Principales

1. **Django**: Framework web principal que maneja las vistas tradicionales, modelos y URLs.

2. **Django Channels**: Extiende Django para manejar protocolos asíncronos como WebSockets, crucial para la transmisión de audio en tiempo real.

3. **Twilio**: Proporciona la infraestructura telefónica y el API de Media Streams para comunicación bidireccional.

4. **ElevenLabs**: API de generación de voz para producir respuestas de audio de alta calidad.

5. **ngrok**: Herramienta que expone el servidor local a Internet para que Twilio pueda enviar webhooks.

### Flujo de Datos

```
┌─────────┐      ┌───────┐      ┌──────────────────┐
│ Usuario │──────│ Twilio│──────│ ngrok tunnel     │
└─────────┘      └───────┘      └──────────────────┘
                                         │
                                         ▼
┌─────────┐      ┌───────────────────────────────┐
│ Browser │◄─────│ Django + Django Channels      │
└─────────┘      │ (WebSockets + HTTP endpoints) │
                 └───────────────────────────────┘
                                │
                                ▼
                  ┌─────────────────────────┐
                  │ ElevenLabs API          │
                  │ (Generación de audio)   │
                  └─────────────────────────┘
```

### Comunicación en Tiempo Real

La clave de este proyecto es el manejo bidireccional de audio en tiempo real:

1. **Entrada**: El audio del usuario se recibe a través de Twilio Media Streams.
2. **Procesamiento**: Se procesa el audio y se genera una respuesta apropiada.
3. **Salida**: El audio generado se envía de vuelta al usuario en tiempo real.

Esta arquitectura permite una experiencia conversacional fluida y natural, similar a las interacciones humanas.

## 📂 Estructura y Explicación de Archivos

### Estructura General

```
voice-streamer/
├── audio_streaming/        # App para manejar streaming de audio
│   ├── consumers.py        # Manejo de WebSockets para audio en tiempo real
│   ├── models.py           # Modelo de datos para logs de audio
│   ├── routing.py          # Configuración de rutas WebSocket
│   ├── templates/          # Plantillas HTML
│   │   └── logs.html       # Interfaz de visualización de logs
│   ├── urls.py             # Configuración de URLs de la app
│   └── views.py            # Vistas para API y páginas web
│
├── calls/                  # App para manejar llamadas Twilio
│   ├── models.py           # Modelo para registrar información de llamadas
│   ├── serializers.py      # Serializadores para la API REST
│   ├── urls.py             # Configuración de URLs de la app
│   └── views.py            # Vistas para manejar webhooks de Twilio
│
├── voice_flow/             # Configuración principal del proyecto
│   ├── asgi.py             # Configuración ASGI para WebSockets
│   ├── settings.py         # Configuración de Django
│   ├── urls.py             # URLs globales del proyecto
│   └── wsgi.py             # Configuración WSGI
│
├── logs/                   # Directorio para archivos de log
│   └── debug.log           # Registro de eventos y errores
│
├── main.py                 # Script CLI para configuración automática
├── manage.py               # Script de gestión de Django
└── requirements.txt        # Dependencias del proyecto
```

### Archivos Clave Explicados

#### 1. Configuración del Proyecto

- **`voice_flow/settings.py`**: Contiene toda la configuración de Django, incluyendo:

  - Configuración de Channels para WebSockets
  - Integración con Twilio y ElevenLabs
  - Configuración de logging y seguridad
  - Carga de variables de entorno desde `.env`

- **`voice_flow/asgi.py`**: Configura el servidor ASGI para manejar tanto HTTP tradicional como WebSockets, esencial para la comunicación en tiempo real.

- **`main.py`**: CLI personalizado que:
  - Crea túneles ngrok para exponer el servidor local
  - Configura automáticamente los números de Twilio
  - Facilita el proceso de prueba y desarrollo

#### 2. Streaming de Audio

- **`audio_streaming/consumers.py`**: El corazón del manejo de audio en tiempo real:

  - Implementa el `AudioStreamConsumer` que gestiona conexiones WebSocket
  - Procesa datos de audio entrantes
  - Integra con ElevenLabs para generar respuestas de audio
  - Envía el audio generado de vuelta al cliente

- **`audio_streaming/routing.py`**: Define las rutas WebSocket para el streaming de audio.

- **`audio_streaming/views.py`**: Implementa:
  - API REST para acceder a los logs de audio
  - Interfaz web para visualizar los logs

#### 3. Gestión de Llamadas

- **`calls/models.py`**: Define el modelo `Call` para almacenar información sobre las llamadas recibidas.

- **`calls/views.py`**: Implementa:

  - Webhook para recibir llamadas de Twilio
  - API para gestionar y consultar información de llamadas
  - Generación de TwiML para controlar el flujo de las llamadas

- **`calls/serializers.py`**: Serializadores para convertir modelos Django a JSON y viceversa en la API REST.

#### 4. Interfaz de Usuario

- **`audio_streaming/templates/logs.html`**: Página web que:
  - Muestra logs de audio en una tabla
  - Proporciona controles para probar la generación de audio
  - Incluye JavaScript para manejar WebSockets y reproducción de audio

### Flujo de Código

1. Una llamada entrante es recibida por Twilio y enviada al webhook definido en `calls/views.py`
2. Se establece una conexión WebSocket en `audio_streaming/consumers.py` para el streaming de audio
3. El audio recibido se procesa y se utiliza para generar una respuesta con ElevenLabs
4. El audio generado se envía de vuelta al cliente a través del WebSocket
5. Todos los eventos se registran en la base de datos y pueden visualizarse en la interfaz web

## 📄 Explicación Detallada de Archivos

A continuación, se detalla el propósito y funcionalidad de cada archivo principal del proyecto:

### App `audio_streaming`

#### `audio_streaming/consumers.py`

- **Propósito**: Maneja la comunicación WebSocket para el streaming bidireccional de audio.
- **Funcionalidades**:
  - Clase `AudioStreamConsumer` que gestiona la conexión WebSocket
  - Métodos para conexión, desconexión y recepción de mensajes
  - Inicialización del cliente ElevenLabs para generación de audio
  - Manejo de eventos como 'start', 'stop', 'media' y 'connected'
  - Procesamiento de datos de audio y generación de respuestas
  - Envío de audio generado de vuelta al cliente
  - Registro de logs en la base de datos

#### `audio_streaming/models.py`

- **Propósito**: Define el modelo de datos para almacenar información sobre los eventos de audio.
- **Funcionalidades**:
  - Modelo `AudioLog` con campos para fecha, evento, texto generado, duración, SID de Twilio e IP
  - Representación en string personalizada para facilitar la depuración

#### `audio_streaming/routing.py`

- **Propósito**: Configura las rutas WebSocket para la aplicación.
- **Funcionalidades**:
  - Define el patrón URL para la ruta WebSocket del streaming de audio
  - Asigna la ruta al consumidor `AudioStreamConsumer`

#### `audio_streaming/urls.py`

- **Propósito**: Define las rutas HTTP para la aplicación.
- **Funcionalidades**:
  - Ruta para la API de logs de audio
  - Ruta para la página web de visualización de logs

#### `audio_streaming/views.py`

- **Propósito**: Implementa las vistas para la interfaz web y API REST.
- **Funcionalidades**:
  - Función `audio_logs_api` que devuelve los logs en formato JSON
  - Función `logs_page` que renderiza la plantilla HTML para visualizar logs

#### `audio_streaming/templates/audio_streaming/logs.html`

- **Propósito**: Proporciona la interfaz de usuario para visualizar logs y probar el audio.
- **Funcionalidades**:
  - Tabla para mostrar logs de audio
  - Controles para iniciar/detener pruebas de audio
  - Reproductor de audio para escuchar las respuestas generadas
  - JavaScript para manejar conexiones WebSocket y reproducción de audio

### App `calls`

#### `calls/admin.py`

- **Propósito**: Configura la interfaz de administración de Django para las llamadas.
- **Funcionalidades**:
  - Registra el modelo `Call` en el admin de Django
  - Define la visualización y filtros para la interfaz de administración

#### `calls/models.py`

- **Propósito**: Define el modelo de datos para almacenar información sobre llamadas.
- **Funcionalidades**:
  - Modelo `Call` con campos para SID, números de origen/destino, estado, duración y timestamps
  - Configuración de ordenamiento por fecha de creación

#### `calls/serializers.py`

- **Propósito**: Define serializadores para la API REST.
- **Funcionalidades**:
  - Clase `CallSerializer` que convierte objetos `Call` a/desde JSON
  - Define campos para la API y cuáles son de solo lectura

#### `calls/urls.py`

- **Propósito**: Define las rutas HTTP para la aplicación de llamadas.
- **Funcionalidades**:
  - Actualmente vacío, preparado para futuras rutas

#### `calls/views.py`

- **Propósito**: Implementa las vistas para manejar webhooks de Twilio y APIs REST.
- **Funcionalidades**:
  - Función `handle_call` que procesa llamadas entrantes de Twilio
  - Función `call_list` que lista todas las llamadas o filtra por estado
  - Función `call_detail` que obtiene o actualiza detalles de una llamada específica
  - Generación de respuestas TwiML para controlar el flujo de llamadas

### Configuración del Proyecto

#### `voice_flow/settings.py`

- **Propósito**: Contiene toda la configuración de Django para el proyecto.
- **Funcionalidades**:
  - Configuración de aplicaciones instaladas, middleware, bases de datos
  - Configuración de Channels para WebSockets
  - Integración con Twilio y ElevenLabs mediante variables de entorno
  - Configuración de logging
  - Gestión de seguridad (CSRF, CORS, etc.)
  - Configuración de archivos estáticos

#### `voice_flow/asgi.py`

- **Propósito**: Configura la interfaz ASGI para servir tanto HTTP como WebSockets.
- **Funcionalidades**:
  - Crea un router de protocolos que dirige HTTP a Django y WebSockets a Channels
  - Integra las rutas WebSocket definidas en `audio_streaming/routing.py`

#### `voice_flow/urls.py`

- **Propósito**: Define las rutas URL globales del proyecto.
- **Funcionalidades**:
  - Incluye rutas para el panel de administración de Django
  - Incluye las rutas de las aplicaciones `calls` y `audio_streaming`

#### `voice_flow/wsgi.py`

- **Propósito**: Configura la interfaz WSGI para despliegues tradicionales.
- **Funcionalidades**:
  - Inicializa la aplicación Django para servidores WSGI

### Scripts y Herramientas

#### `main.py`

- **Propósito**: Script CLI para automatizar la configuración de Twilio y ngrok.
- **Funcionalidades**:
  - Comandos para iniciar, ver el estado y detener la integración
  - Creación automática de túneles ngrok
  - Configuración del número de Twilio para apuntar al túnel creado
  - Mantenimiento del túnel durante un tiempo especificado

#### `manage.py`

- **Propósito**: Script estándar de Django para gestionar el proyecto.
- **Funcionalidades**:
  - Ejecutar el servidor de desarrollo
  - Aplicar migraciones
  - Crear superusuarios
  - Y otras tareas administrativas de Django

#### `requirements.txt`

- **Propósito**: Lista todas las dependencias del proyecto.
- **Funcionalidades**:
  - Especifica las versiones exactas de todas las bibliotecas requeridas
  - Facilita la instalación con `pip install -r requirements.txt`

## 🧪 Pruebas

### Realizar una llamada de prueba

1. Asegúrate de que el servidor Django esté ejecutándose
2. Ejecuta `python main.py start` para configurar ngrok y Twilio
3. Llama al número de teléfono de Twilio desde cualquier teléfono
4. Deberías escuchar una respuesta de audio generada por ElevenLabs

### Visualizar logs

Visita `http://localhost:8000/audio/logs/` para ver los logs de las llamadas y el audio procesado. La interfaz muestra:

- **Tabla de logs**: Muestra el historial de eventos de audio con fecha, evento, texto generado, duración, SID de Twilio e IP
- **Prueba de audio en tiempo real**: Permite probar la generación de audio sin necesidad de realizar una llamada

![Interfaz de Logs](https://github.com/leonardosanch/voice-streamer/raw/main/static/logs-interface.png)

Cuando inicias una prueba, verás mensajes en la consola del navegador:

```
✅ WebSocket conectado
📩 Mensaje recibido: {"event": "connection_established", "message": "Conexión WebSocket establecida", "client_id": "135797259400112"}
📩 Mensaje recibido: {"event": "ready", "message": "Listo para streaming", "client_id": "135797259400112"}
📩 Mensaje recibido: {"event": "started", "message": "Streaming iniciado", "status": "streaming"}
🎵 Reproduciendo audio
```

Y en el servidor verás logs detallados del proceso:

```
INFO consumers ✅ Cliente ElevenLabs inicializado
INFO consumers 🔗 Cliente conectado (ID: 128986493685872)
INFO consumers ▶️ Stream iniciado para cliente 128986493685872
INFO consumers Tipo de respuesta: <class 'generator'>
INFO _client HTTP Request: POST https://api.elevenlabs.io/v1/text-to-speech/9BWtsMINqrJLrRacOk9x "HTTP/1.1 200 OK"
INFO consumers Longitud de bytes de audio: 40587
INFO consumers 🎵 Audio enviado para cliente 128986493685872
INFO consumers 📝 Log guardado para cliente 128986493685872
```

## 🔄 Flujo de la aplicación

### Flujo de llamada telefónica:

1. El usuario llama al número de Twilio configurado
2. Twilio envía la llamada a tu webhook
3. La aplicación recibe el audio entrante a través de WebSockets
4. El audio se procesa y se genera una respuesta utilizando ElevenLabs
5. La respuesta de audio se envía de vuelta al usuario en tiempo real
6. Todos los eventos se registran en la base de datos
7. Los logs pueden visualizarse en la interfaz web

### Flujo de prueba desde la interfaz web:

1. El usuario accede a `http://localhost:8000/audio/logs/`
2. Al hacer clic en "Iniciar prueba", se establece una conexión WebSocket
3. La aplicación genera audio de prueba usando ElevenLabs
4. El audio se transmite al navegador y se reproduce automáticamente
5. El evento se registra en la base de datos y aparece en la tabla de logs
6. El usuario puede detener la prueba en cualquier momento

## ⚠️ Notas Importantes

- Esta aplicación está configurada para desarrollo y pruebas, no para producción
- Las credenciales de Twilio y ElevenLabs deben mantenerse seguras y nunca deben compartirse.

```

```
