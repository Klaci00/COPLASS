from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

# Create your models here.

class AccessRight(models.Model):
    security_zone = models.ForeignKey('SecurityZone', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    start_date = models.DateField(db_index=True)
    end_date = models.DateField(db_index=True)
    employee = models.ForeignKey('Employee', on_delete=models.CASCADE,
                              related_name='access_rights_for_employee')
    def __str__(self):
        emp = f"{self.employee.firstname} {self.employee.lastname}" if self.employee else "Unknown Employee"
        zone = self.security_zone.name if self.security_zone else "Unknown Zone"
        return f"{emp} - {zone} ({self.start_date} → {self.end_date})"

class AccessRightRequest(models.Model):
    security_zone = models.ForeignKey('SecurityZone', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    start_date = models.DateField()
    end_date = models.DateField()
    supervisor = models.ForeignKey('Employee', on_delete=models.SET_NULL, related_name='access_right_requests_for_supervisor', null=True)
    employee = models.ForeignKey('Employee', on_delete=models.CASCADE,
                              related_name='access_right_requests_for_employee')
    approved = models.BooleanField(default=False)
    def approve(self):
        if self.approved:
            return  # already approved, do nothing
        self.approved = True
        self.save(update_fields=['approved'])
        AccessRight.objects.create(
            security_zone=self.security_zone,
            start_date=self.start_date,
            end_date=self.end_date,
            employee=self.employee
        )
        Message.objects.create(
            content=f"Your access right request for {self.security_zone.name} has been approved.",
            employee=self.employee
        )
    def __str__(self):
        emp = f"{self.employee.firstname} {self.employee.lastname}" if self.employee else "Unknown Employee"
        zone = self.security_zone.name if self.security_zone else "Unknown Zone"
        return f"Request: {emp} - {zone} ({self.start_date} → {self.end_date}) - {'Approved' if self.approved else 'Pending'}"

class Department(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name
    
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
        extra_fields.setdefault('is_active', True)
        return self.create_user(hr_id, password, **extra_fields)

class Employee(AbstractBaseUser, PermissionsMixin):
    firstname = models.CharField(max_length=100)
    lastname = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    hr_id = models.IntegerField(unique=True)
    department = models.ForeignKey('Department', on_delete=models.SET_NULL, null=True, blank=True)
    current_zone = models.ForeignKey('SecurityZone', on_delete=models.SET_NULL, null=True, blank=True)
    on_the_clock = models.BooleanField(default=True)
    deputy = models.ManyToManyField('self', symmetrical=True, related_name='deputies_for_employee', blank=True)
    supervisor = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='supervisees')
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

class Message(models.Model):
    is_read = models.BooleanField(default=False)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='messages_for_employee', null=True, blank=True)
    def __str__(self):
        emp = f"{self.employee.firstname} {self.employee.lastname}" if self.employee else "Unknown Employee"
        return f"Message for {emp} at {self.created_at}"
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
        card_count = Card.objects.filter(employee=self.employee).count() + 1
        self.card_number = str(self.employee.hr_id) + str(card_count)
        self.related_hr_id = str(self.employee.hr_id)
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
        gate = self.gate.id if self.gate else "N/A"
        card = self.card.card_number if self.card else "N/A"
        return f"Gate {gate} - {card} at {self.timestamp}"
class Gate(models.Model):
    current_zone = models.ForeignKey(SecurityZone, on_delete=models.CASCADE, related_name='gates_current')
    opposite_zone = models.ForeignKey(SecurityZone, on_delete=models.CASCADE, related_name='gates_oppposite')
    def __str__(self):
        return f"Gate between {self.opposite_zone.name} and {self.current_zone.name}"