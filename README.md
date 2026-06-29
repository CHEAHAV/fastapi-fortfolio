# Online Shop Backend

This backend is configured for Python 3.14.

Use `python -m pip` instead of plain `pip` so dependencies install into the same Python runtime that starts the API.

```powershell
python -V
python -m pip install -r requirements.txt
python create_table.py
python -m uvicorn main:app --host 127.0.0.1 --port 8000
```

## PostgreSQL Setup

This project can use local PostgreSQL for development and Neon PostgreSQL for hosting.

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

Default admin login after seeding:
