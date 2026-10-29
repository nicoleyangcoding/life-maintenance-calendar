# life-maintenance-calendar

Keep the chores you only do once a year (or once a decade) in one plain-text file, and get them on your phone's calendar.

Furnace filters, smoke alarm batteries, passport renewals, warranty end dates, car registration: write them down once, and `lifecal` turns the list into a standard calendar file that works with Apple Calendar, Google Calendar and Outlook.

```
$ lifecal upcoming
2026-11-01  in 3 days      Replace HVAC air filter
2026-11-01  in 3 days      Test smoke and CO alarms
2027-01-15  in 78 days     Clean dryer vent
2027-03-01  in 123 days    Flush water heater
```

## Quick start

Requires Python 3.9 or newer.

```bash
pipx install git+https://github.com/nicoleyangcoding/life-maintenance-calendar
lifecal init homeowner        # creates life.yml from a template
lifecal build                 # writes life.ics
```

Open `life.ics` to import it into your calendar app. That's it.

No `pipx`? `pip install git+https://github.com/nicoleyangcoding/life-maintenance-calendar` works too.

## The task file

```yaml
calendar:
  name: Home maintenance
  remind: 1 week before          # default reminder for every task

tasks:
  - name: Replace HVAC air filter
    every: 3 months              # repeating: needs a start date
    start: 2026-11-01

  - name: Passport expires
    due: 2030-05-01              # one-off date
    remind: 9 months before
    notes: Many countries require 6 months of validity to enter.
```

| Field    | Use it for                                                                 |
| -------- | -------------------------------------------------------------------------- |
| `name`   | What shows on the calendar. Required.                                      |
| `every`  | A repeat interval: `2 weeks`, `3 months`, `1 year`, `monthly`, `yearly`.   |
| `start`  | First date for a repeating task (`YYYY-MM-DD`).                            |
| `until`  | Optional last date for a repeating task.                                   |
| `due`    | A single date, for things that happen once.                                |
| `remind` | `3 days before`, `2 weeks before`, `same day`, or `none`. Default: 1 week. |
| `notes`  | Optional details shown in the event.                                       |

Each task uses either `every` + `start`, or `due`. If something is off, `lifecal check` tells you exactly what to fix.

## Templates

`lifecal init --list` shows them all:

| Template      | Includes                                                       |
| ------------- | -------------------------------------------------------------- |
| `starter`     | Two examples to edit (the default)                             |
| `homeowner`   | Filters, alarms, gutters, water heater, dryer vent, furnace    |
| `renter`      | Alarms, range hood filter, insurance, lease renewal            |
| `car-owner`   | Oil, tires, wipers, registration, insurance                    |
| `pet-owner`   | Monthly treatments, vet checkups, license renewal              |
| `travel-docs` | Passport, driver's license, trusted traveler, travel insurance |

Templates are general starting points, not professional advice. Where your manufacturer, vet or local authority sets a different schedule, follow theirs.

## Commands

| Command                       | What it does                                    |
| ----------------------------- | ----------------------------------------------- |
| `lifecal init [template]`     | Create `life.yml` from a template               |
| `lifecal build [file]`        | Write the `.ics` calendar file                  |
| `lifecal upcoming [--days N]` | List what's due in the next N days (default 90) |
| `lifecal check [file]`        | Validate the file and explain any problems      |

Every command reads `life.yml` in the current folder unless you pass another file.

## Stay in sync with a calendar subscription

Importing a file makes a one-time copy. For edits to show up automatically, host `life.ics` at a URL and subscribe to it:

- **Apple Calendar:** File > New Calendar Subscription
- **Google Calendar:** Other calendars > From URL
- **Outlook:** Add calendar > Subscribe from web

This repo includes a GitHub Action that rebuilds the calendar and publishes it to GitHub Pages every time you push. See [examples/publish-calendar.yml](examples/publish-calendar.yml).

> **Privacy:** anyone who has the link can read anything on GitHub Pages. Don't publish personal details like document numbers. For private dates, import the file instead of subscribing, or host it somewhere private.

Google Calendar ignores reminders in subscribed calendars and only refreshes them every several hours. Apple Calendar and Outlook honor reminders.

## Privacy

`lifecal` runs entirely on your computer. It makes no network requests and collects nothing.

## Contributing

New templates are the easiest and most useful contribution. See [CONTRIBUTING.md](CONTRIBUTING.md). Planned work is in [ROADMAP.md](ROADMAP.md).

## License

[MIT](LICENSE)
