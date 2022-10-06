from django import forms


class AdvanceSeasonForm(forms.Form):
    """
    Form for selecting how many weeks to advance the season.
    Bound form processed in AdvanceSeasonFormView.
    Unbound form initialized in advance_season_form context processor.
    """

    CHOICES = [
        ("initial", "Advance"),
        (1, "1 Week"),
        (2, "2 Weeks"),
        (4, "4 Weeks"),
        (8, "8 Weeks"),
        ("Next", "Next phase"),
    ]
    advance = forms.ChoiceField(choices=CHOICES, required=True, label="")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Set <select> HTML attributes
        self.fields["advance"].widget.attrs = {
            "class": "form-select",
            "id": "advance-select",
            "onchange": "this.form.submit()",
        }
