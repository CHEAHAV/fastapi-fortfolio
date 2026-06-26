# Online Shop Backend

This backend is configured for Python 3.14.

Use `python -m pip` instead of plain `pip` so dependencies install into the same Python runtime that starts the API.

```powershell
python -V
python -m pip install -r requirements.txt
python create_table.py
python -m uvicorn main:app --host 127.0.0.1 --port 8000
```

Default admin login after seeding:
