from django import forms
from django.core.validators import MaxValueValidator, MinValueValidator
from eveuniverse.models import EveSolarSystem, EveType

from buybackprogram.models import Owner, Program


class ProgramForm(forms.ModelForm):
    # specify the name of model to use
    class Meta:
        model = Program
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)

        super(ProgramForm, self).__init__(*args, **kwargs)
        self.fields["owner"].queryset = Owner.objects.filter(user=self.user)


class ProgramItemForm(forms.Form):
    item_type = forms.ModelChoiceField(
        queryset=EveType.objects.none(),
        label="Item type",
        help_text="Add the name of item which you want to determine an tax on. Once you start typing, we offer suggestions",
        empty_label=None,
    )
    item_tax = forms.IntegerField(
        label="Tax amount",
        validators=[MaxValueValidator(100), MinValueValidator(0)],
        help_text="Set an tax on the item. If program default tax is defined this tax will be added on top of the program tax. If program does not allow all items this tax is used to calculate the tax for the product.",
    )
    disallow_item = forms.BooleanField(
        label="Disallow item in this program",
        help_text="If you want to prevent any prices to be given for this item in this program you can check this box.",
        required=False,
    )

    def __init__(self, *args, **kwargs):
        value = kwargs.pop("value", None)

        super(ProgramItemForm, self).__init__(*args, **kwargs)

        if value is not None:
            self.fields["item_type"].queryset = EveType.objects.filter(
                pk=value,
                published=True,
            ).exclude(eve_group__eve_category__id=9)


class LocationForm(forms.Form):
    eve_solar_system = forms.ModelChoiceField(
        queryset=EveSolarSystem.objects.none(),
        label="Solar system",
        help_text="Select solar system name. Start typing and we will give you suggestions.",
        empty_label=None,
    )
    name = forms.CharField(
        label="Structure/station name",
        help_text="A name or identification tag of the structure where the items should be contracted at.",
    )

    def __init__(self, *args, **kwargs):
        value = kwargs.pop("value", None)

        super(LocationForm, self).__init__(*args, **kwargs)

        if value is not None:
            self.fields["eve_solar_system"].queryset = EveSolarSystem.objects.filter(
                pk=value,
            )


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
