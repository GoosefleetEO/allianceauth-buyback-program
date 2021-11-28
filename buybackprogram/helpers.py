import requests


def evemarketer(
    typeid: [int],
) -> [dict]:
    response = requests.get(
        "https://api.evemarketer.com/ec/marketstat/json",
        params={
            "typeid": typeid,
            "regionlimit": 10000002,
        },
    )

    items = response.json()

    result = {}

    for item in items:
        id = item["buy"]["forQuery"]["types"][0]

        result[id] = {
            "buy": item["buy"]["max"],
            "sell": item["sell"]["min"],
        }

    return result
