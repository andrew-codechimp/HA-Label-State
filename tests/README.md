# Label State tests

The suite uses `pytest-homeassistant-custom-component`, following the shared
fixtures, parameterized tests, and Syrupy snapshots pattern.

Run commands from the repository root:

```bash
./scripts/setup
uv run --no-sync pytest
uv run --no-sync pytest --cov=custom_components.label_state --cov-report=term-missing
uv run --no-sync ruff check .
uv run --no-sync ruff format --check .
uv run --no-sync mypy
```

VS Code provides `Tests: All with Coverage` (the default test task), `Tests: All`,
and `Tests: Current File`. The coverage task also writes an HTML report to
`htmlcov/index.html`.

The GitHub `Tests` workflow runs on relevant pushes and pull requests to `main`,
and can be started manually. It installs dependencies from `uv.lock` and runs
the full suite.

The tests cover:

- State and inverse state matching, numeric boundaries, and invalid readings.
- Label membership, label renaming/deletion, self-labeling, and source names.
- Menu and options flows, numeric validation, setup, reload, and listener cleanup.

`mock_config_entry` accepts option overrides with indirect parametrization.
`setup_integration` loads the helper. A frozen clock keeps entity timestamps
stable.

Entity metadata is captured in `snapshots/*.ambr`. After intentional output
changes, regenerate and review the snapshots:

```bash
uv run --no-sync pytest tests --snapshot-update
```
