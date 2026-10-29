# Contributing

Thanks for helping. Small pull requests are easiest to review.

## Add a template

1. Copy `src/lifecal/templates/starter.yml` to `src/lifecal/templates/<name>.yml`.
2. Use widely accepted, general intervals. Add a `notes:` line when people should check their own manual or professional.
3. Run the tests (below). Every template is checked automatically.
4. Add a row to the Templates table in `README.md`.

## Development setup

```bash
git clone https://github.com/nicoleyangcoding/life-maintenance-calendar
cd life-maintenance-calendar
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest
ruff check . && ruff format --check .
```

## Guidelines

- Keep it dependency-light. PyYAML is the only runtime dependency.
- No network access at runtime.
- Error messages should tell the user what to type to fix the problem.
