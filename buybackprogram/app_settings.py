from django.conf import settings

from .utils import clean_setting

# put your app settings here


EXAMPLE_SETTING_ONE = getattr(settings, "EXAMPLE_SETTING_ONE", None)


# Hard timeout for tasks in seconds to reduce task accumulation during outages
BUYBACKPROGRAM_TASKS_TIME_LIMIT = clean_setting("BUYBACKPROGRAM_TASKS_TIME_LIMIT", 7200)

# Tracking number tag
BUYBACKPROGRAM_TRACKING_PREFILL = clean_setting(
    "BUYBACKPROGRAM_TRACKING_PREFILL", "aa-bbp"
)
