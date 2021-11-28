from django.contrib import admin

from .models import Location, Owner, Program, ProgramItem

# Register your models here.


@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ("owner", "is_corporation")


@admin.register(Owner)
class OwnerAdmin(admin.ModelAdmin):
    list_display = ("corporation", "character")


@admin.register(ProgramItem)
class ProgramItemAdmin(admin.ModelAdmin):
    list_display = ("program", "item_type")


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ("name", "eve_solar_system")
