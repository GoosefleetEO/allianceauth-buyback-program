from django import forms

from buybackprogram.models import Program, ProgramItem


class ProgramForm(forms.ModelForm):
    # specify the name of model to use
    class Meta:
        model = Program
        fields = "__all__"


class ProgramItemForm(forms.ModelForm):
    class Meta:
        model = ProgramItem
        fields = "__all__"


class CalculatorForm(forms.Form):

    items = forms.CharField(
        widget=forms.Textarea,
        label="Items",
        help_text="Copy and paste the item data from your inventory. Item types not in this buyback program will be ignored",
    )

    def __init__(self, *args, items=None, **kwargs):
        super(CalculatorForm, self).__init__(*args, **kwargs)
