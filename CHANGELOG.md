# Changelog

All notable changes are listed here. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and versions follow [Semantic Versioning](https://semver.org/).

## [0.3.0] - 2026-11-19

### Added
- `build`, `upcoming` and `check` accept several task files and combine them, like `lifecal build home.yml car.yml`. Each file keeps its own reminder default, problems and warnings name the file they come from, and a task that appears in two files gets a warning.
- `lifecal build --name` sets the calendar name. When combined files have different names, the calendar is called "Life maintenance" unless you pass `--name`.

## [0.2.1] - 2026-11-15

### Fixed
- One-off tasks whose `due` date has already passed now print a warning from `check`, `build` and `upcoming`, instead of silently disappearing from the upcoming list.

## [0.2.0] - 2026-11-05

### Added
- `lifecal upcoming --format json` prints the upcoming list as JSON (date, days left, task, repeat interval, notes)

## [0.1.0] - 2026-10-29

### Added
- `lifecal init`, `build`, `upcoming` and `check` commands
- Repeating tasks (`every` + `start`, optional `until`) and one-off tasks (`due`)
- Per-task and default reminders
- Templates: starter, homeowner, renter, car-owner, pet-owner, travel-docs
- GitHub Action for building the calendar in CI and publishing to GitHub Pages
