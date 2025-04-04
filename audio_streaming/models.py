from django.db import models

class AudioLog(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    event = models.CharField(max_length=50)
    response_text = models.TextField(blank=True, null=True)
    audio_length = models.FloatField(blank=True, null=True)
    twilio_sid = models.CharField(max_length=64, blank=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)

    def __str__(self):
        return f"{self.timestamp} | {self.event}"