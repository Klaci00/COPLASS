from .models import Card, Employee
from datetime import timezone
from rest_framework.response import Response

def check_card_person(card : Card | None, employee : Employee | None) -> Response:
    if not card:
        return Response({"error": "Card not found."}, status=404)
    
    if not employee:
        return Response({"error": "Employee not found."}, status=404)
    
    if not card.is_active:
        return Response({"error": "Card is inactive."}, status=403)
    
    if card.valid_from > timezone.now().date() or card.valid_to < timezone.now().date():
        return Response({"error": "Card is not valid at this time."}, status=403)
    
    
    return Response({"message": "Card and person details are valid."}, status=200)