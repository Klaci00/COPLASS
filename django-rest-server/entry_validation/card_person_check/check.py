import random
from .models import Card, Employee
from django.utils import timezone
from rest_framework.response import Response

def check_card_person(card : Card | None, employee : Employee | None) -> Response:
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
    
    if random.randint(0, 1) == 1:
        card.lock_until = timezone.now() + timezone.timedelta(minutes=5)
        card.save()
        return Response({"denied" : {"control" : True}}, status=403)
    
    return Response({"message": "Card and person details are valid."}, status=200)