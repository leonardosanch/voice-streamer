from django.contrib import admin
from .models import Call

@admin.register(Call)
class CallAdmin(admin.ModelAdmin):
    list_display = ('call_sid', 'from_number', 'to_number', 'status', 'duration', 'created_at')
    search_fields = ('call_sid', 'from_number', 'to_number')
    list_filter = ('status', 'created_at')
