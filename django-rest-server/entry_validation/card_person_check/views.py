from rest_framework.views import APIView, Response
from .models import Card, GateEvent, Gate, AccessRightRequest, SecurityZone, Employee, Message
from .check import check_card_person
from django.contrib.auth import authenticate
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
# Create your views here.

class CheckCardPersonView(APIView):
    def post(self, request):
        self.post_data = request.data
        card_number = self.post_data.get('card_number')
        card = Card.objects.filter(card_number=card_number).first()      
        direction = self.post_data.get('direction', 0)
        employee = card.employee if card else None
        gate=self.post_data.get('gate', 0)
        gate_obj = Gate.objects.filter(gate_number=gate).first()
        response = check_card_person(card, employee, gate_obj, direction)
        if card is None:
            warning = f"Foreign card!! {card_number}"  
        else:
            warning = response.data.get("denied") if response.status_code != 200 else None
        denied = response.data.get("denied")
        control = False
        allowed = response.status_code == 200
        if denied and isinstance(denied, dict):
            control = denied.get("control", False)
        gate_event = GateEvent(
            gate=gate_obj,
            card=card,
            timestamp=self.post_data.get('timestamp'),
            control=control,
            allowed=allowed,
            warning=warning if not None else None,
            from_zone = gate_obj.outside_zone if direction == 0 else gate_obj.inside_zone,
            to_zone = gate_obj.inside_zone if direction == 0 else gate_obj.outside_zone
            )
        employee.current_zone = gate_event.to_zone if allowed else employee.current_zone
        employee.save()
        gate_event.save()
        return response

class AccessRightRequestView(APIView):
    def post(self, request):
        data = request.data
        security_zone = data.get('security_zone')
        created_at =data.get('created_at')
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        employee = data.get('employee')
        access_request = AccessRightRequest(
            security_zone=SecurityZone.objects.get(id=security_zone),
            created_at=created_at,
            start_date=start_date,
            end_date=end_date,
            employee=Employee.objects.get(id=employee),
            approved=False
        )
        access_request.save()
        try:
            return Response({"message": "Access right request created successfully."}, status=201)
        except Exception as e:
            return Response({"error": str(e)}, status=400)

class SecutityZoneListView(APIView):
    def get(self, request):
        security_zones = SecurityZone.objects.all()
        data = [{"id": zone.id, "name": zone.name} for zone in security_zones]
        return Response(data)

class EmployeeListView(APIView):
    def get(self, request):
        employees = Employee.objects.all()
        data = [{"id": emp.id, "name": emp.firstname + " " + emp.lastname} for emp in employees]
        return Response(data)

@api_view(['POST'])
@permission_classes([AllowAny]) # Allows anyone to access the login page
def login_view(request):
    # Extract username and password from the Vue JSON request
    username = request.data.get('username')
    password = request.data.get('password')

    # Django's built-in authenticate function checks if the credentials are correct
    user = authenticate(username=username, password=password)

    if user is not None and user.is_active:
        # Get the existing token for the user, or create a new one if it doesn't exist
        token, created = Token.objects.get_or_create(user=user)
        
        # Return the token in the exact JSON format the Vue frontend expects
        return Response({'token': token.key}, status=status.HTTP_200_OK)
    else:
        # Return an error status which will trigger the 'catch' block in Vue
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

class RegisterEmployee(APIView):
    def post(self, request):
        data = request.data
        firstname = data.get('firstname')
        lastname = data.get('lastname')
        date_of_birth = data.get('date_of_birth')
        hr_id = Employee.objects.last().hr_id + 1 if Employee.objects.exists() else 1
        department = data.get('department')
        password = data.get('password')
        employee = Employee.objects.create_user(
            hr_id=hr_id,
            password=password,
            firstname=firstname,
            lastname=lastname,
            date_of_birth=date_of_birth,
            department=department
        )
        employee.save()
        message = Message.objects.create(
            employee=employee,
            content=f"Welcome {employee.firstname}! Your employee account has been created successfully. Your HR ID is {employee.hr_id}. Please contact your administrator to activate your account and assign access rights."
        )
        message.save()

        try:
            return Response({"message": "Employee registered successfully."}, status=201)
        except Exception as e:
            return Response({"error": str(e)}, status=400)

class MessageListView(APIView):
    def get(self, request):
        messages = Message.objects.filter(employee_id=request.query_params.get('employee_id')).order_by('-created_at')
        data = [{"id": msg.id, "content": msg.content, "is_read": msg.is_read, "created_at": msg.created_at} for msg in messages]
        return Response(data)
    def post(self, request):
        is_read = request.data.get('is_read', False)
        message = Message.objects.filter(id=request.data.get('id')).first()
        if message:
            message.is_read = is_read
            message.save()
            return Response({"message": "Message updated successfully."}, status=200)