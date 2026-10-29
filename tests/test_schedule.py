import datetime as dt

from lifecal.model import Interval, Task
from lifecal.schedule import add_months, occurrences, upcoming

D = dt.date


def test_add_months_clamps():
    assert add_months(D(2027, 1, 31), 1) == D(2027, 2, 28)
    assert add_months(D(2028, 1, 31), 1) == D(2028, 2, 29)
    assert add_months(D(2026, 11, 15), 3) == D(2027, 2, 15)


def test_occurrences_repeat_and_until():
    task = Task("x", D(2026, 1, 1), Interval(6, "month"), until=D(2027, 6, 1))
    assert list(occurrences(task, D(2030, 1, 1))) == [D(2026, 1, 1), D(2026, 7, 1), D(2027, 1, 1)]


def test_monthly_from_31st_does_not_drift():
    task = Task("x", D(2027, 1, 31), Interval(1, "month"))
    days = list(occurrences(task, D(2027, 4, 30)))
    assert days == [D(2027, 1, 31), D(2027, 2, 28), D(2027, 3, 31), D(2027, 4, 30)]


def test_upcoming_sorted_and_bounded():
    tasks = (
        Task("B", D(2026, 11, 10)),
        Task("A", D(2026, 10, 1), Interval(1, "month")),
        Task("Far", D(2031, 1, 1)),
    )
    rows = upcoming(tasks, today=D(2026, 10, 29), days=30)
    assert [(d, t.name) for d, t in rows] == [(D(2026, 11, 1), "A"), (D(2026, 11, 10), "B")]
