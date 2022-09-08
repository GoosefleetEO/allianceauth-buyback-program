import requests
from bravado.exception import HTTPBadGateway, HTTPGatewayTimeout, HTTPServiceUnavailable
from celery import shared_task

from django.db import Error
from django.utils import timezone
from eveuniverse.models import EveMarketPrice

from allianceauth.services.hooks import get_extension_logger
from allianceauth.services.tasks import QueueOnce

from buybackprogram.app_settings import (
    BUYBACKPROGRAM_PRICE_SOURCE_ID,
    BUYBACKPROGRAM_PRICE_SOURCE_NAME,
    BUYBACKPROGRAM_PRICE_METHOD,
    BUYBACKPROGRAM_PRICE_JANICE_API_KEY,
)
from buybackprogram.models import ItemPrices, Owner

from .app_settings import BUYBACKPROGRAM_TASKS_TIME_LIMIT

logger = get_extension_logger(__name__)

NORMAL_TASK_PRIORITY = 4

# Create your tasks here
TASK_DEFAULT_KWARGS = {
    "time_limit": BUYBACKPROGRAM_TASKS_TIME_LIMIT,
}

TASK_ESI_KWARGS = {
    **TASK_DEFAULT_KWARGS,
    **{
        "bind": True,
        "autoretry_for": (
            OSError,
            HTTPBadGateway,
            HTTPGatewayTimeout,
            HTTPServiceUnavailable,
        ),
        "retry_kwargs": {"max_retries": 3},
        "retry_backoff": 30,
    },
}

def get_bulk_prices(type_ids):
    r = None
    if BUYBACKPROGRAM_PRICE_METHOD == "Fuzzwork":
        r = requests.get(
            "https://market.fuzzwork.co.uk/aggregates/",
            params={
                "types": ",".join([str(x) for x in type_ids]),
                "station": BUYBACKPROGRAM_PRICE_SOURCE_ID,
            },
        ).json()
    elif BUYBACKPROGRAM_PRICE_METHOD == "Janice":
        r = response_janice = requests.post(
            "https://janice.e-351.com/api/rest/v2/pricer?market=2",
            data = "\n".join([str(x) for x in type_ids]),
            headers={'Content-Type': 'text/plain', 'X-ApiKey': 'G9KwKq3465588VPd6747t95Zh94q3W2E', 'accept': 'application/json'}
        ).json()
        # Make Janice data look like Fuzzworks
        output = {}
        for item in r:
            output[str(item["itemType"]["eid"])] = {
                    "buy": {"max": str(item["top5AveragePrices"]["buyPrice5DayMedian"])},
                    "sell": {"min": str(item["top5AveragePrices"]["sellPrice5DayMedian"])}
                    }
        r = output
    else:
        raise f"Unknown pricing method: {BUYBACKPROGRAM_PRICE_METHOD}"

    return r



@shared_task
def update_all_prices():

    i = 0
    type_ids = []
    market_data = {}

    # Get all type ids
    prices = ItemPrices.objects.all()

    if BUYBACKPROGRAM_PRICE_METHOD == "Fuzzwork":
        logger.debug(
            "Price setup starting for %s items from Fuzzworks API from station id %s (%s), this may take up to 30 seconds..."
            % (
                len(typeids),
                BUYBACKPROGRAM_PRICE_SOURCE_ID,
                BUYBACKPROGRAM_PRICE_SOURCE_NAME,
            )
        )
    elif BUYBACKPROGRAM_PRICE_METHOD == "Janice":
        logger.debug(
            "Price setup starting for %s items from Janice API for Jita 4-4, this may take up to 30 seconds..."
            % (
                len(typeids),
            )
        )
    else:
        logger.error( "Unknown pricing method: '%s', skipping" % BUYBACKPROGRAM_PRICE_METHOD)
        return


    # Build suitable bulks to fetch prices from API
    for item in prices:
        type_ids.append(item.eve_type_id)

        if len(type_ids) == 1000:
            market_data.update(get_bulk_prices(type_ids))
            type_ids.clear()

    # Get leftover data from the bulk
    market_data.update(get_bulk_prices(type_ids))

    logger.debug("Market data fetched, starting database update...")
    for price in prices:

        buy = int(float(market_data[str(price.eve_type_id)]["buy"]["max"]))
        sell = int(float(market_data[str(price.eve_type_id)]["sell"]["min"]))

        price.buy = buy
        price.sell = sell
        price.updated = timezone.now()

    try:
        ItemPrices.objects.bulk_update(prices, ["buy", "sell", "updated"])
        logger.debug("All prices succesfully updated")
    except Error as e:
        logger.error("Error updating prices: %s" % e)

    EveMarketPrice.objects.update_from_esi()

    logger.debug("Updated all eveuniverse market prices.")


@shared_task(
    **{
        **TASK_ESI_KWARGS,
        **{
            "base": QueueOnce,
            "once": {"keys": ["owner_pk"], "graceful": True},
            "max_retries": None,
        },
    }
)
def update_contracts_for_owner(self, owner_pk):
    """fetches all contracts for owner from ESI"""

    return _get_owner(owner_pk).update_contracts_esi()


@shared_task(**TASK_DEFAULT_KWARGS)
def update_all_contracts():
    logger.debug("Starting all contract updates")
    for owner in Owner.objects.all():
        logger.debug("Updating contracts for %s" % owner)
        update_contracts_for_owner.apply_async(
            kwargs={"owner_pk": owner.pk},
            priority=NORMAL_TASK_PRIORITY,
        )


def _get_owner(owner_pk: int) -> Owner:
    """returns the owner or raises exception"""
    try:
        owner = Owner.objects.get(pk=owner_pk)
    except Owner.DoesNotExist:
        raise Owner.DoesNotExist(
            "Requested owner with pk {} does not exist".format(owner_pk)
        )
    return owner
