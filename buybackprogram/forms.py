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

    for m in marketgroups:
        print("market group")
        print(m)

        m.child_groups = m.market_group_children.all()

        for c in m.child_groups:
            print("child")
            print(c)
            c.child_groups = c.market_group_children.all()

            for d in c.child_groups:
                print("sub")
                print(d)
                d.child_groups = d.market_group_children.all()

    class Meta:
        model = ProgramItem
        fields = ("item_tax", "program")
