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
- [Setup](#setup)
- [Permissions](#permissions)
- [Settings](#settings)
- [Program Settings](#program-settings)
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

1. Activate your venv ```source /home/allianceserver/venv/auth/bin/activate```
1. Install the plugin ```pip install aa-buybackprogram```
1. Add ```buybackprogram``` into your settings/local.py installed apps section
1. Run migrations ```python manage.py migrate```
1. Collect static files ```python manage.py collectstatic```
1. Reload supervisor
1. Run the management commands in the next section

## Setup

Buybackprogram requires a lot of data to function as it is designed to allow your clients to sell you any items that exsist in EVE. For this reason pre-loading all the date will take a while.

### Type data

To load type data run the command ```python manage.py buybackprogram_load_data```. This will start the preload of all `EveType`, `SolarSystem` and `EveTypeMaterial` objects.

You can follow the progress of the load from your auth da

You will need to wait for the type data to load up before you can start to use the plugin. Trying to calculate prices for items that have not been preloaded into the database will result in 0 prices for the item degardless of your settings.
{: .alert .alert-danger}

### Price data

After you have preloaded the type data you can preload price data into the database. Price data preloading is not mandatory but will speed up the first buyback calculations.

If price information is not found for items when the prices are calcualted the first time the prices for that item will be fetched during the calculation process. This will increase the calculation time for the contract.
{: .alert .alert-info}

To preload price data run ```python manage.py buybackprogram_load_prices```

### Periodic tasks

Buyback program requires a few periodic tasks to operate and update its data.

#### Price updates
Buybackprogram is designed to use localy stored prices to speed up the price calculations. It is important that you have the price update task in your periodic tasks so that your prices will update.

To have your prices updated every 24 hours add the following line in your `local.py` setting file:

```
# Buybackprogram price updates
CELERYBEAT_SCHEDULE['buybackprogram_update_all_prices'] = {
    'task': 'buybackprogram.tasks.update_all_prices',
    'schedule': crontab(minute=0, hour='0'),
}
```

#### Contract updates
To fetch contracts from your program managers add the following line in your `local.py` settings file. This will update your contracts every hour

```
# Buybackprogram contract updates
CELERYBEAT_SCHEDULE['buybackprogram_update_all_contracts'] = {
    'task': 'buybackprogram.tasks.update_all_contracts',
    'schedule': crontab(minute=0, hour='*'),
}
```

## Permissions
Overview of all permissions in this program. Note that all permissions are in the "general" section.

Name | Purpose | Example Target Audience
-- | -- | --
basic_access | Can access this app and see own statics. Can use buyback programs that are allowed by the buyback restriction rules. | Member State
manage_programs | Can create new locations and buyback programs and manage their own buyback programs. Can see own buyback programs statics. | Buyback managers
see_all_statics | Can see all statistics in all buyback programs | Leadership

## Settings
After you have preloaded all the needed data you can start to setup programs.

Each user with `manage_programs` permission is able to setup their own buyback programs.

### Managers
Each buyback program is operated by a manager. To add a new manager click on the `setup manager` button.

### Locations
1. Each buyback program operates at a location that is constructed of `SolarSystem` and a `Custom name`. To add a new location click on the `add location` button on the buyback page.

Find a solar system by typing in the solar system box. Then determine a name for the structure. Most often you want to use the actual ingame name of the structure so that people are able to identify the location.

### Additional settings
Name | Description | Default
-- | -- | --
BUYBACKPROGRAM_TRACKING_PREFILL | This is the prefill tag you will have on the tracking description for your contracts | aa-bbp.

## Program
Once you have created a location you can setup the actual program. Click on the `create program` button to create a new program.

### Program settings

Each program can be customized based on your needs. When setting up select the settings you wish to use.

#### Owner
This is the character or the characters corporation which will be used as the assign to target for buyback contracts at this location. To add more owners use the `add manager` button. You can only see your own characters.

#### Is Corporation
If you wish that the contracts are assigned to the owners corporation instead of the character tick this box.

#### Tax
This is a general tax which is applied on all items in this program. If you wish to not allow all items in this program you can leave this to 0.

General tax is applied on all items sold via the buyback. You can add additional taxes on individual items or ban them from beeing accepted to the program once you have created the program.

#### Hauling fuel cost
You can add a fuel cost expense that is applied on each item sold via this program based on the volume of the item.

This setting is aimed more to null sec buyback programs to make it easier to calculate your taxes and display your members the expenses you have when selling.
{: .alert .alert-info}

#### Price dencity modifier
You can use a price dencity modifier which will add a additional tax on items with low price per volume ratio such as T1 ships.

This setting is aimer more at high sec buyback programs.
{: .alert .alert-info}

#### Price dencity treshold
This is the lowest isk/m^3 ratio for items that are accepted to the program without the price dencity tax. Finding your own limits depends on your logistical department.

For example: Tritanium is 500 ISK/m³ @ 5 ISK per unit price. PLEX is 14,5Trillion ISK/m³ @2.9M per unit price.

#### Price dencity tax
This is the tax which will be applied to items with a price dencity bellow the price dencity treshold


You should avoid using both the hauling fuel cost and the price dencity modifier at the same time as their function is fairly similar.
{: .alert .alert-warning}

#### Allow all items
If you wish to allow any types of items to be sold via this program keep this box ticker.

You can determine individual increased taxes or ban items from beeing accepted to this program after creating the program.

If you do not want to accept all items you can set this box to False. By doing this you will need to set up a tax for each item you wish to accept into the program individually.

### Ore settings
Ore type items such as asteroid, moon goo and ice have additional pricing methods you can use. You can use a mix of any of the three pricing models.

When using more than one pricing model the best price will be used as the buy value.
{: .alert .alert-info}

#### Use Refined value
If you wish to calculate ore buyback value based on the mineral values tick this box.

#### Use compressed value
If you want to use compressed value as a pricing method tick this box.

#### Use raw ore value
If you want to use raw ore value as a pricing method you can tick this box. Note that some ores such as Kernite and Moon Goo do not represent the real mineral value of the ores.

You can also individually ban raw ore types from the program. If you have an other option than the raw ore value selected the price will be calculated based on the other pricing models.

#### Allow unpacked items
Most often you want to buy only items that are packed. This will ensure that people do not sell items such as broken ammo crystals for you.

#### Refining rate
The refining rate is used in combination with the use refined value option.


### Restrctions
You can restict the visibnility of the buyback programs to groups and states with the restriction options.

If no options are selected the program will be visible for everyone with the `basic_access` role.

Do not mix group and state restrictions as this may lead into logic error. If you need to mix then create a separate programs for them.
{: .alert .alert-danger}
