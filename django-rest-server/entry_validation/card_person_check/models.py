from django.db import models

# Create your models here.

class Employee(models.Model):
    firstname = models.CharField(max_length=100)
    lastname = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    hr_id = models.CharField(max_length=50, unique=True)
    department = models.CharField(max_length=100)
    cards = models.ManyToManyField('Card', related_name='employees', blank=True)
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

class Gate(models.Model):
    inside_zone = models.ForeignKey(SecurityZone, on_delete=models.CASCADE, related_name='gates_inside')
    outside_zone = models.ForeignKey(SecurityZone, on_delete=models.CASCADE, related_name='gates_outside')
    gate_number = models.IntegerField()
    def __str__(self):
        return f"Gate {self.gate_number} between {self.outside_zone.name} and {self.inside_zone.name}"