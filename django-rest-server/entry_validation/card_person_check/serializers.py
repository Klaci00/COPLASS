from rest_framework import serializers
from .models import Card, Gate, AccessRightRequest, SecurityZone, Employee, Message


# ──────────────────────────────────────────────
# Auth
# ──────────────────────────────────────────────

class LoginSerializer(serializers.Serializer):
    username = serializers.IntegerField(required=True)
    password = serializers.CharField(required=True, write_only=True)


# ──────────────────────────────────────────────
# Gate / Card check
# ──────────────────────────────────────────────

class CheckCardPersonSerializer(serializers.Serializer):
    card_number = serializers.CharField(required=True)
    gate        = serializers.IntegerField(required=True)
    direction   = serializers.IntegerField(default=0)
    timestamp   = serializers.DateTimeField(required=True)

    def validate_direction(self, value):
        if value not in (0, 1):
            raise serializers.ValidationError("Direction must be 0 (entry) or 1 (exit).")
        return value

    def validate_gate(self, value):
        if not Gate.objects.filter(gate_number=value).exists():
            raise serializers.ValidationError(f"Gate '{value}' does not exist.")
        return value


# ──────────────────────────────────────────────
# Access right requests
# ──────────────────────────────────────────────

class AccessRightRequestSerializer(serializers.Serializer):
    security_zone = serializers.PrimaryKeyRelatedField(
        queryset=SecurityZone.objects.all()
    )
    supervisor      = serializers.PrimaryKeyRelatedField(
        queryset=Employee.objects.all()
    )
    employee      = serializers.PrimaryKeyRelatedField(
        queryset=Employee.objects.all()
    )
    created_at    = serializers.DateTimeField(required=False)
    start_date    = serializers.DateField(required=True)
    end_date      = serializers.DateField(required=True)

    def validate(self, data):
        if data['start_date'] > data['end_date']:
            raise serializers.ValidationError("start_date must be before end_date.")
        return data

    def create(self, validated_data):
        return AccessRightRequest.objects.create(
            **validated_data,
            approved=False
        )


# ──────────────────────────────────────────────
# Security zones
# ──────────────────────────────────────────────

class SecurityZoneSerializer(serializers.ModelSerializer):
    class Meta:
        model  = SecurityZone
        fields = ['id', 'name']


# ──────────────────────────────────────────────
# Employees
# ──────────────────────────────────────────────

class EmployeeListSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    class Meta:
        model  = Employee
        fields = ['id', 'name', 'is_staff']

    def get_name(self, obj):
        return f"{obj.firstname} {obj.lastname}"


class RegisterEmployeeSerializer(serializers.Serializer):
    firstname     = serializers.CharField(required=True, max_length=150)
    lastname      = serializers.CharField(required=True, max_length=150)
    date_of_birth = serializers.DateField(required=True)
    department    = serializers.CharField(required=True, max_length=150)
    password      = serializers.CharField(
        required=True,
        write_only=True,
        min_length=8,
        style={'input_type': 'password'}
    )

    def create(self, validated_data):
        from django.db.models import Max
        max_id = Employee.objects.aggregate(Max('hr_id'))['hr_id__max']
        hr_id  = (max_id or 0) + 1

        return Employee.objects.create_user(
            hr_id=hr_id,
            **validated_data
        )


# ──────────────────────────────────────────────
# Messages
# ──────────────────────────────────────────────

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Message
        fields = ['id', 'content', 'is_read', 'created_at']
        read_only_fields = ['id', 'content', 'created_at']


class MessageUpdateSerializer(serializers.Serializer):
    id      = serializers.IntegerField(required=True)
    is_read = serializers.BooleanField(required=True)

    def validate_id(self, value):
        if not Message.objects.filter(id=value).exists():
            raise serializers.ValidationError("Message not found.")
        return value