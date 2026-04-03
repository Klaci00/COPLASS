from multiprocessing.sharedctypes import Value

from rest_framework.views import APIView, Response
from .models import Card, Department, GateEvent, Gate, AccessRightRequest, SecurityZone, Employee, Message
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
                          MessageUpdateSerializer,
                          NewRegistrationsSerializer
                          )
from django.db import models
from django.db.models import Case, When, Value, BooleanField

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

        if user.is_supervisor:
            # Supervisor sees requests assigned to them + their own requests
            own_requests = models.Q(supervisor=user) | models.Q(employee=user)

            # Find supervisors who are out of office AND have this user as a deputy.
            # Since deputy is symmetrical, deputy=user matches both directions.
            absent_supervisors = Employee.objects.filter(
                is_supervisor=True,
                on_the_clock=False,
                deputy=user
            )
            supervisors_with_no_deputies = Employee.objects.filter(
                is_supervisor=True,deputy = None, on_the_clock=False )
            if supervisors_with_no_deputies.exists():
                super_super = supervisors_with_no_deputies.filter(supervisor = user)
                supervisor_coverage = models.Q(supervisor__in=super_super)
                
            # Include requests assigned to those absent supervisors
            deputy_coverage = models.Q(supervisor__in=absent_supervisors)

            requests = AccessRightRequest.objects.filter(
                own_requests | deputy_coverage | (  supervisor_coverage if supervisors_with_no_deputies.exists() else models.Q())
            ).distinct().order_by('-created_at')
            
            requests = requests.annotate(
                covered_as_deputy=Case(
                When(supervisor__in=absent_supervisors, then=Value(True)),
                    default=Value(False),
                    output_field=BooleanField()
                )
            )


        else:
            # Regular employee sees only their own requests
            requests = AccessRightRequest.objects.filter(
                employee=user
            ).order_by('-created_at')

        return Response(AccessRightRequestSerializer(requests, many=True).data)

class ApproveAccessRightRequestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        user = request.user

        if not user.is_supervisor:
            return Response({"error": "Permission denied."}, status=403)

        access_request = AccessRightRequest.objects.filter(pk=pk).first()
        if not access_request:
            return Response({"error": "Request not found."}, status=404)
        if access_request.approved:
            return Response({"error": "Already approved."}, status=400)

        is_assigned_supervisor = access_request.supervisor == user

        # Deputy coverage: supervisor exists, is absent, and user is their deputy
        is_covering_deputy = (
            access_request.supervisor is not None
            and not access_request.supervisor.on_the_clock
            and access_request.supervisor.deputy.filter(pk=user.pk).exists()
        )
        is_covering_supervisor = (
            access_request.supervisor is not None and not access_request.supervisor.on_the_clock
            and access_request.supervisor.supervisor == user)

        if not is_assigned_supervisor and not is_covering_deputy and not is_covering_supervisor:
            return Response({"error": "You are not authorised to approve this request."}, status=403)

        # ✅ Single approval point
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
        return Response({'token': token.key,
                         'is_staff': user.is_staff,
                         'user_name': f"{user.firstname} {user.lastname}", 'hr_id': username,
                         'is_supervisor': user.is_supervisor,
                         'department': user.department.id},
                         status=status.HTTP_200_OK)
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

class DepartmentListView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        departments = Department.objects.all()
        return Response([{"id": dept.id, "name": dept.name} for dept in departments])

class SuperVisorListView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        dept = request.query_params.get('department')
        if dept:
            supervisors = Employee.objects.filter(is_supervisor=True, department__id=dept, on_the_clock=True)
            return Response([{"id": sup.id, "name": f"{sup.firstname} {sup.lastname}"} for sup in supervisors])
        else:
            return Response({"error": "Department ID is required."}, status=400)

class NewRegistrationsListView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user = request.user
        if not user.is_staff:
            return Response({"error": "Permission denied."}, status=403)
        new_employees = Employee.objects.filter(is_active=False, supervisor=user)
        return Response(NewRegistrationsSerializer(new_employees, many=True).data)

class ApproveEmployeeRegistrationView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, pk):
        user = request.user
        if not user.is_staff:
            return Response({"error": "Permission denied."}, status=403)
        employee = Employee.objects.filter(pk=pk, is_active=False, supervisor=user).first()
        if not employee:
            return Response({"error": "Employee not found or already active."}, status=404)
        employee.is_active = True
        employee.save()
        Message.objects.create(
            employee=employee,
            content=(
                f"Hello {employee.firstname}, your account has been approved and is now active. "
                f"You can start using your credentials to access the system."
            )
        )
        return Response({"message": "Employee registration approved successfully."}, status=200)