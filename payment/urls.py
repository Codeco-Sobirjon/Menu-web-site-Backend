from django.urls import path
from payment.views import *


urlpatterns = [
    path('create_card/',VirifyCardView.as_view()),
    path('paycom/<uuid:unique_id>/', Payment.as_view())
]
