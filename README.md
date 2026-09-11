# Portfolio Backend

This backend is configured for Python 3.14.

Use `python -m pip` instead of plain `pip` so dependencies install into the same Python runtime that starts the API.

```powershell
python -V
python -m pip install -r requirements.txt
python create_table.py
python -m uvicorn main:app --host 127.0.0.1 --port 8000
```

## PostgreSQL Setup

Skills have an optional `official_url` column (HTTP/HTTPS, up to 2048 characters).
Set it in the `create_skill` / `update_skill` form in `/docs`; admin and public
skill responses include the saved link. Omitting it on update preserves the
existing URL. To remove a link, submit an empty `official_url` form field.

For an existing database, run the focused migration **before** starting the new
backend. It adds only this column and fills the current technologies' official
links. Running it again preserves saved or deliberately cleared links.

```powershell
.\venv\Scripts\python.exe migrate_skill_official_url.py --target local
# Run against the hosted database before deploying the updated backend:
.\venv\Scripts\python.exe migrate_skill_official_url.py --target neon
```

New databases also get the column through `create_table.py`. Set the URL when
creating a skill. The frontend uses the API's saved `official_url`; known
technology links are a compatibility fallback only for older API deployments
that do not return this field.

This project can use local PostgreSQL for development and Neon PostgreSQL for hosting.

To check **all local tables and columns**, including tables outside the current
ORM models, compare them with Neon:

```powershell
.\venv\Scripts\python.exe check_database_schema.py
.\venv\Scripts\python.exe check_database_schema.py --apply-missing
```

The second command only creates missing tables and adds missing nullable columns.
It preserves rows and existing column definitions. Required/generated column
additions need a dedicated migration. Differences in existing types, nullability,
or defaults are reported with a nonzero exit code for review.

`GET /health` checks the API's selected database and returns 503 if it is unavailable.
It does not test external email or media delivery.

For local development, keep:

```env
DB_TARGET=local
CREATE_TABLE_TARGETS=local,neon
DB_USER=postgres
DB_PASSWORD=your_local_password
DB_SERVER=localhost
DB_PORT=5432
DB_NAME=your_local_database
```

For Neon or hosting, set:

```env
DB_TARGET=neon
NEON_DATABASE_URL=postgresql://neondb_owner:your_password@your-neon-host.neon.tech/Portfolio?sslmode=require
```

The API connects to the database selected by `DB_TARGET`. The table command uses `CREATE_TABLE_TARGETS`, so `local,neon` creates or syncs tables in both databases:

```powershell
python create_table.py
```

To copy future API create/update/delete writes to the other configured database, enable:

```env
MIRROR_DATABASE_WRITES=true
```

With `DB_TARGET=local`, the API writes to local PostgreSQL first, then mirrors the same row to Neon. Existing rows that were created before mirroring was enabled must be copied separately.

To copy existing local data to Neon:

```powershell
python sync_data.py
```

For hosting, add `DB_TARGET=neon` and `NEON_DATABASE_URL` to your hosting provider's environment variables. For local development, keep `DB_TARGET=local`. Do not commit your real `.env` file.

## Vercel Deployment

Vercel uses `.python-version`, which is set to Python 3.12 because Python 3.14 is not available in the Vercel runtime used by this project. Local development can still use the project `venv`.

Set these Vercel environment variables:

```env
DB_TARGET=neon
NEON_DATABASE_URL=postgresql://neondb_owner:your_password@your-neon-host.neon.tech/Portfolio?sslmode=require
MIRROR_DATABASE_WRITES=false
SECRET_KEY=your_secret_key
CORS_ORIGINS=https://your-frontend-domain.com
```

Add your Cloudinary variables too if uploads are used:

```env
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_cloud_api_key
CLOUDINARY_API_SECRET=your_cloud_api_secret
CLOUDINARY_FOLDER_PREFIX=hav-portfolio
```

Default admin login after seeding:
