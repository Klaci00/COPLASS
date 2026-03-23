import random
from rest_framework.views import APIView
from .models import Card, GateEvent
from .check import check_card_person

# Create your views here.

class CheckCardPersonView(APIView):
    def post(self, request):
        self.post_data = request.data
        card_number = self.post_data.get('card_number')
        card = Card.objects.filter(card_number=card_number).first()
        employee = card.employee if card else None
        response = check_card_person(card, employee)
        denied = response.data.get("denied")
        if denied and isinstance(denied, dict):
            control = denied.get("control", False)
        if card and employee:
            gate_event = GateEvent(
                gate=self.post_data.get('gate', 0),
                card=card,
                timestamp=self.post_data.get('timestamp'),
                control=control
            )
            gate_event.save()
        return response
