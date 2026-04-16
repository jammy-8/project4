from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(required=False)

    class Meta:
        model = User
        fields = (
            'username',
            'first_name',
            'last_name',
            'email',
            'password1',
            'password2',
        )

class ProfileForm(forms.ModelForm):
    password1 = forms.CharField(
        widget=forms.PasswordInput,
        required=False,
        label='New Password'
    )

    password2 = forms.CharField(
        widget=forms.PasswordInput,
        required=False,
        label='Confirm New Password'
    )

    class Meta:
        model = User
        fields = ['username', 'email']

    def clean(self):
        cleaned = super().clean()

        p1 = cleaned.get('password1')
        p2 = cleaned.get('password2')

        if p1 or p2: 
            if p1 != p2:
                raise forms.ValidationError('Password mismatch')
            
        return cleaned
    
    def clean_username(self):
        username = self.cleaned_data.get('username')

        if User.objects.filter(username = username).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('Username has been taken')
        
        return username