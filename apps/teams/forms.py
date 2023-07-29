from django import forms
from django.db.models import Q

from .models import Team


class TeamSelectForm(forms.Form):
    """
    Form for selecting the user-controlled team in a league.

    Bound form processed in TeamSelectFormView.
    Unbound form initialized in TeamListView context.
    """

    team = forms.ModelChoiceField(
        queryset=None, label="", empty_label="--- Select a team ---", required=True
    )

    def __init__(self, *args, **kwargs):
        form_kwargs = kwargs.pop("form_kwargs", None)
        if form_kwargs is not None:
            # Unbound form in TeamListView - league object from form_kwargs
            league = form_kwargs["league"]
            query = Q(league=league)
        else:
            # Bound form in TeamSelectFormView - league slug from URL kwargs
            league = kwargs.pop("league")
            query = Q(league__slug=league)

        team = Team.objects.filter(query)

        super().__init__(*args, **kwargs)

        # Set queryset and <select> HTML attributes
        self.fields["team"].queryset = team
        self.fields["team"].widget.attrs = {
            "class": "form-select mb-3",
            "id": "team-select",
        }
