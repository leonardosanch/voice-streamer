from django.db import models

class Call(models.Model):
    call_sid = models.CharField(max_length=100, unique=True)
    from_number = models.CharField(max_length=20)
    to_number = models.CharField(max_length=20)
    status = models.CharField(max_length=20)
    duration = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Call {self.call_sid} from {self.from_number} to {self.to_number}"

    class Meta:
        ordering = ['-created_at']
