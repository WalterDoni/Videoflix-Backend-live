from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from content.views import VideoView  
from user.views import *
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
urlpatterns = [
    path('admin/', admin.site.urls),
    path('video/', VideoView.as_view()), 
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', LoginView.as_view()),
    path('users/<int:pk>/', DeleteUserView.as_view(), name='user-delete'),
    path('users/<int:pk>/update/', ChangeUserValuesView.as_view(), name="user-update"),
    path('users/<int:pk>/username/', GetUsernameAndEmailByUrlID.as_view()),
    path('__debug__/', include("debug_toolbar.urls")),
    path('api-auth/', include('rest_framework.urls')),
    path('django-rq/', include('django_rq.urls')),
    
   
    path('verify-email-confirm/<uidb64>/<token>/', verify_email_confirm, name='verify-email-confirm'),
    path('verify-email/complete/', verify_email_complete, name='verify-email-complete'),
    path('send-email/', send_email, name='send-email'),
]

urlpatterns += staticfiles_urlpatterns()

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
