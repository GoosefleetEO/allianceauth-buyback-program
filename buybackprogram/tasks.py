import requests
from celery import shared_task

from django.db import Error
from django.utils import timezone

from allianceauth.services.hooks import get_extension_logger

from buybackprogram.models import ItemPrices

logger = get_extension_logger(__name__)


@shared_task
def update_all_prices():

    i = 0
    type_ids = []
    market_data = {}

    # Get all type ids
    prices = ItemPrices.objects.all()

    logger.debug("Price setup starting for %s items from Fuzzworks API" % len(prices))

    # Build suitable bulks to fetch prices from API
    for item in prices:
        type_ids.append(item.eve_type_id)

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
            market_data.update(items_fuzzwork)

            i = 0
            type_ids.clear()

    # Get leftover data from the bulk
    response_fuzzwork = requests.get(
        "https://market.fuzzwork.co.uk/aggregates/",
        params={
            "types": ",".join([str(x) for x in type_ids]),
            "station": 60003760,
        },
    )

    items_fuzzwork = response_fuzzwork.json()
    market_data.update(items_fuzzwork)

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
        logger.errro("Error updating prices: %s" % e)


# from buybackprogram.tasks import update_all_prices
