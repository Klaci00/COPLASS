from django.urls import path
from .views import CheckCardPersonView, login_view

urlpatterns = [ path("check_card_person/", CheckCardPersonView.as_view()),
               path("login/", login_view, name="api-login"),
]