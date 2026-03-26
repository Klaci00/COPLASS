import random
from .models import Card, Employee, Gate, AccessRight
from django.utils import timezone
from rest_framework.response import Response

def check_access_rights(employee : Employee, gate : Gate, direction : int) -> bool:
    current_date = timezone.now().date()
    print(f'Inside Zone: {gate.inside_zone.name}')
    access_rights = AccessRight.objects.filter(employee=employee, security_zone=gate.inside_zone if direction == 0 else gate.outside_zone, start_date__lte=current_date, end_date__gte=current_date)
    print('test:',access_rights)
    return access_rights.exists()

def check_card_person(card : Card | None, employee : Employee | None, gate : Gate | None, direction : int) -> Response:
    if not card:
        return Response({"denied": "Card not found."}, status=404)
    
    if not employee:
        return Response({"denied": "Employee not found."}, status=404)
    
    if not card.is_active:
        return Response({"denied": "Card is inactive."}, status=403)
    
    if card.valid_from > timezone.now().date() or card.valid_to < timezone.now().date():
        return Response({"denied": "Card is not valid at this time."}, status=403)
    
    if card.lock_until and card.lock_until > timezone.now():
        return Response({"denied": "Card is temporarily locked."}, status=403)
    
    if not check_access_rights(employee, gate, direction):
        return Response({"denied": "Access denied. No valid access rights for this gate."}, status=403)
    
    if random.randint(0, 99) == 1:
        card.lock_until = timezone.now() + timezone.timedelta(minutes=5)
        card.save()
        return Response({"denied" : {"control" : True}}, status=403)
    
    return Response({"message": "Card and person details are valid."}, status=200)