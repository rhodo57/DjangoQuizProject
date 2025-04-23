from django import forms
from django.forms.widgets import RadioSelect, CheckboxSelectMultiple
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .models import OdproUser

class QuestionForm(forms.Form):
    def __init__(self, multi, choices, *args, **kwargs):
        super(QuestionForm, self).__init__(*args, **kwargs)
        if multi is True:
            self.fields["answers"] = forms.MultipleChoiceField(
                choices=choices,
                widget=CheckboxSelectMultiple)
        else:
            self.fields["answers"] = forms.ChoiceField(
                choices=choices,
                widget=RadioSelect)

class EmailAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={"autofocus": True})
    )

class UserRegistrationForm(UserCreationForm):
    class Meta:
        model = OdproUser
        fields = ['email', 'username']  # Password fields are included by the base class
