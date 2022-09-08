from django.conf import settings

from .utils import clean_setting

# put your app settings here


EXAMPLE_SETTING_ONE = getattr(settings, "EXAMPLE_SETTING_ONE", None)


# Hard timeout for tasks in seconds to reduce task accumulation during outages
BUYBACKPROGRAM_TASKS_TIME_LIMIT = clean_setting("BUYBACKPROGRAM_TASKS_TIME_LIMIT", 7200)

# Warning limit for Jita price updates if prices have not been updated
BUYBACKPROGRAM_PRICE_AGE_WARNING_LIMIT = clean_setting(
    "BUYBACKPROGRAM_PRICE_AGE_WARNING_LIMIT", 48
)

# Tracking number tag
BUYBACKPROGRAM_TRACKING_PREFILL = clean_setting(
    "BUYBACKPROGRAM_TRACKING_PREFILL", "aa-bbp"
)

BUYBACKPROGRAM_PRICE_SOURCE_ID = clean_setting(
    "BUYBACKPROGRAM_PRICE_SOURCE_ID", 60003760
)

BUYBACKPROGRAM_PRICE_SOURCE_NAME = clean_setting(
    "BUYBACKPROGRAM_PRICE_SOURCE_NAME", "Jita"
)

BUYBACKPROGRAM_PRICE_METHOD = clean_setting(
    "BUYBACKPROGRAM_PRICE_METHOD", "Fuzzwork"
)

BUYBACKPROGRAM_PRICE_JANICE_API_KEY = clean_setting(
    "BUYBACKPROGRAM_PRICE_JANICE_API_KEY", ""
)



def allianceauth_discordbot_active():
    """
    check if allianceauth-dicordbot is installed and active
    :return:
    """
    return "aadiscordbot" in settings.INSTALLED_APPS


def aa_discordnotify_active():
    """
    check if allianceauth-dicordbot is installed and active
    :return:
    """
    return "discordnotify" in settings.INSTALLED_APPS
