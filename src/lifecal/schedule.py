"""Work out when tasks fall due."""

from __future__ import annotations

import calendar
import datetime as dt
from collections.abc import Iterator

from .model import Interval, Task


def add_months(day: dt.date, months: int) -> dt.date:
    """Add months, clamping to the last day of shorter months (Jan 31 + 1 -> Feb 28)."""
    index = day.month - 1 + months
    year, month = day.year + index // 12, index % 12 + 1
    return day.replace(year=year, month=month, day=min(day.day, calendar.monthrange(year, month)[1]))


def nth_occurrence(start: dt.date, every: Interval, n: int) -> dt.date:
    if every.unit == "day":
        return start + dt.timedelta(days=every.count * n)
    if every.unit == "week":
        return start + dt.timedelta(weeks=every.count * n)
    if every.unit == "month":
        return add_months(start, every.count * n)
    return add_months(start, 12 * every.count * n)


def occurrences(task: Task, until: dt.date) -> Iterator[dt.date]:
    """Yield each date the task falls due, up to and including `until`."""
    if not task.repeats:
        if task.start <= until:
            yield task.start
        return
    end = min(until, task.until) if task.until else until
    n = 0
    while (day := nth_occurrence(task.start, task.every, n)) <= end:
        yield day
        n += 1


def upcoming(tasks: tuple[Task, ...], today: dt.date, days: int) -> list[tuple[dt.date, Task]]:
    """Every due date from today through `days` from now, soonest first."""
    horizon = today + dt.timedelta(days=days)
    found = [(day, task) for task in tasks for day in occurrences(task, horizon) if day >= today]
    return sorted(found, key=lambda pair: (pair[0], pair[1].name.lower()))
