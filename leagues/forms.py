from django import forms
from django.apps import apps


class AdvanceSeasonForm(forms.Form):
    """Form for selecting how many weeks to advance the season"""
    
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
        

class TeamSelectForm(forms.Form):
    """Form for selecting the user-controlled team"""
    
    team = forms.ModelChoiceField(queryset=None, label='', empty_label='--- Select a team ---')
    
    def __init__(self, *args, **kwargs):
        Team = apps.get_model('leagues.Team')
        if kwargs.get('form_kwargs'): 
            league = kwargs.pop('form_kwargs')
            league = league['league']
            team = Team.objects.filter(league=league)
        else:
            league = kwargs.pop('league')
            team = Team.objects.filter(league__slug=league)
            
        super().__init__(*args, **kwargs)
        
        self.fields['team'].queryset = team
        self.fields['team'].widget.attrs={
            'class': 'form-select mb-3',
            'id': 'team-select'
        }