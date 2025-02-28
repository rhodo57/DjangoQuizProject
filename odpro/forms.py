from django import forms
from django.forms.widgets import RadioSelect, CheckboxSelectMultiple


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
