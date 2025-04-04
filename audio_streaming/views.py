from django.http import JsonResponse
from django.shortcuts import render
from .models import AudioLog

def audio_logs_api(request):
    logs = AudioLog.objects.order_by('-timestamp')[:100]
    data = [
        {
            'timestamp': log.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            'event': log.event,
            'response_text': log.response_text,
            'audio_length': log.audio_length,
            'twilio_sid': log.twilio_sid,
            'ip_address': log.ip_address
        }
        for log in logs
    ]
    return JsonResponse({'logs': data})

def logs_page(request):
    return render(request, 'audio_streaming/logs.html')
