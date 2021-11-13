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
