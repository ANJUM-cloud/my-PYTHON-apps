# CareerTrack

A full-stack Python web application starter.

## Features
- Account registration and sign-in
- Secure password hashing and session management
- User-specific records and ownership checks
- Create, update, and delete workflows
- CSRF protection on POST forms
- Responsive dashboard
- SQLite local database; configurable PostgreSQL URL
- `/health` endpoint and Gunicorn deployment entry point

## Run locally
Python 3.10+ is required.

```bash
python -m venv .venv
# Windows PowerShell
.venv\\Scripts\\Activate.ps1
# macOS / Linux
source .venv/bin/activate
pip install -r requirements.txt
# Copy .env.example to .env and set SECRET_KEY
python app.py
```
Open http://127.0.0.1:5000

## Tests
```bash
pytest -q
```

## Deploy to Render or another Python host
1. Push this folder to a Git repository.
2. Create a Python Web Service.
3. Build command: `pip install -r requirements.txt`
4. Start command: `gunicorn app:app`
5. Configure `SECRET_KEY` with a long random value.
6. Configure `DATABASE_URL` with a managed PostgreSQL connection string.
7. Set `COOKIE_SECURE=1` when HTTPS is active.
8. Deploy and verify `/health`.

SQLite is for local development. Use managed PostgreSQL for multi-instance production.
The app creates tables automatically for a starter/demo. Add Flask-Migrate before evolving a production schema.

## Project structure
- `app.py` — app factory, models, auth, routes
- `templates/` — Jinja pages
- `static/style.css` — responsive styling
- `tests/` — pytest smoke tests
- `requirements.txt` — dependencies
- `Procfile` — production process command

## Learning roadmap
1. Trace `create_app()` and extension initialization.
2. Study the SQLAlchemy model and `user_id` ownership.
3. Follow the register → login → dashboard flow.
4. Add search, pagination, CSV export, and REST endpoints.
5. Add migrations, rate limiting, email verification, and password reset.

## Production hardening checklist
- Replace the development secret and store secrets only in host environment variables.
- Use PostgreSQL with backups.
- Enable HTTPS and secure cookies.
- Add authentication rate limiting and account recovery.
- Add migrations, monitoring, structured logging, and error reporting.
- Add pagination and input constraints for larger datasets.
- Review privacy and security requirements before storing real user data.

This is a runnable advanced learning project and deployment-oriented starter, not a security-audited enterprise product.
