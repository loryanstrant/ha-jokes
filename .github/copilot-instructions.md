# Copilot instructions — ha-jokes

> Canonical standards live in the `dev-standards` repo on SOUNDWAVE/Gitea.
> Read by Copilot chat **and** inline suggestions. For full HA build conventions,
> see the `build-ha-component` skill in dev-standards.

## What this repo is

A **Home Assistant custom component** — a sensor that serves jokes, with a
service to fetch new ones. Domain: `ha_jokes`.

## Repo shape

- `custom_components/ha_jokes/` — `manifest.json`, `__init__.py`,
  `config_flow.py`, `const.py`, `sensor.py`, `services.yaml`, `strings.json`.
- `hacs.json`, `info.md`, `BREAKING_CHANGES.md`, `.github/workflows/`.

## Conventions

- Bump `manifest.json` **version** every release (semver); `domain` matches the
  folder name. Note `BREAKING_CHANGES.md` — keep it updated when behaviour shifts.
- Any new/changed service must be reflected in `services.yaml` + `strings.json`.
- Test: `hassfest` + HACS validation, then `pytest` with
  `pytest-homeassistant-custom-component`.
- Deploy/test via the published release artifact into TEST1/TEST2, not host
  file-copy. Backup + auto-rollback.

## Never

- Don't commit HA long-lived tokens or deploy keys — Gitea Actions secrets only.
