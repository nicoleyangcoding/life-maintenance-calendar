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


def test_check_warns_about_past_due_dates(tmp_path: Path, capsys):
    life = tmp_path / "life.yml"
    life.write_text("tasks:\n  - name: Old filing\n    due: 2001-04-15\n")
    assert main(["check", str(life)]) == 0
    assert "warning: task 1 (Old filing): due 2001-04-15 has already passed" in capsys.readouterr().err


def test_build_combines_files(tmp_path: Path, capsys):
    home = tmp_path / "home.yml"
    car = tmp_path / "car.yml"
    home.write_text(
        "calendar:\n  name: Home\n"
        "tasks:\n  - name: Replace air filter\n    every: quarterly\n    start: 2027-01-01\n"
    )
    car.write_text(
        "calendar:\n  name: Car\n  remind: none\n"
        "tasks:\n"
        "  - name: Oil change\n    every: 6 months\n    start: 2027-01-15\n"
        "  - name: Replace Air Filter\n    every: 1 year\n    start: 2027-04-01\n"
    )
    out = tmp_path / "all.ics"
    assert main(["build", str(home), str(car), "-o", str(out)]) == 0
    text = out.read_text()
    assert text.count("BEGIN:VEVENT") == 3
    assert "X-WR-CALNAME:Life maintenance" in text
    assert text.count("BEGIN:VALARM") == 1  # each file keeps its own reminder default
    captured = capsys.readouterr()
    assert "Wrote 3 task(s)" in captured.out
    assert f"warning: {car}: 'Replace Air Filter' is also in {home}" in captured.err

    assert main(["build", str(home), str(car), "-o", str(out), "--name", "Everything"]) == 0
    assert "X-WR-CALNAME:Everything" in out.read_text()
    capsys.readouterr()

    assert main(["upcoming", str(home), str(car), "--days", "3650", "--format", "json"]) == 0
    assert {"Oil change", "Replace air filter"} <= {i["task"] for i in json.loads(capsys.readouterr().out)}
    assert main(["check", str(home), str(car)]) == 0
    assert "3 task(s)" in capsys.readouterr().out


def test_combined_problems_name_the_file(tmp_path: Path, capsys):
    good = tmp_path / "good.yml"
    good.write_text("tasks:\n  - name: Renew passport\n    due: 2099-01-01\n")
    assert main(["check", str(good), str(tmp_path / "missing.yml")]) == 1
    assert f"{tmp_path / 'missing.yml'}: " in capsys.readouterr().err


def test_build_default_output_for_several_files(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    for name in ("a.yml", "b.yml"):
        (tmp_path / name).write_text(f"tasks:\n  - name: Task {name}\n    due: 2099-01-01\n")
    assert main(["build", "a.yml", "b.yml"]) == 0
    assert (tmp_path / "life.ics").read_text().count("BEGIN:VEVENT") == 2
