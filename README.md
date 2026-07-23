# my-fastapi-backend

A minimal **FastAPI** demo backend, ready to deploy on **Databricks Apps**.

## Endpoints

| Method | Path              | Description                          |
| ------ | ----------------- | ------------------------------------ |
| GET    | `/`               | Service info                         |
| GET    | `/health`         | Health check (readiness probe)       |
| GET    | `/env`            | Selected Databricks environment vars |
| GET    | `/items`          | List all items                       |
| GET    | `/items/{id}`     | Get an item by id                    |
| POST   | `/items`          | Create an item                       |
| DELETE | `/items/{id}`     | Delete an item                       |

Interactive API docs are served at `/docs` (Swagger UI) and `/redoc`.

## Project structure

```
my-fastapi-backend/
├── app.py            # FastAPI application
├── app.yaml          # Databricks Apps entrypoint / run command
├── requirements.txt  # Python dependencies
└── .gitignore
```

## Run locally

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app:app --reload
```

Then open http://127.0.0.1:8000/docs.

## Deploy to Databricks Apps

Databricks Apps runs the process defined in `app.yaml`. The platform injects the
port to bind to via the `DATABRICKS_APP_PORT` environment variable, which the
run command references.

### Option A — Databricks CLI

```bash
# 1. Create the app (once)
databricks apps create my-fastapi-backend

# 2. Sync this folder to your workspace
databricks sync . /Workspace/Users/<you>/my-fastapi-backend

# 3. Deploy
databricks apps deploy my-fastapi-backend \
  --source-code-path /Workspace/Users/<you>/my-fastapi-backend
```

### Option B — Databricks UI

1. In your workspace, go to **Compute → Apps → Create app**.
2. Choose **Custom** app.
3. Upload / point it to this repository folder (must contain `app.yaml`).
4. Click **Deploy**.

Once deployed, open the app URL and append `/docs` to explore the API.

## Notes

- `app.yaml` must be at the root of the deployed folder.
- Do not hard-code the port; always bind to `$DATABRICKS_APP_PORT`.
- Keep dependencies pinned in `requirements.txt` for reproducible builds.