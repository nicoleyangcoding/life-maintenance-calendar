import datetime as dt

import pytest

from lifecal.model import ConfigError, Interval, parse, parse_interval, parse_remind


def test_parse_interval():
    assert parse_interval("3 months") == Interval(3, "month")
    assert parse_interval("1 Year") == Interval(1, "year")
    assert parse_interval("weekly") == Interval(1, "week")
    assert parse_interval("quarterly") == Interval(3, "month")
    with pytest.raises(ValueError):
        parse_interval("sometimes")
    with pytest.raises(ValueError):
        parse_interval("0 days")


def test_parse_remind():
    assert parse_remind("2 weeks before") == 14
    assert parse_remind("1 month before") == 30
    assert parse_remind("same day") == 0
    assert parse_remind("none") is None
    assert parse_remind(False) is None
    with pytest.raises(ValueError):
        parse_remind("soonish")


def test_parse_valid_file():
    cal = parse(
        {
            "calendar": {"name": "Home", "remind": "3 days before"},
            "tasks": [
                {"name": "Filter", "every": "3 months", "start": dt.date(2026, 11, 1)},
                {"name": "Passport", "due": "2030-05-01", "remind": "none"},
            ],
        }
    )
    assert cal.name == "Home"
    filt, passport = cal.tasks
    assert filt.every == Interval(3, "month") and filt.remind_days == 3
    assert passport.start == dt.date(2030, 5, 1) and passport.remind_days is None


def test_collects_every_problem():
    with pytest.raises(ConfigError) as err:
        parse(
            {
                "tasks": [
                    {"name": "No date"},
                    {"name": "Both", "every": "1 year", "due": "2030-01-01"},
                    {"name": "No start", "every": "1 year"},
                    {"name": "Bad date", "due": "next tuesday"},
                    {"name": "Typo", "due": "2030-01-01", "remindd": "1 day"},
                ]
            }
        )
    assert len(err.value.problems) == 5


def test_rejects_empty_and_wrong_shape():
    for data in (None, [], {"tasks": []}, {"tasks": "x"}):
        with pytest.raises(ConfigError):
            parse(data)


def test_warns_on_late_month_start():
    cal = parse({"tasks": [{"name": "Rent", "every": "monthly", "start": "2026-01-31"}]})
    assert cal.warnings
