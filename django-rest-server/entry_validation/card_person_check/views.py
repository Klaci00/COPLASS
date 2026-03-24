from rest_framework.views import APIView
from .models import Card, GateEvent, Gate
from .check import check_card_person

# Create your views here.

class CheckCardPersonView(APIView):
    def post(self, request):
        self.post_data = request.data
        card_number = self.post_data.get('card_number')
        card = Card.objects.filter(card_number=card_number).first()
        if card is None:
            warning = f"Foreign card!! {card_number}"           
        employee = card.employee if card else None
        response = check_card_person(card, employee)
        denied = response.data.get("denied")
        control = False
        allowed = response.status_code == 200
        if denied and isinstance(denied, dict):
            control = denied.get("control", False)
        gate=self.post_data.get('gate', 0)
        gate_obj = Gate.objects.filter(gate_number=gate).first()
        direction = self.post_data.get('direction', 0)
        gate_event = GateEvent(
            gate=gate_obj,
            card=card,
            timestamp=self.post_data.get('timestamp'),
            control=control,
            allowed=allowed,
            warning=warning if not allowed else None,
            from_zone = gate_obj.outside_zone if direction == 0 else gate_obj.inside_zone,
            to_zone = gate_obj.inside_zone if direction == 0 else gate_obj.outside_zone
            )
        gate_event.save()
        return response
