"""Command-line interface: lifecal init | build | upcoming | check."""

from __future__ import annotations

import argparse
import datetime as dt
import sys
from importlib import resources
from pathlib import Path

from . import __version__, ics, model, schedule

DEFAULT_FILE = "life.yml"


def template_names() -> list[str]:
    folder = resources.files("lifecal") / "templates"
    return sorted(p.name.removesuffix(".yml") for p in folder.iterdir() if p.name.endswith(".yml"))


def read_template(name: str) -> str:
    return (resources.files("lifecal") / "templates" / f"{name}.yml").read_text(encoding="utf-8")


def _load(path: str) -> model.Calendar:
    cal = model.load(path)
    for warning in cal.warnings:
        print(f"warning: {warning}", file=sys.stderr)
    return cal


def cmd_init(args: argparse.Namespace) -> int:
    if args.list:
        print("\n".join(template_names()))
        return 0
    if args.template not in template_names():
        choices = ", ".join(template_names())
        print(f"Unknown template '{args.template}'. Choose from: {choices}", file=sys.stderr)
        return 2
    out = Path(args.output)
    if out.exists() and not args.force:
        print(f"{out} already exists. Use --force to replace it.", file=sys.stderr)
        return 1
    out.write_text(read_template(args.template), encoding="utf-8")
    print(f"Created {out} from the '{args.template}' template.")
    print(f"Edit the dates, then run: lifecal build {out}")
    return 0


def cmd_build(args: argparse.Namespace) -> int:
    cal = _load(args.file)
    out = Path(args.output) if args.output else Path(args.file).with_suffix(".ics")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(ics.render(cal).encode("utf-8"))
    print(f"Wrote {len(cal.tasks)} task(s) to {out}")
    return 0


def cmd_upcoming(args: argparse.Namespace) -> int:
    cal = _load(args.file)
    today = dt.date.today()
    rows = schedule.upcoming(cal.tasks, today, args.days)
    if not rows:
        print(f"Nothing due in the next {args.days} days.")
        return 0
    for day, task in rows:
        left = (day - today).days
        when = "today" if left == 0 else f"in {left} day{'' if left == 1 else 's'}"
        print(f"{day.isoformat()}  {when:<13}  {task.name}")
    return 0


def cmd_check(args: argparse.Namespace) -> int:
    cal = _load(args.file)
    repeating = sum(task.repeats for task in cal.tasks)
    print(f"{args.file} looks good: {len(cal.tasks)} task(s), {repeating} repeating.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="lifecal",
        description="Turn a plain-text list of life and home chores into a calendar you can subscribe to.",
    )
    parser.add_argument("--version", action="version", version=f"lifecal {__version__}")
    sub = parser.add_subparsers(dest="command", required=True, metavar="command")

    p = sub.add_parser("init", help="start a task file from a template")
    p.add_argument("template", nargs="?", default="starter", help="template name (default: starter)")
    p.add_argument("-o", "--output", default=DEFAULT_FILE, help=f"file to create (default: {DEFAULT_FILE})")
    p.add_argument("--list", action="store_true", help="show available templates")
    p.add_argument("--force", action="store_true", help="overwrite an existing file")
    p.set_defaults(func=cmd_init)

    p = sub.add_parser("build", help="write an .ics calendar file")
    p.add_argument("file", nargs="?", default=DEFAULT_FILE)
    p.add_argument("-o", "--output", help="where to write (default: same name, .ics)")
    p.set_defaults(func=cmd_build)

    p = sub.add_parser("upcoming", help="list what is due soon")
    p.add_argument("file", nargs="?", default=DEFAULT_FILE)
    p.add_argument("--days", type=int, default=90, help="how far ahead to look (default: 90)")
    p.set_defaults(func=cmd_upcoming)

    p = sub.add_parser("check", help="validate a task file")
    p.add_argument("file", nargs="?", default=DEFAULT_FILE)
    p.set_defaults(func=cmd_check)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.func(args)
    except model.ConfigError as exc:
        print("Could not read the task file:", file=sys.stderr)
        for problem in exc.problems:
            print(f"  - {problem}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
