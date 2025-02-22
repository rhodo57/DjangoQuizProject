from django import forms
from django.forms.widgets import RadioSelect, CheckboxSelectMultiple


class QuestionForm(forms.Form):
    def __init__(self, multi, choices, *args, **kwargs):
        super(QuestionForm, self).__init__(*args, **kwargs)
        myWidget = RadioSelect
        if multi is True:
            myWidget = CheckboxSelectMultiple
        self.fields["answers"] = forms.ChoiceField(
            choices=choices,
            widget=myWidget)
