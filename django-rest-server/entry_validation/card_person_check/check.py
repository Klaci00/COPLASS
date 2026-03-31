import random
from .models import Employee, Gate, AccessRight
from django.utils import timezone
from datetime import timedelta
from dataclasses import dataclass
from typing import Optional
import logging
from .constants import CHECK_PROBABILITY

def check_access_rights(employee: Employee, gate: Gate, direction: int) -> bool:
    today = timezone.now().date()
    target_zone = gate.inside_zone if direction == 0 else gate.outside_zone
    return AccessRight.objects.filter(
        employee=employee,
        security_zone=target_zone,
        start_date__lte=today,
        end_date__gte=today
    ).exists()
# check.py — return a plain dataclass instead

@dataclass
class AccessResult:
    allowed: bool
    status_code: int
    message: Optional[str] = None
    control: bool = False

def check_card_person(card, employee, gate, direction) -> AccessResult:
    if not card:
        return AccessResult(allowed=False, status_code=404, message="Card not found.")
    if not employee:
        return AccessResult(allowed=False, status_code=404, message="Employee not found.")
    if not gate:
        return AccessResult(allowed=False, status_code=404, message="Gate not found.")
    if not card.is_active:
        return AccessResult(allowed=False, status_code=403, message="Card is inactive.")
    if card.valid_from and card.valid_to:
        if card.valid_from > timezone.now().date() or card.valid_to < timezone.now().date():
            return AccessResult(allowed=False, status_code=403, message="Card is not valid at this time.")
    if card.lock_until and card.lock_until > timezone.now():
        return AccessResult(allowed=False, status_code=403, message="Card is temporarily locked.")
    if not check_access_rights(employee, gate, direction):
        return AccessResult(allowed=False, status_code=403, message="No valid access rights for this gate.")
    if random.randint(1, CHECK_PROBABILITY) == 0:
        card.lock_until = timezone.now() + timedelta(minutes=5)
        card.save()
        return AccessResult(allowed=False, status_code=403, control=True)
    return AccessResult(allowed=True, status_code=200)