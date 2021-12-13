from django.contrib import admin

from .models import Contract, Location, Owner, Program, ProgramItem

# Register your models here.

admin.site.register(Program)

admin.site.register(Owner)

admin.site.register(ProgramItem)

admin.site.register(Location)

admin.site.register(Contract)
