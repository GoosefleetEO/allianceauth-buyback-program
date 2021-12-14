from django import forms
from django.core.validators import MaxValueValidator, MinValueValidator

from buybackprogram.models import Owner, Program, ProgramItem


class ProgramForm(forms.ModelForm):
    # specify the name of model to use
    class Meta:
        model = Program
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)

        super(ProgramForm, self).__init__(*args, **kwargs)
        self.fields["owner"].queryset = Owner.objects.filter(user=self.user)


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
    donation = forms.IntegerField(
        label="Donation %",
        initial=0,
        help_text="You can set a optional donation percentage on your contract",
        validators=[MaxValueValidator(100), MinValueValidator(0)],
    )

    def __init__(self, *args, items=None, **kwargs):
        program = kwargs.pop("program", None)
        # TODO: remove this error
        print(program)
        super(CalculatorForm, self).__init__(*args, **kwargs)
