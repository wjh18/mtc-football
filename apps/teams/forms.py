from django import forms

from .models import Team


class TeamSelectForm(forms.Form):
    """
    Form for selecting the user-controlled team
    from a list of the current league's teams.
    Bound form processed in TeamSelectFormView.
    Unbound form initialized in TeamListView context.
    """

    team = forms.ModelChoiceField(
        queryset=None, label="", empty_label="--- Select a team ---", required=True
    )

    def __init__(self, *args, **kwargs):
        # pop() prevents __init__ from having too many args
        if kwargs.get("form_kwargs"):
            # Unbound form in TeamListView - object in 'form_kwargs'
            form_kwargs = kwargs.pop("form_kwargs")
            league = form_kwargs["league"]
            team = Team.objects.filter(league=league)
        else:
            # Bound form in TeamSelectFormView - slug in 'league' kwargs
            league = kwargs.pop("league")
            team = Team.objects.filter(league__slug=league)

        super().__init__(*args, **kwargs)

        # Set queryset and <select> HTML attributes
        self.fields["team"].queryset = team
        self.fields["team"].widget.attrs = {
            "class": "form-select mb-3",
            "id": "team-select",
        }
