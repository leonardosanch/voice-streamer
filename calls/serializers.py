from rest_framework import serializers
from .models import Call

class CallSerializer(serializers.ModelSerializer):
    class Meta:
        model = Call
        fields = [
            'id',
            'call_sid',
            'from_number',
            'to_number',
            'status',
            'duration',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
