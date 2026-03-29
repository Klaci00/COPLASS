from django.urls import path
from .views import CheckCardPersonView, login_view, SecurityZoneListView, EmployeeListView,AccessRightRequestView, RegisterEmployee, MessageListView

urlpatterns = [ path("check_card_person/", CheckCardPersonView.as_view()),
               path("login/", login_view, name="api-login"),
               path("security_zones/", SecurityZoneListView.as_view(), name="api-security-zones"),
               path("employees/", EmployeeListView.as_view(), name="api-employees"),
               path("access_right_requests/", AccessRightRequestView.as_view(), name="api-access-right-requests"),
               path("register_employee/", RegisterEmployee.as_view(), name="api-register-employee"),
                path("messages/", MessageListView.as_view(), name="api-messages"),  
]