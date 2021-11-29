from eveuniverse.models import EveType, EveCategory, EveTypeMaterial
from buybackprogram.models import ItemPrices, Owner, Program, ProgramItem

def get_refined_price(type_id, tax, refining_rate, disallowed_item):
	# Get eve material types for id
	typematerial = EveTypeMaterial.objects.filter(eve_type_id=type_id).values()

	# List for all materials
	materials = []

	notes = []

	# Process each material
	for material in typematerial:
		# Get material data
		data = EveType.objects.filter(id=material['material_eve_type_id']).first()
	    
		# Get material price
		price = ItemPrices.objects.filter(id=data.id).first()

		# Determine value for material
		if disallowed_item:
			value = 0

			note = {
				"error": "No price information in database."
			}

			notes.append(note)
	
		else:
			value = (100 - tax) / 100 * material['quantity'] * price.buy * (refining_rate / 100)


		# Build dictionary for material
		material_data = {
			"quantity" : material['quantity'],
			"type" : data,
			"price" : price,
			"value" : value,
			"note" : notes,
		}

		# Add material to the materials list
		materials.append(material_data)
	                                    
	return(materials)

def get_price(taxes, quantity, item_price, disallowed_item):
	notes = []

	try:
		if disallowed_item:
			value = 0

			note = {
			"error": "Item not accepted at this location"
			}

			notes.append(note)

		else:

			value = (100 - taxes) / 100 * quantity * item_price.buy	

		item_data = {
			"buy": item_price.buy,
			"sell": item_price.sell,
			"tax": taxes,
			"value": value,
			"note" : notes
		}

		return(item_data)

	except AttributeError:
		if allowed:
			value = (100 - taxes) / 100 * quantity * 0
		else:
			value = 0

			note = {
			"error": "Item not accepted at this location"
			}

			notes.append(note)

		note = {
			"error": "No price information in database."
			}

		notes.append(note)

		item_data = {
			"buy": 0,
			"sell": 0,
			"tax": taxes,
			"value": value,
			"note" : notes
		}

		return(item_data)     