# Buyback Program

An Alliance Auth app for creating buyback programs and to allow users calculate prices for buyback contracts.

[![pipeline](https://gitlab.com/paulipa/allianceauth-buyback-program/badges/master/pipeline.svg)](https://gitlab.com/paulipa/allianceauth-buyback-program/-/commits/master)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![chat](https://img.shields.io/discord/790364535294132234)](https://discord.gg/zmh52wnfvM)

## Contents
- [Images](#images)
- [Features](#features)
- [Installation](#installation)
- [Management Commands](#management-commands)
- [Permissions](#permissions)
- [Settings](#settings)
- [FAQ](#faq)
- [Change Log](CHANGELOG.md)

## Images

![buyback_programs](/uploads/5ed1638501915e936d2e8177f4580da1/buyback_programs.png)
![item_details](/uploads/d124c70b15b36490c79b907fa25f768d/item_details.png)
![calculator](/uploads/47726510c6d6effa0e856e5ad5ca1688/calculator.png)
![program_statics](/uploads/e370ec69a3d050ecff4c4e7a19ec8849/program_statics.png)

## Features

- Multiple programs with their own settings
- Multiple owners
- Supports corporation and character owners
- Flexible program settings:
	- Allow all items
	- Allow only spesific items
	- Custom location names
	- Global program tax
	- Item specified tax
	- Hauling fuel cost
	- Low price dencity tax
- Best price variant for ore:
	- Supports raw, compressed, refined and any combination of the 3.
	- Will calculate price by the best available pricing method

- Allow / disallow unpacked items
- Restrict program to:
	- States
	- Groups
	- Open for everyone
- Personal buyback static tracking for:
	- Outstanding contracts
	- Finished contracts
- Program tracking for owners:
	- Outstanding contracts
	- Total bought value
	- Alerts for mistakes in contracts such as missmatching price
- Contract tracking history

## Installation

1. Activate your venv `source /home/allianceserver/venv/auth/bin/activate`
1. Install the plugin `pip install aa-buybackprogram`
1. Add `buybackprogram` into your settings/local.py installed apps section
1. Run migrations `python manage.py migrate`
1. Collect static files `python manage.py collectstatic`
1. Reload supervisor
1. Run the management commands in the next section

## Management Commands

Buybackprogram requires a lot of data to function as it is designed to allow your clients to sell you any items that exsist in EVE. For this reason pre-loading all the date will take a while.

### Type data

To load type data run the command `python manage.py buybackprogram_load_data`. This will start the preload of all `EveType`, `SolarSystem` and `EveTypeMaterial` objects.

You can follow the progress of the load from your auth dashboard task que. You can expect to see 50k+ tasks generated from this command.

## Permissions

## Settings

## FAQ
