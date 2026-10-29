# Roadmap

Small, focused releases. Ideas and votes are welcome in [issues](https://github.com/nicoleyangcoding/life-maintenance-calendar/issues).

## 0.2
- [ ] `lifecal done "<task>"`: log when you last did a task and move its next date forward
- [ ] `--format json` for `upcoming`, for scripts and dashboards
- [ ] Template: `new-baby` (pediatric visit reminders, car seat expiry)

## 0.3
- [ ] `lifecal add`: add a task interactively, without editing YAML
- [ ] Warn about tasks whose `due` date has already passed
- [ ] Templates: `bike`, `garden`, `small-business` (license and filing renewals)

## Later
- [ ] Combine several task files into one calendar (`lifecal build home.yml car.yml`)
- [ ] Optional time of day for reminders
- [ ] Publish to PyPI so `pipx install life-maintenance-calendar` works

## Not planned
- A hosted service or account system. `lifecal` stays a local, plain-text tool.
