import datetime as dt

from lifecal.ics import escape, fold, render
from lifecal.model import Calendar, Interval, Task


def test_escape():
    backslash = chr(92)
    assert escape("a,b;c" + backslash + "d\ne") == r"a\,b\;c\\d\ne"


def test_fold_respects_octets():
    line = "SUMMARY:" + "é" * 80
    for part in fold(line).split("\r\n"):
        assert len(part.encode()) <= 75


def test_render_structure_and_determinism():
    cal = Calendar(
        "Home",
        (
            Task("Filter", dt.date(2026, 11, 1), Interval(3, "month"), remind_days=7, notes="Size 20x25"),
            Task("Passport", dt.date(2030, 5, 1), remind_days=None),
        ),
    )
    out = render(cal)
    assert out == render(cal)
    assert out.startswith("BEGIN:VCALENDAR\r\n") and out.endswith("END:VCALENDAR\r\n")
    assert out.count("BEGIN:VEVENT") == 2
    assert "RRULE:FREQ=MONTHLY;INTERVAL=3" in out
    assert "DTSTART;VALUE=DATE:20261101" in out
    assert "TRIGGER:-P7D" in out
    assert out.count("BEGIN:VALARM") == 1
    assert "\n" not in out.replace("\r\n", "")
