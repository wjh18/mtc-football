from django import forms
from django.forms import Form


class AdvanceSeasonForm(Form):
    CHOICES = [
        ('initial', 'Advance'),
        (1, '1 Week'),
        (2, '2 Weeks'),
        (4, '4 Weeks'),
        (8, '8 Weeks'),
        ('next', 'Next phase')
    ]
    advance = forms.ChoiceField(choices=CHOICES, required=True, label='')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['advance'].widget.attrs={
            'class': 'form-select',
            'id': 'advance-select',
            'onchange': 'this.form.submit()'
        }