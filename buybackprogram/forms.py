from django import forms

from buybackprogram.models import Program


class ProgramForm(forms.ModelForm):
    # specify the name of model to use
    class Meta:
        model = Program
        fields = "__all__"
