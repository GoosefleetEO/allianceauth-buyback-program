# Change Log

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).

## [Unreleased] - yyyy-mm-dd

### Added
- Added check for discordnotify app to prevent multiple notifications
- Improvent error hanlding on when discordproxy was installed but not running

### Changed
- Reconstructed how notifications work. Greatly improved speed for statistics pages.

### Fixed
- Fixes #24
- Fixes #22

## [1.0.2] - yyyy-mm-dd

### Added
- Closes #21, added parent group mentions for market group item tax fields

### Changed

### Fixed
- Item tax not applying on price variants correctly
- Fixes #20, allow to set 0% item taxes

## [1.0.1] - yyyy-mm-dd

### Fixed
- Fixes #18, compressed variant not used on already compressed ores
- Fixes #19, fixes view all statistics permission issue

## [1.0.0] - 2022-01-09

** THIS RELEASE CONTAINS MAJOR CHANGES THAT REQUIRE A CLEAN REINSTALL OF THE APP. ALL PREVIOUS DATA INSIDE THIS APP WILL BE LOST **

## Updating from 0.1.8 to 1.0.0
- Activate your virtual enviroment `source /home/allianceserver/venv/auth/bin/activate`
- Remove all data from 0.1.8 ** THIS COMMAND WILL REMOVE ALL DATA FROM THE BUYBACKPROGRAM APP STORED IN YOUR DATABASE ** `python /home/allianceserver/myauth/manage.py migrate buybackprogram zero`
- Upgrade to 1.0.0 with `pip install -U aa-buybackprogram==1.0.0`
- Run the migrations `python /home/allianceserver/myauth/manage.py migrate`
- Collect static files `python /home/allianceserver/myauth/manage.py collectstatic`
- Restart auth `supervisorctl restart myauth:`
- Load data `python manage.py buybackprogram_load_data`
- Load prices `python manage.py buybackprogram_load_prices`
- Setup your programs

### Added
- Fixed #10, added ability to delete own locations
- Fixes #9, added ability to track contract locations per structure ID
- Fixes #13, added ability to praisal blue and red loot by npc buy orders
- Fixes #5, added the ability to receive notifications for new contracts and for sellers notifications about completed contracts, supports both aa-discordbot and discordproxy.
- Fixed #15, added mention of scopes into readme file
- Fixes #12, added requirement for eveuniverse in readme
- Fixes #8, added the ability to add special taxes via market groups
- Added total refined value row for refined prices

### Changed
- Fixes #11, now also tracking contracts that have extra characters in the description such as extra spaces.
- Merger readme periodic tasks into a single code block to make copying easier
- Removed ability to use locations that were created by other managers.
- Moved some views into a separate file
- Added more views for special taxes
- Renamed special taxes view paths

### Fixed
- Fixed #16, a corporation can now have multiple managers

## [0.1.8] - 2021-12-24

### Fixed
- Availability field not displaying corp if owner is a corporation on calculation page
- Fixes #7, refined price not used correctly when selling compressed price with only refined pricing method.
- Fixed wrong crontab settigs for contract updates
- Readme spelling fixes

## [0.1.6] - 2021-12-24

### Fixed
- Calculation quantities did not parse correctly if the user had hidden or added more columns to the default detailed view.

## [0.1.5] - 2021-12-24

### Fixed
- Fixed #3
- Fixes #4 by adding support for UK localization

## [0.1.4] - 2021-12-24

### Changed
- Contract celery schedule to every 15 minutes

### Fixed
- #4 Localization issues with number formats

### Fixed
- Readme styling

## [0.1.3] - 2021-12-23

### Added
- Missing manifest entry for swagger.json

## [0.1.2] - 2021-12-23

### Changed
- Tracking item creation changed to bulk create to decrease database calls

### Fixed
- Multiple typos

## [Unreleased] - yyyy-mm-dd

### Added

### Changed

### Fixed
