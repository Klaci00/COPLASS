from datetime import date

from rest_framework import serializers
from .models import (
    Gate,
    AccessRightRequest,
    SecurityZone,
    Employee,
    Message,
    Department,
)

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
    gate = serializers.IntegerField(required=True)
    timestamp = serializers.DateTimeField(required=True)

    def validate_gate(self, value):
        if not Gate.objects.filter(id=value).exists():
            raise serializers.ValidationError(f"Gate '{value}' does not exist.")
        return value


# ──────────────────────────────────────────────
# Access right requests
# ──────────────────────────────────────────────


class AccessRightRequestSerializer(serializers.ModelSerializer):
    # Override FK fields to fetch only 'pk' during validation
    # instead of SELECT * (all columns)
    employee = serializers.PrimaryKeyRelatedField(queryset=Employee.objects.only("pk"))
    supervisor = serializers.PrimaryKeyRelatedField(
        queryset=Employee.objects.only("pk").filter(is_supervisor=True),
    )
    security_zone = serializers.PrimaryKeyRelatedField(
        queryset=SecurityZone.objects.only("pk")
    )

    employee_name = serializers.SerializerMethodField()
    supervisor_name = serializers.SerializerMethodField()
    zone_name = serializers.SerializerMethodField()
    covered_as_deputy = serializers.BooleanField(read_only=True, default=False)

    class Meta:
        model = AccessRightRequest
        fields = [
            "id",
            "employee",
            "employee_name",
            "supervisor",
            "supervisor_name",
            "security_zone",
            "zone_name",
            "start_date",
            "end_date",
            "created_at",
            "approved",
            "covered_as_deputy",
        ]
        read_only_fields = ["id", "created_at", "approved", "covered_as_deputy"]

    def get_employee_name(self, obj):
        return (
            f"{obj.employee.firstname} {obj.employee.lastname}"
            if obj.employee
            else None
        )

    def get_supervisor_name(self, obj):
        return (
            f"{obj.supervisor.firstname} {obj.supervisor.lastname}"
            if obj.supervisor
            else None
        )

    def get_zone_name(self, obj):
        return obj.security_zone.name if obj.security_zone else None

    def validate(self, data):
        if data["end_date"] < data["start_date"]:
            raise serializers.ValidationError("end_date must be after start_date.")
        if data["start_date"] < date.today():
            raise serializers.ValidationError("start_date cannot be in the past.")
        return data


# ──────────────────────────────────────────────
# Security zones
# ──────────────────────────────────────────────


class SecurityZoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = SecurityZone
        fields = ["id", "name"]


# ──────────────────────────────────────────────
# Employees
# ──────────────────────────────────────────────


class EmployeeListSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    class Meta:
        model = Employee
        fields = ["id", "name", "is_staff", "is_supervisor", "department"]

    def get_name(self, obj):
        return f"{obj.firstname} {obj.lastname}"


class NewRegistrationsSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    class Meta:
        model = Employee
        queryset = Employee.objects.filter(is_active=False)
        fields = ["id", "name"]

    def get_name(self, obj):
        return f"{obj.firstname} {obj.lastname}"


class RegisterEmployeeSerializer(serializers.Serializer):
    firstname = serializers.CharField(required=True, max_length=150)
    lastname = serializers.CharField(required=True, max_length=150)
    date_of_birth = serializers.DateField(required=True)
    department = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.all(), required=True
    )
    supervisor = serializers.PrimaryKeyRelatedField(
        queryset=Employee.objects.filter(is_supervisor=True),
        required=False,
        allow_null=True,
        default=None,
    )
    password = serializers.CharField(
        required=True, write_only=True, min_length=8, style={"input_type": "password"}
    )

    def create(self, validated_data):
        from django.db.models import Max

        max_id = Employee.objects.aggregate(Max("hr_id"))["hr_id__max"]
        hr_id = (max_id or 0) + 1

        # Pop supervisor out — ManyToMany and FK need to be handled after save
        supervisor = validated_data.pop("supervisor", None)

        employee = Employee.objects.create_user(
            hr_id=hr_id, supervisor=supervisor, **validated_data
        )

        # Populate deputy with all colleagues who share the same supervisor
        if supervisor:
            colleagues = Employee.objects.filter(supervisor=supervisor).exclude(
                pk=employee.pk
            )  # exclude the new employee themselves

            employee.deputy.set(colleagues)

            # ✅ Since deputy is symmetrical=True, also add the new employee
            # to each colleague's deputy set — Django handles this automatically
            # for symmetrical M2M, so .set() is sufficient.

        return employee


# ──────────────────────────────────────────────
# Messages
# ──────────────────────────────────────────────


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ["id", "content", "is_read", "created_at"]
        read_only_fields = ["id", "content", "created_at"]


class MessageUpdateSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    is_read = serializers.BooleanField(required=True)

    def validate_id(self, value):
        if not Message.objects.filter(id=value).exists():
            raise serializers.ValidationError("Message not found.")
        return value
