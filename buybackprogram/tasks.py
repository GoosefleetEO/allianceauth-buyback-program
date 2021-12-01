from datetime import date

import requests
from celery import shared_task

from django.db import Error
from eveuniverse.models import EveType

from allianceauth.services.hooks import get_extension_logger

from buybackprogram.models import ItemPrices

logger = get_extension_logger(__name__)


@shared_task
def update_all_prices():

    i = 0
    type_ids = []

    typeids = EveType.objects.values_list("id", flat=True).filter(published=True)

    for item in typeids:
        type_ids.append(item)

        i += 1

        if i == 1000:

            response_fuzzwork = requests.get(
                "https://market.fuzzwork.co.uk/aggregates/",
                params={
                    "types": ",".join([str(x) for x in type_ids]),
                    "station": 60003760,
                },
            )

            items_fuzzwork = response_fuzzwork.json()

            for key, i in items_fuzzwork.items():

                objs = [
                    ItemPrices(
                        id=key,
                        eve_type_id=key,
                        buy=int(float(i["buy"]["max"])),
                        sell=int(float(i["sell"]["min"])),
                        updated=date.today(),
                    )
                ]

            try:
                ItemPrices.objects.bulk_update(
                    objs, ["buy", "sell", "updated", "eve_type_id"]
                )
            except Error as e:
                logger.debug("Error with bulk create: %s" % e)

            i = 0
            type_ids.clear()

    return "Updated prices for buybackprogram"


# from buybackprogram.tasks import update_all_prices
