from django.urls import path
from .views import ApproveAccessRightRequestView, CheckCardPersonView, login_view, SecurityZoneListView, EmployeeListView,AccessRightRequestView, AccessRightRequestListView, RegisterEmployee, MessageListView, DepartmentListView, SuperVisorListView,NewRegistrationsListView, ApproveEmployeeRegistrationView

urlpatterns = [ path("check_card_person/", CheckCardPersonView.as_view()),
                path("login/", login_view, name="api-login"),
                path("security_zones/", SecurityZoneListView.as_view(), name="api-security-zones"),
                path("employees/", EmployeeListView.as_view(), name="api-employees"),
                path("access_right_requests/", AccessRightRequestView.as_view(), name="api-access-right-requests"),
                path('access-right-requests/', AccessRightRequestListView.as_view()),
                path('access-right-requests/<int:pk>/approve/', ApproveAccessRightRequestView.as_view()),
                path("register-employee/", RegisterEmployee.as_view(), name="api-register-employee"),
                path("new-registrations/", NewRegistrationsListView.as_view(), name="api-new-registrations"),
                path("approve-registration/<int:pk>/", ApproveEmployeeRegistrationView.as_view(), name="api-approve-registration"),
                path("messages/", MessageListView.as_view(), name="api-messages"), 
                path("departments/", DepartmentListView.as_view(), name="api-departments"),
                path("supervisors/", SuperVisorListView.as_view(), name="api-supervisors"), 
]