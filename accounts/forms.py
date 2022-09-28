from allauth.account.forms import LoginForm, SignupForm
from django import forms
from django.contrib.auth.forms import (PasswordChangeForm,
                                       PasswordResetForm, SetPasswordForm)
from django.contrib.auth.models import User

from accounts.models import Profile
from utils.forms import update_fields_widget, init_town


class CustomUserCreationForm(SignupForm):
    field_order = ('username', 'email', 'password1', 'password2',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        update_fields_widget(self, ('username', 'email', 'password1', 'password2',), 'form-control')
        self.fields['username'].label = 'Логин'
        self.fields['email'].label = 'Email'
        self.fields['password2'].label = 'Подтверждение'


class CustomAuthenticationForm(LoginForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        update_fields_widget(self, ('login', 'password'), 'form-control')
        self.fields['login'].label = 'Логин или Email'
        self.fields['remember'].widget.attrs.update({'class': 'form-check-input'})


class CustomPasswordChangeForm(PasswordChangeForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        update_fields_widget(self, ('old_password', 'new_password1', 'new_password2'), 'form-control')


class CustomPasswordResetForm(PasswordResetForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        update_fields_widget(self, ('email',), 'form-control')


class CustomSetPasswordForm(SetPasswordForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        update_fields_widget(self, ('new_password1', 'new_password2',), 'form-control')


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'email',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        update_fields_widget(self, ('username', 'email',), 'form-control')

    def clean(self):
        cleaned_data = super().clean()
        email = self.cleaned_data.get('email')
        id = self.instance.id
        qs = User.objects.filter(email=email)
        if email and qs.exists():
            found = qs.first()
            if found.id != id:
                raise forms.ValidationError('Эта почта уже используется!')
        return cleaned_data


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('avatar', 'phone', 'country', 'town', 'role',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        update_fields_widget(self, ('avatar', 'phone',), 'form-control')
        init_town(self, kwargs)
        inst = kwargs.get('instance')
        if inst:
            user = inst.user
            if user.is_superuser:
                return
            i = 1 if user.is_staff else 2
            self.fields['role'].choices = Profile.USER_ROLE_CHOICES[i:]
