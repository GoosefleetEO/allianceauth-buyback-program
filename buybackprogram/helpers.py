from eveuniverse.models import EveType, EveTypeMaterial

from allianceauth.services.hooks import get_extension_logger

from buybackprogram.constants import COMPRESSING_EVE_GROUPS, REFINING_EVE_GROUPS
from buybackprogram.models import ItemPrices, ProgramItem

logger = get_extension_logger(__name__)


def getList(dict):
    return dict.keys()


# This method will get the price information for the item. It will not calculate the values as in price including taxes.
def get_item_prices(item_type, name, quantity, program):

    # TODO check if item is in allowed list
    # TODO checks if not all items are allowed

    # Get item raw price information
    item_price = ItemPrices.objects.filter(eve_type_id=item_type.id).first()

    # If raw ore value should not be taken into account
    if not program.use_raw_ore_value and item_type.eve_group.id in getList(
        REFINING_EVE_GROUPS
    ):
        item_type_price = False

    else:
        item_type_price = {
            "id": item_type.id,
            "quantity": quantity,
            "buy": item_price.buy,
            "sell": item_price.sell,
        }

    # Check if we should get refined value for the item
    if (
        item_type.eve_group.id in getList(REFINING_EVE_GROUPS)
        and program.use_refined_value
    ):
        item_material_price = []
        # Get all refining materials for item
        type_materials = EveTypeMaterial.objects.filter(
            eve_type_id=item_type.id
        ).prefetch_related("eve_type")

        # Get price details for the materials inside the item
        logger.debug("Getting refined values for %s" % name)
        for material in type_materials:
            material_price = ItemPrices.objects.filter(
                eve_type_id=material.material_eve_type.id
            ).first()

            refining_ratio = REFINING_EVE_GROUPS[item_type.eve_group.id]

            # Quantity of refined materials
            material_quantity = (material.quantity * quantity) / refining_ratio

            material_type_prices = {
                "id": material.material_eve_type.id,
                "quantity": material_quantity,
                "buy": material_price.buy,
                "sell": material_price.sell,
            }

            item_material_price.append(material_type_prices)
    else:
        item_material_price = False
        type_materials = False
        logger.debug("No refined value used for %s" % name)

    # Get compressed versions of the ores that are not yet compressed
    if (
        item_type.eve_group.id in getList(COMPRESSING_EVE_GROUPS)
        and "Compressed" not in name
        and program.use_compressed_value
    ):
        compresed_name = "Compressed " + name
        compression_ratio = COMPRESSING_EVE_GROUPS[item_type.eve_group.id]

        logger.debug(
            "Getting compression prices for %s based on original item %s"
            % (compresed_name, name)
        )

        compression_price = ItemPrices.objects.filter(
            eve_type_id__name=compresed_name
        ).first()

        logger.debug(
            "Got prices %s ISK for %s" % (compression_price.buy, compresed_name)
        )

        compressed_type_prices = {
            "id": compression_price.eve_type_id,
            "quantity": quantity / compression_ratio,
            "buy": compression_price.buy,
            "sell": compression_price.sell,
        }

    # If item can't or should not be compressed
    else:
        logger.debug("No compression required/available for %s" % name)
        compressed_type_prices = False

    prices = {
        "materials": type_materials,
        "type_prices": item_type_price,
        "material_prices": item_material_price,
        "compression_prices": compressed_type_prices,
    }

    return prices


def get_item_values(item_type, item_prices, program):

    # Get special taxes and see if our item belongs to this table
    program_item_settings = ProgramItem.objects.filter(
        program=program, item_type__id=item_type.id
    ).first()

    # If we have an special taxation item, assign it to a variable
    if program_item_settings:
        item_tax = program_item_settings.item_tax
        logger.debug("Found tax %s for %s" % (item_tax, item_type.id))

    # If no special taxes are found we ensure our tax variable remains zero
    else:
        item_tax = 0
        logger.debug("No item tax for %s" % item_type.id)

    # Get values for the type prices (base prices) if we have any
    if item_prices["type_prices"]:

        price = item_prices["type_prices"]["buy"]
        quantity = item_prices["type_prices"]["quantity"]
        program_tax = program.tax
        item_tax = item_tax
        tax_multiplier = (100 - (program_tax + item_tax)) / 100

        logger.debug("Calculating type value for %s" % item_type.id)

        type_value = (quantity * price) * tax_multiplier

    # If ther eis no type price the value is also false
    else:
        type_value = False

    # Get values for item materials
    if item_prices["material_prices"]:

        material_value = 0

        for material in item_prices["material_prices"]:

            price = material["buy"]
            quantity = material["quantity"]
            program_tax = program.tax
            item_tax = item_tax
            refining_rate = program.refining_rate / 100
            tax_multiplier = (100 - (program_tax + item_tax)) / 100

            value = (quantity * refining_rate * price) * tax_multiplier

            material_value += value

    else:
        material_value = False

    # Calculate values for compressed variant
    if item_prices["compression_prices"]:
        price = item_prices["compression_prices"]["buy"]
        quantity = item_prices["compression_prices"]["quantity"]
        program_tax = program.tax
        item_tax = item_tax
        tax_multiplier = (100 - (program_tax + item_tax)) / 100

        logger.debug("Calculating compression value for %s" % item_type.id)

        compression_value = (quantity * price) * tax_multiplier

    else:
        compression_value = False

    # Get the highest value of the used pricing methods
    buy_value = max([type_value, material_value, compression_value])

    # Final values for this item
    values = {
        "type_value": type_value,
        "material_value": material_value,
        "compression_value": compression_value,
        "buy_value": buy_value,
    }

    return values


def get_refined_price(type_id, tax, refining_rate, disallowed_item):
    # Get eve material types for id
    typematerial = EveTypeMaterial.objects.filter(eve_type_id=type_id).values()

    # List for all materials
    materials = []

    notes = []

    # Process each material
    for material in typematerial:
        # Get material data
        data = EveType.objects.filter(id=material["material_eve_type_id"]).first()

        # Get material price
        price = ItemPrices.objects.filter(id=data.id).first()

        # Determine value for material
        if disallowed_item:
            value = 0

            note = {"error": "Item not allowed at this location"}

            notes.append(note)

        else:
            value = (
                (100 - tax)
                / 100
                * material["quantity"]
                * price.buy
                * (refining_rate / 100)
            )

        # Build dictionary for material
        material_data = {
            "quantity": material["quantity"],
            "type": data,
            "price": price,
            "value": value,
            "note": notes,
        }

        # Add material to the materials list
        materials.append(material_data)

    return materials


def get_price(taxes, quantity, item_price, disallowed_item):
    notes = []

    try:
        if disallowed_item:
            value = 0

            note = {"error": "Item not accepted at this location"}

            notes.append(note)

        else:

            value = (100 - taxes) / 100 * quantity * item_price.buy

        item_data = {
            "buy": item_price.buy,
            "sell": item_price.sell,
            "tax": taxes,
            "value": value,
            "note": notes,
        }

        return item_data

    except AttributeError:
        logger.error(
            "No price data found in database. Did you remember to populate it?"
        )
