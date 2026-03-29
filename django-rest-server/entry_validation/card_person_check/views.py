from rest_framework.views import APIView, Response
from .models import Card, GateEvent, Gate, AccessRightRequest, SecurityZone, Employee, Message
from .check import check_card_person
from django.contrib.auth import authenticate
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from .serializers import (CheckCardPersonSerializer, 
                          AccessRightRequestSerializer, 
                          SecurityZoneSerializer,
                          EmployeeListSerializer,
                          RegisterEmployeeSerializer,
                          MessageSerializer,
                          MessageUpdateSerializer
                          )
from django.db import models

class CheckCardPersonView(APIView):
    def post(self, request):
        serializer = CheckCardPersonSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        card     = Card.objects.filter(card_number=data['card_number']).first()
        employee = card.employee if card else None
        gate_obj = Gate.objects.filter(gate_number=data['gate']).first()
        direction = data['direction']
        result = check_card_person(card, employee, gate_obj, direction)

        if not result.allowed:
            denied_payload = {"control": True} if result.control else result.message
            response = Response({"denied": denied_payload}, status=result.status_code)
        else:
            response = Response({"message": "Access granted."}, status=200)
        gate_event = GateEvent(
            gate=gate_obj,
            card=card,
            timestamp=data['timestamp'],
            control=result.control,
            allowed=result.allowed,
            warning=result.message if not result.allowed else None,
            from_zone=gate_obj.outside_zone if direction == 0 else gate_obj.inside_zone,
            to_zone=gate_obj.inside_zone   if direction == 0 else gate_obj.outside_zone,
        )
        gate_event.save()

        if employee:
            employee.current_zone = gate_event.to_zone if result.allowed else employee.current_zone
            employee.save()

        return response


class AccessRightRequestView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        serializer = AccessRightRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            serializer.save()
            return Response({"message": "Access right request created successfully."}, status=201)
        except Exception as e:
            return Response({"error": str(e)}, status=400)

class AccessRightRequestListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.is_staff:
            # Supervisor sees requests assigned to them + their own requests
            requests = AccessRightRequest.objects.filter(
                models.Q(supervisor=user) | models.Q(employee=user)
            ).distinct().order_by('-created_at')
        else:
            # Regular employee sees only their own requests
            requests = AccessRightRequest.objects.filter(
                employee=user
            ).order_by('-created_at')

        return Response(AccessRightRequestSerializer(requests, many=True).data)


class ApproveAccessRightRequestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        if not request.user.is_staff:
            return Response({"error": "Permission denied."}, status=403)

        access_request = AccessRightRequest.objects.filter(pk=pk).first()
        if not access_request:
            return Response({"error": "Request not found."}, status=404)
        if access_request.approved:
            return Response({"error": "Already approved."}, status=400)

        # Ensure the supervisor can only approve requests assigned to them
        if access_request.supervisor != request.user:
            return Response({"error": "You are not the supervisor for this request."}, status=403)

        access_request.approve()
        return Response({"message": "Request approved successfully."}, status=200)

class SecurityZoneListView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        zones = SecurityZone.objects.all()
        return Response(SecurityZoneSerializer(zones, many=True).data)

class EmployeeListView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        employees = Employee.objects.all()
        return Response(EmployeeListSerializer(employees, many=True).data)

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
        return Response({'token': token.key, 'is_staff': user.is_staff, 'user_name': f"{user.firstname} {user.lastname}", 'hr_id': username}, status=status.HTTP_200_OK)
    else:
        # Return an error status which will trigger the 'catch' block in Vue
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

class RegisterEmployee(APIView):
    def post(self, request):
        serializer = RegisterEmployeeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            employee = serializer.save()
            Message.objects.create(
                employee=employee,
                content=(
                    f"Welcome {employee.firstname}! Your account has been created. "
                    f"Your HR ID is {employee.hr_id}. "
                    f"Please contact your administrator to activate your account."
                )
            )
            return Response({"message": "Employee registered successfully."}, status=201)
        except Exception as e:
            return Response({"error": str(e)}, status=400)

class MessageListView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        messages = Message.objects.filter(
            employee_id=request.query_params.get('employee_id')
        ).order_by('-created_at')
        return Response(MessageSerializer(messages, many=True).data)

    def post(self, request):
        serializer = MessageUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data    = serializer.validated_data
        message = Message.objects.get(id=data['id'])
        message.is_read = data['is_read']
        message.save()
        return Response({"message": "Message updated successfully."}, status=200)