import json
from pathlib import Path

from lifecal.cli import main, template_names
from lifecal.model import load


def test_every_template_is_valid(tmp_path: Path):
    names = template_names()
    assert "starter" in names and len(names) >= 5
    for name in names:
        out = tmp_path / f"{name}.yml"
        assert main(["init", name, "-o", str(out)]) == 0
        assert load(out).tasks


def test_init_build_upcoming_check(tmp_path: Path, capsys):
    life = tmp_path / "life.yml"
    assert main(["init", "-o", str(life)]) == 0
    assert main(["init", "-o", str(life)]) == 1  # refuses to overwrite
    assert main(["check", str(life)]) == 0
    assert main(["build", str(life)]) == 0
    assert (tmp_path / "life.ics").read_text().startswith("BEGIN:VCALENDAR")
    assert main(["upcoming", str(life), "--days", "3650"]) == 0
    assert "Passport expires" in capsys.readouterr().out


def test_bad_file_reports_problems(tmp_path: Path, capsys):
    bad = tmp_path / "bad.yml"
    bad.write_text("tasks:\n  - name: Oops\n")
    assert main(["check", str(bad)]) == 1
    assert "give either 'every'" in capsys.readouterr().err


def test_upcoming_json(tmp_path: Path, capsys):
    life = tmp_path / "life.yml"
    life.write_text(
        "tasks:\n"
        "  - name: Replace air filter\n"
        "    every: quarterly\n"
        "    start: 2020-01-01\n"
        "    notes: 16x25x1\n"
        "  - name: Renew passport\n"
        "    due: 2099-01-01\n"
    )
    assert main(["upcoming", str(life), "--days", "120", "--format", "json"]) == 0
    items = json.loads(capsys.readouterr().out)
    assert items
    first = items[0]
    assert set(first) == {"date", "days_left", "task", "every", "notes"}
    assert first["task"] == "Replace air filter"
    assert first["every"] == "3 months"
    assert first["notes"] == "16x25x1"
    assert 0 <= first["days_left"] <= 120
    assert all(item["task"] != "Renew passport" for item in items)


def test_upcoming_json_empty(tmp_path: Path, capsys):
    life = tmp_path / "life.yml"
    life.write_text("tasks:\n  - name: Renew passport\n    due: 2099-01-01\n")
    assert main(["upcoming", str(life), "--format", "json"]) == 0
    assert json.loads(capsys.readouterr().out) == []
