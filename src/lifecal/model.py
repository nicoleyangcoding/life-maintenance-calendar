"""Load and validate a life.yml task file."""

from __future__ import annotations

import datetime as dt
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

UNITS = ("day", "week", "month", "year")
ALIASES = {
    "daily": (1, "day"),
    "weekly": (1, "week"),
    "monthly": (1, "month"),
    "quarterly": (3, "month"),
    "yearly": (1, "year"),
    "annually": (1, "year"),
}
_AMOUNT = re.compile(r"^\s*(\d+)\s*(day|week|month|year)s?\s*(before)?\s*$", re.IGNORECASE)
_DAYS_PER_UNIT = {"day": 1, "week": 7, "month": 30, "year": 365}

DEFAULT_REMIND_DAYS = 7


class ConfigError(Exception):
    """Raised when a task file cannot be used. Holds every problem found."""

    def __init__(self, problems: list[str]):
        self.problems = problems
        super().__init__("\n".join(problems))


@dataclass(frozen=True)
class Interval:
    count: int
    unit: str  # one of UNITS

    def __str__(self) -> str:
        return f"{self.count} {self.unit}{'' if self.count == 1 else 's'}"


@dataclass(frozen=True)
class Task:
    name: str
    start: dt.date
    every: Interval | None = None
    until: dt.date | None = None
    remind_days: int | None = DEFAULT_REMIND_DAYS
    notes: str = ""

    @property
    def repeats(self) -> bool:
        return self.every is not None


@dataclass(frozen=True)
class Calendar:
    name: str
    tasks: tuple[Task, ...]
    warnings: tuple[str, ...] = ()


def parse_interval(value: Any) -> Interval:
    text = str(value).strip().lower()
    if text in ALIASES:
        return Interval(*ALIASES[text])
    match = _AMOUNT.match(text)
    if not match or match.group(3):
        raise ValueError(f"'{value}' is not an interval. Try '3 months' or 'yearly'.")
    count = int(match.group(1))
    if count < 1:
        raise ValueError("an interval must be at least 1")
    return Interval(count, match.group(2).lower())


def parse_remind(value: Any) -> int | None:
    """Return days of advance notice, or None for no reminder."""
    if value is None or value is False or str(value).strip().lower() in ("none", "no", "off"):
        return None
    text = str(value).strip().lower()
    if text in ("same day", "on the day", "0"):
        return 0
    match = _AMOUNT.match(text)
    if not match:
        raise ValueError(f"'{value}' is not a reminder. Try '2 weeks before' or 'none'.")
    return int(match.group(1)) * _DAYS_PER_UNIT[match.group(2).lower()]


def parse_date(value: Any) -> dt.date:
    if isinstance(value, dt.datetime):
        return value.date()
    if isinstance(value, dt.date):
        return value
    try:
        return dt.date.fromisoformat(str(value).strip())
    except ValueError:
        raise ValueError(f"'{value}' is not a date. Use YYYY-MM-DD.") from None


def load(path: str | Path) -> Calendar:
    path = Path(path)
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        raise ConfigError([f"{path}: file not found"]) from None
    try:
        data = yaml.safe_load(text)
    except yaml.YAMLError as exc:
        raise ConfigError([f"{path}: not valid YAML ({exc})"]) from None
    return parse(data, source=str(path))


def parse(data: Any, source: str = "life.yml") -> Calendar:
    if not isinstance(data, dict):
        raise ConfigError([f"{source}: expected a 'tasks:' list at the top level"])

    settings = data.get("calendar") or {}
    if not isinstance(settings, dict):
        raise ConfigError([f"{source}: 'calendar' must be a mapping"])

    problems: list[str] = []
    warnings: list[str] = []

    default_remind: int | None = DEFAULT_REMIND_DAYS
    if "remind" in settings:
        try:
            default_remind = parse_remind(settings["remind"])
        except ValueError as exc:
            problems.append(f"calendar.remind: {exc}")

    raw_tasks = data.get("tasks")
    if not isinstance(raw_tasks, list) or not raw_tasks:
        problems.append(f"{source}: add at least one item under 'tasks:'")
        raise ConfigError(problems)

    tasks: list[Task] = []
    seen: set[str] = set()
    for index, raw in enumerate(raw_tasks, start=1):
        label = f"task {index}"
        if not isinstance(raw, dict):
            problems.append(f"{label}: expected fields like 'name' and 'due'")
            continue
        name = str(raw.get("name") or "").strip()
        if not name:
            problems.append(f"{label}: missing 'name'")
            continue
        label = f"task {index} ({name})"
        if name.lower() in seen:
            warnings.append(f"{label}: another task has the same name")
        seen.add(name.lower())

        unknown = set(raw) - {"name", "every", "start", "due", "until", "remind", "notes"}
        if unknown:
            problems.append(f"{label}: unknown field(s) {', '.join(sorted(unknown))}")

        has_every, has_due = "every" in raw, "due" in raw
        if has_every == has_due:
            problems.append(f"{label}: give either 'every' (repeating) or 'due' (one date)")
            continue

        try:
            remind = parse_remind(raw["remind"]) if "remind" in raw else default_remind
            notes = str(raw.get("notes") or "").strip()
            if has_due:
                if "start" in raw or "until" in raw:
                    problems.append(f"{label}: 'start' and 'until' only apply to repeating tasks")
                    continue
                tasks.append(Task(name, parse_date(raw["due"]), remind_days=remind, notes=notes))
                continue

            if "start" not in raw:
                problems.append(f"{label}: repeating tasks need a 'start' date")
                continue
            every = parse_interval(raw["every"])
            start = parse_date(raw["start"])
            until = parse_date(raw["until"]) if raw.get("until") is not None else None
            if until and until < start:
                problems.append(f"{label}: 'until' is before 'start'")
                continue
            if every.unit == "month" and start.day > 28:
                warnings.append(
                    f"{label}: starts on day {start.day}; some calendar apps skip months "
                    "without that day. Day 28 or earlier is safest."
                )
            elif every.unit == "year" and (start.month, start.day) == (2, 29):
                warnings.append(f"{label}: starts on Feb 29, so it only appears in leap years")
            tasks.append(Task(name, start, every, until, remind, notes))
        except ValueError as exc:
            problems.append(f"{label}: {exc}")

    if problems:
        raise ConfigError(problems)

    name = str(settings.get("name") or "Life maintenance").strip()
    return Calendar(name, tuple(tasks), tuple(warnings))
