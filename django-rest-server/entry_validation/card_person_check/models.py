from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

# Create your models here.

class AccessRight(models.Model):
    security_zone = models.ForeignKey('SecurityZone', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    start_date = models.DateField()
    end_date = models.DateField()
    employee = models.ForeignKey('Employee', on_delete=models.CASCADE, related_name='access_rights_for_employee', null=True, blank=True)
    def __str__(self):
        return f"{self.employee.firstname} {self.employee.lastname} - {self.security_zone.name} ({self.start_date} → {self.end_date})"

class AccessRightRequest(models.Model):
    security_zone = models.ForeignKey('SecurityZone', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    start_date = models.DateField()
    end_date = models.DateField()
    employee = models.ForeignKey('Employee', on_delete=models.CASCADE, related_name='access_right_requests_for_employee', null=True, blank=True)
    approved = models.BooleanField(default=False)
    def __str__(self):
        return f"Request: {self.employee.firstname} {self.employee.lastname} - {self.security_zone.name} ({self.start_date} → {self.end_date}) - {'Approved' if self.approved else 'Pending'}"

class EmployeeManager(BaseUserManager):
    def create_user(self, hr_id, password=None, **extra_fields):
        if not hr_id:
            raise ValueError('The HR ID must be set')
        user = self.model(hr_id=hr_id, **extra_fields)
        user.set_password(password) # Hashes the password securely
        user.save(using=self._db)
        return user

    def create_superuser(self, hr_id, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(hr_id, password, **extra_fields)

class Employee(AbstractBaseUser, PermissionsMixin):
    firstname = models.CharField(max_length=100)
    lastname = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    hr_id = models.IntegerField(unique=True)
    department = models.CharField(max_length=100)
    current_zone = models.ForeignKey('SecurityZone', on_delete=models.SET_NULL, null=True, blank=True)
    access_rights = models.ManyToOneRel(
        to=AccessRight, field='employee',field_name='employee', related_name='employee_access_rights')
    # Required for Django Admin and Authentication
    is_active = models.BooleanField(default=False)
    is_supervisor = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    objects = EmployeeManager()
    # Tells Django to use hr_id instead of a username for login
    USERNAME_FIELD = 'hr_id'
    REQUIRED_FIELDS = ['firstname', 'lastname', 'date_of_birth']
    def __str__(self):
        return f"{self.firstname} {self.lastname} ({self.hr_id})"

class Card(models.Model):
    is_active = models.BooleanField(default=False)
    valid_from = models.DateField()
    valid_to = models.DateField()
    card_id = models.CharField(max_length=50, unique=True)
    card_number = models.CharField(max_length=20, editable=False, unique=True)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='related_cards')
    related_hr_id = models.CharField(max_length=50, editable=False)
    lock_until = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        self.card_number = self.card_id + self.employee.hr_id
        self.related_hr_id = self.employee.hr_id
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Card {self.card_number} for {self.employee.firstname} {self.employee.lastname}"

class SecurityZone(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    def __str__(self):
        return f"{self.name}"
class GateEvent(models.Model):
    gate = models.ForeignKey('Gate', on_delete=models.CASCADE, null=True, blank=True)
    card = models.ForeignKey(Card, on_delete=models.CASCADE, null=True, blank=True)
    timestamp = models.DateTimeField()
    control = models.BooleanField(default=False, editable=False)
    allowed = models.BooleanField(default=False, editable=False)
    warning = models.CharField(max_length=255, null=True, blank=True, editable=False)
    from_zone = models.ForeignKey(SecurityZone, on_delete=models.CASCADE, related_name='events_from_zone', null=True, blank=True)
    to_zone = models.ForeignKey(SecurityZone, on_delete=models.CASCADE, related_name='events_to_zone', null=True, blank=True)
    def __str__(self):
        return f"Gate {self.gate.gate_number} - {self.card.card_number} at {self.timestamp}"
class Gate(models.Model):
    inside_zone = models.ForeignKey(SecurityZone, on_delete=models.CASCADE, related_name='gates_inside')
    outside_zone = models.ForeignKey(SecurityZone, on_delete=models.CASCADE, related_name='gates_outside')
    gate_number = models.IntegerField()
    def __str__(self):
        return f"Gate {self.gate_number} between {self.outside_zone.name} and {self.inside_zone.name}"