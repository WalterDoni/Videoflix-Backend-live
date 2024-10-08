from django.shortcuts import render, redirect
from django.views import View
import json
from django.http import HttpResponse, JsonResponse
from rest_framework.authtoken.models import Token
from .models import CustomUser
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from .forms import UserRegisterForm
from django.contrib.auth import get_user_model,authenticate
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from .tokens import account_activation_token  
from django.core.mail import EmailMessage
from django.contrib import messages
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

#Reference for using the user model as User instead of CustomUser
User = get_user_model()

class SignupView(View):

    def post(self, request):
        data = json.loads(request.body)
        email = data.get('email')
        password = data.get('password')
        username = data.get('username')

        # Form validation with directly provided data
        form = UserRegisterForm(data={'email': email, 'password': password, 'username': username})
        
        if form.is_valid():
            email = form.cleaned_data.get('email')

            if User.objects.filter(email=email).exists():
                return JsonResponse({'error': 'Email already exists'}, status=409)
            if User.objects.filter(username=username).exists():
                return JsonResponse({'error': 'Username already exists'}, status=409)
            # Create user and authenticate
            user = form.save(commit=False)
            password = form.cleaned_data.get('password')
            user.set_password(password)
            user.save()

            # After successful registration, a verification email will be sent
            current_site = get_current_site(request)
            subject = "Bestätigungsmail"
            message = render_to_string('users/verify_email_message.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            email_message = EmailMessage(subject, message, to=[email])
            email_message.content_subtype = 'html'
            email_message.send()

            return JsonResponse({'message': 'User created successfully. Please check your email to verify your account.'}, status=201)

        else:
            errors = form.errors.as_data()
            error_message = ", ".join([f"{field}: {error[0].message}" for field, error in errors.items()])
            return JsonResponse({'error': f"Validation error: {error_message}"}, status=400)
    
# Verify a new account via email confirmation


def verify_email_confirm(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.email_is_verified = True
        user.save()
        messages.success(request, 'Your email has been verified.')
        return redirect('verify-email-complete')   
    else:
        messages.warning(request, 'The link is invalid.')
    return render(request, 'users/verify_email_confirm.html')

def verify_email_complete(request):
    return redirect('https://videoflix.walter-doni.at')

# -- end verify account

# Password reset - start

class PasswordResetRequestView(View):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        email = data.get('email')

        user = CustomUser.objects.filter(email=email).first()

        if user:
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            reset_link = f'https://videoflix.walter-doni.at/reset-password/{uid}/{token}'
            send_mail(
                'Setze dein Passwort zurück',
                f'Bitte klicke auf diesen Link, um dein Passwort zurückzusetzen: {reset_link}',
                'walter.doni1991@gmail.com',
                [user.email],
                fail_silently=False,
            )
            return JsonResponse({'message': 'Password reset email sent'}, status=200)
        else:
            return JsonResponse({'error': 'No user found with this email address'}, status=400)

class PasswordResetConfirmView(View):
    def post(self, request, uidb64, token):
        try:
          
            data = json.loads(request.body)
            new_password = data.get('new_password')
            
            if not isinstance(new_password, str):
                return JsonResponse({'error': 'Password must be a string'}, status=400)

            uid = force_str(urlsafe_base64_decode(uidb64))
            user = CustomUser.objects.get(pk=uid)
  
        except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
            user = None
       
        if user is not None and default_token_generator.check_token(user, token):
            user.set_password(new_password) 
            user.save()
            return JsonResponse({'message': 'Password has been reset'}, status=200)
        else:
            return JsonResponse({'error': 'Invalid link'}, status=400)

# Password reset - end
  
class LoginView(ObtainAuthToken):

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        # Authenticate user based on email
        try:
            user = User.objects.get(email=email)

            # Check if email is verified
            if not user.email_is_verified:
                return Response({'error': 'Email not verified.'}, status=400)

            # Check if the password is correct
            if not user.check_password(password):
                return Response({'error': 'Password is wrong.'}, status=400)

        except User.DoesNotExist:
            return Response({'error': 'Email does not exist.'}, status=400)

        # Create or retrieve token
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'email': user.email,
            'username': user.username
        })

class DeleteUserView(View):
    
    def delete(self, _ , pk):
        try:
            user = CustomUser.objects.get(pk=pk)
            user.delete()
            return HttpResponse({'message': 'User deleted'})
        except Exception as e:
            return JsonResponse({'error': str(e)})
        

class ChangeUserValuesView(View):
    
    def patch(self, request, pk):
        try:
            user = CustomUser.objects.get(pk=pk)
            data = json.loads(request.body)
            user.username = data.get('username', user.username)
            user.email = data.get('email', user.email)
            user.save()
            return JsonResponse({'message': 'User successfully changed'})
        except Exception as e:
            return JsonResponse({'error': str(e)})

class GetUsernameAndEmailByUrlID(View):
    def get(self,request,pk):
        try:
            user = User.objects.get(pk=pk)
            return JsonResponse({'username': user.username , 'email' : user.email})
        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found'})
    
    
def send_email(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email')
        name = data.get('name')
        title = data.get('title')
        message = data.get('message')

        send_mail(
            subject=title,
            message=f"Name: {name}\nEmail: {email}\nMessage: {message}",
            from_email='walter.doni1991@gmail.com',
            recipient_list=['walter.doni@gmx.at'],
        )
        return JsonResponse({'message': 'Email sent successfully'})

    return JsonResponse({'error': 'Invalid request method'}, status=400)