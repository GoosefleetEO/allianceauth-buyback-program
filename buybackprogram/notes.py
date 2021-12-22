from allianceauth.services.hooks import get_extension_logger
logger = get_extension_logger(__name__)

def note_price_dencity_tax(name, price_dencity, price_dencity_tax):
	if price_dencity_tax:
		note = {
					"icon": "fa-weight-hanging",
					"color": "orange",
					"message": "%s has price dencity of %s isk/m³, %s %s low price dencity tax applied"
					% (name, price_dencity, price_dencity_tax, "%"),
				}

		return note
	else:
		return False

def note_item_disallowed(item_disallowed, name):
	if item_disallowed:
		note = {
			"icon": "fa-hand-paper",
			"color": "red",
			"message": "%s is disallowed in this program" % name,
		}
		return note
	else:
		return False

def note_unpublished_item(name):
	note = {
			"icon": "fa-hand-paper",
			"color": "red",
			"message": "%s is not a published item. Special commondite or expired item?"
			% name,
		}
	return note

def note_missing_typematerials(type_materials, name):
	if type_materials.count() == 0:
		
		logger.error(
					"TypeMaterials not found for %s. Did you forget to run buybackprogram_load_data?"
					% name
				)

		note = {
			"icon": "fa-exclamation-triangle",
			"color": "red",
			"message": "Refined price valuation is used in this program but TypeMaterials for %s are missing from the database."
			% name,
		}
		return note
	else:
		return False

def note_item_specific_tax(name, item_tax):
	if item_tax > 0:
		note = {
				"icon": "fa-percentage",
				"color": "orange",
				"message": "%s has an additional %s %s item spesific tax applied on it"
				% (name, item_tax, "%"),
			}
		return note
	else:
		return False

def note_no_price_data(name):
	note = {
			"icon": "fa-question",
			"color": "red",
			"message": "%s has no price data" % name,
		}
	return note

def note_refined_price_used(name):
	note = {
			"icon": "fa-exchange-alt",
			"color": "blue",
			"message": "Best price: Using refined price for %s" % name,
		}

	return note

def note_compressed_price_used(name):
	note = {
			"icon": "fa-exchange-alt",
			"color": "blue",
			"message": "Best price: Using compressed price for %s" % name,
		}
	return note