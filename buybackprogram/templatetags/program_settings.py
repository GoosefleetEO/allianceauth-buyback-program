from django import template

from buybackprogram.models import ProgramItem

register = template.Library()


def setting_icons(option, program):
    icons = {
        "all_items": {
            "icon": "fa-globe-europe",
            "color": False,
            "message": "This program accepts all types of items.",
        },
        "fuel_cost": {
            "icon": "fa-truck",
            "color": False,
            "message": "Items sold via this program have an added freight cost of %s ISK per m³"
            % program.hauling_fuel_cost,
        },
        "price_dencity_modifier": {
            "icon": "fa-compress-arrows-alt",
            "color": False,
            "message": "Items with price dencity bellow {} isk/m³ will have an additional {} % tax on them.".format(
                program.price_dencity_treshold, program.price_dencity_tax
            ),
        },
        "compressed": {
            "icon": "fa-file-archive",
            "color": False,
            "message": "Compressed price is taken into account when calculating values for ores.",
        },
        "refined": {
            "icon": "fa-industry",
            "color": False,
            "message": "Refined price is taken into account when calculating values for ores.",
        },
        "raw_ore": {
            "icon": "fa-icicles",
            "color": False,
            "message": "Raw price is taken into account when calculating values for ores.",
        },
        "unpacked": {
            "icon": "fa-box-open",
            "color": False,
            "message": "Unpacked items are accepted in this program.",
        },
        "special_items": {
            "icon": "fa-search-dollar",
            "color": False,
            "message": "This program has individual items with adjusted taxes or items that are not allowed in the program.",
        },
    }

    return icons[option]


@register.filter
def program_setting(program):

    settings = []

    program_items = ProgramItem.objects.filter(program=program)

    if program.allow_all_items:
        setting = setting_icons("all_items", program)

        settings.append(setting)

    if program.hauling_fuel_cost:
        setting = setting_icons("fuel_cost", program)

        settings.append(setting)

    if program.price_dencity_modifier:
        setting = setting_icons("price_dencity_modifier", program)

        settings.append(setting)

    if program.use_compressed_value:
        setting = setting_icons("compressed", program)

        settings.append(setting)

    if program.use_refined_value:
        setting = setting_icons("refined", program)

        settings.append(setting)

    if program.use_raw_ore_value:
        setting = setting_icons("raw_ore", program)

        settings.append(setting)

    if program.allow_unpacked_items:
        setting = setting_icons("unpacked", program)

        settings.append(setting)

    if program_items:
        setting = setting_icons("special_items", program)

        settings.append(setting)

    return settings
