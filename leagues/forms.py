from django import forms
from django.apps import apps


class AdvanceSeasonForm(forms.Form):
    """
    Form for selecting how many weeks to advance the season.
    Bound form processed in AdvanceSeasonFormView.
    Unbound form initialized in advance_season_form context processor.
    """
    
    CHOICES = [
        ('initial', 'Advance'),
        (1, '1 Week'),
        (2, '2 Weeks'),
        (4, '4 Weeks'),
        (8, '8 Weeks'),
        ('Next', 'Next phase')
    ]
    advance = forms.ChoiceField(choices=CHOICES, required=True, label='')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Set <select> HTML attributes
        self.fields['advance'].widget.attrs={
            'class': 'form-select',
            'id': 'advance-select',
            'onchange': 'this.form.submit()'
        }
        

class TeamSelectForm(forms.Form):
    """
    Form for selecting the user-controlled team
    from a list of the current league's teams.
    Bound form processed in TeamSelectFormView.
    Unbound form initialized in TeamListView context.
    """
    team = forms.ModelChoiceField(queryset=None, label='',
                                  empty_label='--- Select a team ---',
                                  required=True)
    
    def __init__(self, *args, **kwargs):
        Team = apps.get_model('leagues.Team')       
        # pop() prevents __init__ from having too many args
        if kwargs.get('form_kwargs'): 
            # Unbound form in TeamListView - object in 'form_kwargs'
            form_kwargs = kwargs.pop('form_kwargs')
            league = form_kwargs['league']
            team = Team.objects.filter(league=league)
        else:
            # Bound form in TeamSelectFormView - slug in 'league' kwargs
            league = kwargs.pop('league')
            team = Team.objects.filter(league__slug=league)
            
        super().__init__(*args, **kwargs)
        
        # Set queryset and <select> HTML attributes
        self.fields['team'].queryset = team
        self.fields['team'].widget.attrs={
            'class': 'form-select mb-3',
            'id': 'team-select'
        }