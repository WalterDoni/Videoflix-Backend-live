from django.urls import path
from . import views
from .views import send_email

urlpatterns = [
    path('verify-email-confirm/<uidb64>/<token>/', views.verify_email_confirm, name='verify-email-confirm'),
    path('verify-email/complete/', views.verify_email_complete, name='verify-email-complete'),
    path('send-email/', send_email, name='send-email'),
]