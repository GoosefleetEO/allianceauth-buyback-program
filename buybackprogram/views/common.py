from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render

from allianceauth.services.hooks import get_extension_logger

from buybackprogram.models import Program

logger = get_extension_logger(__name__)


@login_required
@permission_required("buybackprogram.basic_access")
def index(request):
    context = {"programs": Program.objects.filter()}

    return render(request, "buybackprogram/index.html", context)
