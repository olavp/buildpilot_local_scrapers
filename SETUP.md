# Setup

## Create Local Environment

```bash
cd /home/olav/apps/buildpilot_local_scrapers
python3 -m venv env
source env/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If `env/` already exists, update it with:

```bash
/home/olav/apps/buildpilot_local_scrapers/env/bin/pip install -r /home/olav/apps/buildpilot_local_scrapers/requirements.txt
```

## Run Manually

```bash
/home/olav/apps/buildpilot_local_scrapers/cron.py
```

## Cron

```cron
*/25 * * * * /home/olav/apps/buildpilot_local_scrapers/cron.py
```

## Notes

- The Python environment is local to this folder in `env/`.
- Firefox and `geckodriver` must be installed on the laptop outside the Python environment.
- `main.py` uses the Firefox profile path hardcoded in the script.
- `cron.py` is the small entry point and uses the local `env` Python via its shebang.
