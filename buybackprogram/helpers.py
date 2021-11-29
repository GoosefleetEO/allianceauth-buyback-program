from eveuniverse.models import EveType, EveTypeMaterial

from allianceauth.services.hooks import get_extension_logger

from buybackprogram.models import ItemPrices

logger = get_extension_logger(__name__)


def get_item_prices(item_type, name, quantity, program, program_item_settings):

    # Get item raw price information
    item_price = ItemPrices.objects.filter(id=item_type.id).first()

    item_type_price = {
        "id": item_type.id,
        "quantity": quantity,
        "buy": item_price.buy,
        "sell": item_price.sell,
    }

    # Get refining materials for item
    type_materials = EveTypeMaterial.objects.filter(
        eve_type_id=item_type.id
    ).prefetch_related("eve_type")

    item_material_price = []

    for material in type_materials:
        material_price = ItemPrices.objects.filter(
            id=material.material_eve_type.id
        ).first()

        material_type_prices = {
            "id": material.material_eve_type.id,
            "quantity": material.quantity,
            "buy": material_price.buy,
            "sell": material_price.sell,
        }

        item_material_price.append(material_type_prices)

    prices = {
        "materials": type_materials,
        "type_prices": item_type_price,
        "material_prices": item_material_price,
    }

    return prices


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
