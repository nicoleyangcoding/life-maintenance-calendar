"""Write an RFC 5545 (iCalendar) file.

Output is deterministic: building the same task file twice gives identical bytes,
so a published calendar only changes when the tasks do.
"""

from __future__ import annotations

import datetime as dt
import hashlib

from .model import Calendar, Task

PRODID = "-//life-maintenance-calendar//lifecal//EN"
_FREQ = {"day": "DAILY", "week": "WEEKLY", "month": "MONTHLY", "year": "YEARLY"}


def escape(text: str) -> str:
    return (
        text.replace("\\", "\\\\")
        .replace(";", "\\;")
        .replace(",", "\\,")
        .replace("\r\n", "\\n")
        .replace("\n", "\\n")
    )


def fold(line: str) -> str:
    """Fold a content line at 75 octets without splitting a UTF-8 character."""
    out, current, size = [], "", 0
    for char in line:
        width = len(char.encode("utf-8"))
        limit = 75 if not out else 74  # continuation lines start with a space
        if size + width > limit:
            out.append(current)
            current, size = "", 0
        current += char
        size += width
    out.append(current)
    return "\r\n ".join(out)


def _date(day: dt.date) -> str:
    return day.strftime("%Y%m%d")


def uid(task: Task) -> str:
    key = f"{task.name}|{task.start.isoformat()}".encode()
    return f"{hashlib.sha1(key).hexdigest()[:16]}@lifecal"


def event_lines(task: Task) -> list[str]:
    lines = [
        "BEGIN:VEVENT",
        f"UID:{uid(task)}",
        f"DTSTAMP:{_date(task.start)}T000000Z",
        f"DTSTART;VALUE=DATE:{_date(task.start)}",
        f"DTEND;VALUE=DATE:{_date(task.start + dt.timedelta(days=1))}",
        f"SUMMARY:{escape(task.name)}",
        "TRANSP:TRANSPARENT",
    ]
    if task.every:
        rule = f"RRULE:FREQ={_FREQ[task.every.unit]};INTERVAL={task.every.count}"
        if task.until:
            rule += f";UNTIL={_date(task.until)}"
        lines.append(rule)
    description = task.notes
    if task.every:
        description = f"Repeats every {task.every}." + (f"\n\n{task.notes}" if task.notes else "")
    if description:
        lines.append(f"DESCRIPTION:{escape(description)}")
    if task.remind_days is not None:
        lines += [
            "BEGIN:VALARM",
            "ACTION:DISPLAY",
            f"DESCRIPTION:{escape(task.name)}",
            f"TRIGGER:-P{task.remind_days}D" if task.remind_days else "TRIGGER:PT9H",
            "END:VALARM",
        ]
    lines.append("END:VEVENT")
    return lines


def render(cal: Calendar) -> str:
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        f"PRODID:{PRODID}",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        f"X-WR-CALNAME:{escape(cal.name)}",
    ]
    for task in sorted(cal.tasks, key=lambda t: (t.start, t.name.lower())):
        lines += event_lines(task)
    lines.append("END:VCALENDAR")
    return "\r\n".join(fold(line) for line in lines) + "\r\n"
