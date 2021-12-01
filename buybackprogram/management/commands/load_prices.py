from django.core.management.base import BaseCommand
from eveuniverse.models import EveMarketGroup
from datetime import date
from django.db import IntegrityError, Error

import requests
from celery import shared_task

from eveuniverse.models import EveType

from allianceauth.services.hooks import get_extension_logger

from buybackprogram.models import ItemPrices

logger = get_extension_logger(__name__)

class Command(BaseCommand):
	help = "Preloads data required for the buyback program from ESI"

	def handle(self, *args, **options):
		i = 0
		type_ids = []
		market_data = []

		# Get all type ids 
		typeids = EveType.objects.values_list("id", flat=True).filter(published=True)[:1]

		# Build suitable bulks to fetch prices from API
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
				market_data.append(items_fuzzwork)

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
		market_data.append(items_fuzzwork)

		for objects in market_data:
			for key, value in objects.items():
				objs = [
					ItemPrices(
						eve_type_id=key,
						buy=int(float(value["buy"]["max"])),
						sell=int(float(value["sell"]["min"])),
						updated=date.today(),
					)
				]

				logger.debug('Building objs for %s' % key)

		try:
			ItemPrices.objects.bulk_create(objs)
		except IntegrityError as e:
			return 'Error: Prices already loaded into database, use price update task instead'
			logger.error('Prices already loaded into database, use price update task instead')

				

		return "Updated prices for buybackprogram"

# from buybackprogram.tasks import update_all_prices