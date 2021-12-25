# Change Log

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).

## [Unreleased] - yyyy-mm-dd

### Added

### Changed

### Fixed

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
