from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()

class UserRegisterForm(forms.ModelForm):
    password = forms.CharField(label='Password')

    class Meta:
        model = User
        fields = [
            'email',
            'password',
            'username',
        ]

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')

        if not password:
            raise forms.ValidationError('Password is required.')

        if len(password) < 5:
            raise forms.ValidationError('Your password should have more than 5 characters.')

        return cleaned_data

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('This email is already registered.')
        return email
