from django import forms
from eveuniverse.models import EveMarketGroup

from buybackprogram.models import Program, ProgramItem


class ProgramForm(forms.ModelForm):
    # specify the name of model to use
    class Meta:
        model = Program
        fields = "__all__"


class ProgramItemForm(forms.ModelForm):
    marketgroups = EveMarketGroup.objects.filter(parent_market_group_id__isnull=True)

    def get_market_children(parent):
        for children in parent:
            return children.market_group_children.all()

    for l1 in marketgroups:

        l1.child_groups = l1.market_group_children.all()

        for l2 in l1.child_groups:

            l2.child_groups = l2.market_group_children.all()

            for l3 in l2.child_groups:

                l3.child_groups = l3.market_group_children.all()

                for l4 in l3.child_groups:

                    l4.child_groups = l4.market_group_children.all()

                    for l5 in l4.child_groups:

                        l5.child_groups = l5.market_group_children.all()

    class Meta:
        model = ProgramItem
        fields = ("item_tax", "program")
