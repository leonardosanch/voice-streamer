from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from twilio.twiml.voice_response import VoiceResponse
from .models import Call
from .serializers import CallSerializer
from django.shortcuts import get_object_or_404
import logging

logger = logging.getLogger(__name__)

@csrf_exempt
@api_view(['POST'])
def handle_call(request):
    """
    Maneja las llamadas entrantes de Twilio y responde con TwiML.
    """
    response = VoiceResponse()

    call_sid = request.data.get('CallSid')
    from_number = request.data.get('From')
    to_number = request.data.get('To')

    # Verifica que los datos sean válidos
    if not call_sid or not from_number or not to_number:
        logger.error("❌ Datos de llamada incompletos")
        return Response({'error': 'Datos de llamada incompletos'}, status=status.HTTP_400_BAD_REQUEST)

    call_data = {
        'call_sid': call_sid,
        'from_number': from_number,
        'to_number': to_number,
        'status': 'received'
    }

    serializer = CallSerializer(data=call_data)
    if serializer.is_valid():
        serializer.save()
        logger.info(f"✅ Llamada registrada: {call_sid}")
    else:
        logger.warning(f"⚠️ Error guardando llamada: {serializer.errors}")

    # Respuesta de voz
    response.say('Bienvenido al sistema de respuesta de voz.', voice='alice', language='es-MX')

    return HttpResponse(str(response), content_type='text/xml')

@api_view(['GET'])
def call_list(request):
    """
    Lista todas las llamadas o filtra por estado.
    """
    status_filter = request.query_params.get('status', None)
    calls = Call.objects.filter(status=status_filter) if status_filter else Call.objects.all()

    serializer = CallSerializer(calls, many=True)
    return Response(serializer.data)

@api_view(['GET', 'PUT'])
def call_detail(request, call_sid):
    """
    Obtiene o actualiza los detalles de una llamada específica.
    """
    call = get_object_or_404(Call, call_sid=call_sid)

    if request.method == 'GET':
        serializer = CallSerializer(call)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = CallSerializer(call, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            logger.info(f"✅ Llamada {call_sid} actualizada")
            return Response(serializer.data)
        logger.warning(f"⚠️ Error actualizando llamada {call_sid}: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
