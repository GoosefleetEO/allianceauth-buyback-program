from eveuniverse.models import EveType, EveTypeMaterial

from allianceauth.services.hooks import get_extension_logger

from buybackprogram.constants import COMPRESSING_EVE_GROUPS, REFINING_EVE_GROUPS
from buybackprogram.models import ItemPrices, ProgramItem

logger = get_extension_logger(__name__)


def getList(dict):
    return dict.keys()


def get_price_dencity_tax(program, item_value, item_volume, item_quantity):
    # If price dencity tax should be applied
    if program.price_dencity_modifier:

        item_isk_dencity = item_value / (item_volume * item_quantity)

        logger.debug("Values: Our item isk dencity is at %s ISK/m³" % item_isk_dencity)

        if item_isk_dencity < program.price_dencity_treshold:
            return program.price_dencity_tax
        else:
            return False


# This method will get the price information for the item. It will not calculate the values as in price including taxes.
def get_item_prices(item_type, name, quantity, program):

    notes = []

    # Get special taxes and see if our item belongs to this table
    program_item_settings = ProgramItem.objects.filter(
        program=program, item_type__id=item_type.id
    ).first()

    # Check what items are allowed
    if program.allow_all_items:
        if program_item_settings:
            item_disallowed = program_item_settings.disallow_item
        else:
            item_disallowed = False
    else:
        if program_item_settings:
            item_disallowed = program_item_settings.disallow_item
        else:
            item_disallowed = True

    if not item_disallowed:
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
            logger.debug("Prices: Getting refined values for %s" % name)
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
            logger.debug("Prices: No refined value used for %s" % name)

        # Get compressed versions of the ores that are not yet compressed
        if (
            item_type.eve_group.id in getList(COMPRESSING_EVE_GROUPS)
            and "Compressed" not in name
            and program.use_compressed_value
        ):

            compresed_name = "Compressed " + name
            compression_ratio = COMPRESSING_EVE_GROUPS[item_type.eve_group.id]

            logger.debug(
                "Prices: Getting compression prices for %s based on original item %s"
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
            logger.debug("Prices: No compression required/available for %s" % name)
            compressed_type_prices = False

        prices = {
            "type_prices": item_type_price,
            "material_prices": item_material_price,
            "compression_prices": compressed_type_prices,
        }
    else:

        note = {"error": "%s is not allowed at location %s" % (name, program.location)}
        notes.append(note)

        prices = {
            "materials": False,
            "type_prices": False,
            "material_prices": False,
            "compression_prices": False,
            "note": notes,
        }

    return prices


def get_item_values(item_type, item_prices, program):

    type_value = False
    material_value = False
    compression_value = False
    item_tax = False
    refined = []
    compressed = False

    # Get special taxes and see if our item belongs to this table
    program_item_settings = ProgramItem.objects.filter(
        program=program, item_type__id=item_type.id
    ).first()

    # If we have an special taxation item, assign it to a variable
    if program_item_settings:
        item_tax = program_item_settings.item_tax
        logger.debug("Values: Found tax %s for %s" % (item_tax, item_type))

    # If no special taxes are found we ensure our tax variable remains zero

    # Get values for the type prices (base prices) if we have any
    if item_prices["type_prices"]:

        types = EveType.objects.filter(id=item_prices["type_prices"]["id"]).first()

        quantity = item_prices["type_prices"]["quantity"]
        sell = item_prices["type_prices"]["sell"]
        buy = item_prices["type_prices"]["buy"]
        price = buy
        price_dencity = price / types.volume
        price_dencity_tax = get_price_dencity_tax(
            program, price, types.volume, quantity
        )
        program_tax = program.tax
        item_tax = item_tax
        tax_multiplier = (100 - (program_tax + item_tax + price_dencity_tax)) / 100

        logger.debug("Values: Calculating type value for %s" % item_type)

        type_value = (quantity * price) * tax_multiplier

        raw_item = {
            "id": types.id,
            "name": types.name,
            "quantity": quantity,
            "buy": buy,
            "sell": sell,
            "program_tax": program_tax,
            "item_tax": item_tax,
            "price_dencity_tax": price_dencity_tax,
            "total_tax": program_tax + item_tax + price_dencity_tax,
            "price_dencity": price_dencity,
            "value": type_value,
        }

    # Get values for item materials
    if item_prices["material_prices"]:

        material_value = 0

        for material in item_prices["material_prices"]:

            materials = EveType.objects.filter(id=material["id"]).first()

            quantity = material["quantity"]
            sell = material["sell"]
            buy = material["buy"]
            price = buy
            price_dencity = price / materials.volume
            price_dencity_tax = get_price_dencity_tax(
                program, price, materials.volume, quantity
            )
            program_tax = program.tax
            item_tax = item_tax
            refining_rate = program.refining_rate / 100
            tax_multiplier = (100 - (program_tax + item_tax + price_dencity_tax)) / 100

            value = (quantity * refining_rate * price) * tax_multiplier

            r = {
                "id": material["id"],
                "name": materials.name,
                "quantity": quantity,
                "buy": buy,
                "sell": sell,
                "program_tax": program_tax,
                "item_tax": item_tax,
                "price_dencity_tax": price_dencity_tax,
                "total_tax": program_tax + item_tax + price_dencity_tax,
                "price_dencity": price_dencity,
                "value": value,
            }

            refined.append(r)

            material_value += value

    # Calculate values for compressed variant
    if item_prices["compression_prices"]:

        compressed_version = EveType.objects.filter(
            id=item_prices["compression_prices"]["id"]
        ).first()

        quantity = item_prices["compression_prices"]["quantity"]
        buy = item_prices["compression_prices"]["buy"]
        sell = item_prices["compression_prices"]["sell"]
        price = buy
        price_dencity = price / compressed_version.volume
        price_dencity_tax = get_price_dencity_tax(
            program, price, compressed_version.volume, quantity
        )
        program_tax = program.tax
        item_tax = item_tax
        tax_multiplier = (100 - (program_tax + item_tax + price_dencity_tax)) / 100

        logger.debug("Values: Calculating compression value for %s" % item_type.id)

        compression_value = (quantity * price) * tax_multiplier

        compressed = {
            "id": compressed_version.id,
            "name": compressed_version.name,
            "quantity": quantity,
            "buy": buy,
            "sell": sell,
            "program_tax": program_tax,
            "item_tax": item_tax,
            "price_dencity_tax": price_dencity_tax,
            "total_tax": program_tax + item_tax + price_dencity_tax,
            "price_dencity": price_dencity,
            "value": compression_value,
        }

    # Get the highest value of the used pricing methods
    buy_value = max([type_value, material_value, compression_value])

    logger.debug("Values: Best buy value for %s is %s ISK" % (item_type, buy_value))

    # Final values for this item
    values = {
        "normal": raw_item,
        "refined": refined,
        "compressed": compressed,
        "type_value": type_value,
        "material_value": material_value,
        "compression_value": compression_value,
        "buy_value": buy_value,
    }

    print()

    return values


def get_item_buy_value(buyback_data, program):

    total_all_items = 0
    total_hauling_cost = 0
    contract_net_total = 0

    # Get a grand total value of all buy prices
    for item in buyback_data:
        total_all_items += item["item_values"]["buy_value"]

    logger.debug(
        "Final: Total buy value for all items before expenses is %s ISK"
        % total_all_items
    )

    # Calculate hauling expenses
    if program.hauling_fuel_cost > 0:
        for item in buyback_data:
            item_volume = item["type_data"].volume
            quantity = item["item_values"]["normal"]["quantity"]
            hauling_cost = item_volume * program.hauling_fuel_cost * quantity

            total_hauling_cost += hauling_cost

            logger.debug(
                "Final: Hauling cost %s m³ of %s is %s ISK"
                % (
                    item["item_prices"]["type_prices"]["quantity"],
                    item["type_data"],
                    hauling_cost,
                )
            )

        logger.debug(
            "Final: Total hauling cost for whole contract is %s ISK"
            % total_hauling_cost
        )

    contract_net_total = total_all_items - total_hauling_cost

    logger.debug("Final: Net total after expenses is %s ISK" % contract_net_total)

    contract_net_prices = {
        "total_all_items": total_all_items,
        "total_hauling_cost": total_hauling_cost,
        "contract_net_total": contract_net_total,
    }

    return contract_net_prices
