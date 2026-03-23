from django.urls import path
from .views import CheckCardPersonView

urlpatterns = [ path("check_card_person/", CheckCardPersonView.as_view())
]