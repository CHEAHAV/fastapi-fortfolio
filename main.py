import cloudinary
from fastapi import FastAPI, Request, Response
from config import settings
from fastapi.responses import HTMLResponse, JSONResponse
from typing import Optional
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
import time
import uuid
from pathlib import Path 
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache
from redis import asyncio as aioredis
from collections import defaultdict
from starlette.routing import Route
import core.lib as core_lib
# from core import *

_get_lang = core_lib.get_lang

def _safe_get_lang(key, params=None, lang='en', path=''):
    lang = lang or 'en'
    if lang == 'km':
        lang = 'kh'

    try:
        return _get_lang(key, params=params, lang=lang, path=path)
    except ModuleNotFoundError:
        return _get_lang(key, params=params, lang='en', path=path)

core_lib.get_lang = _safe_get_lang

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION, 
    swagger_ui_parameters={"docExpansion": "none", "filter": True, "tagsSorter": "alpha",},
)

website = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION, 
    swagger_ui_parameters={"docExpansion": "none", "filter": True, "tagsSorter": "alpha",},
)

website.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

STATIC_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

app.mount("/api/v1/website", website)
    
@app.get("/custom/docs", include_in_schema=False)
async def custom_docs():
    if os.path.exists("templates/docs.html") :
        with open("templates/docs.html", encoding="utf-8") as f:  
            return HTMLResponse(f.read())
    return HTMLResponse("<h1>Docs template not found</h1>", status_code=404)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True,
)

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    request_id = str(uuid.uuid4())
    app.state.request_id = request_id

    # if check_app_is_offline(request) or check_system_is_offline(request):
    #     return offline_response()

    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    response.headers["X-Request-ID"] = request_id

    if os.getenv('ENABLE_LOG_REQUEST', 'NO') == 'YES' and not request.url.path.startswith('/static'):  
        response.headers.get("content-type", "")
        # if "text" in content_type or "json" in content_type or "html" in content_type:
        #     response_body = [chunk async for chunk in response.body_iterator]
        #     response.body_iterator = iterate_in_threadpool(iter(response_body))

    return response

def cache_key_builder(
    func,
    namespace: Optional[str] = "",
    request: Request | None = None,
    response: Response | None = None,
    *args,
    **kwargs,
):
    prefix = FastAPICache.get_prefix()
    cache_key = f"{prefix}:{namespace}:{func.__module__}:{func.__name__}:{args}:{kwargs}"
    return cache_key

@app.on_event("startup")
def startup():
    # https://pypi.org/project/fastapi-cache2/ 
    # https://www.digitalocean.com/community/tutorials/how-to-install-and-secure-redis-on-ubuntu-20-04
    # int cache with redis
    redis = aioredis.from_url(os.getenv("REDIS_URL", "redis://127.0.0.1:6379"), encoding="utf8", decode_responses=True)
    FastAPICache.init(RedisBackend(redis), prefix=f"fastapi-{settings.POSTGRES_DB}",key_builder=cache_key_builder)

# Path directory for uploads cv
UPLOAD_DIR = Path("uploads") / "cv"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@app.get('/', response_class=HTMLResponse, tags=["Home Page"])
async def home_page():
    html_path = "templates/home.html"
    static_path = "static"
    # for route in app.routes:
    #     print(route.path)
    if os.path.exists(html_path) and os.path.exists(static_path):
        with open(html_path, encoding="utf-8") as f:
            return HTMLResponse(f.read())
    html = '''
        <center>
        <h1>Welcome Backend Swinger</h1>
        <p><a href="/docs">Visit Backend API Document</a></p>
        <p><a href="/api/v1/website/docs">Visit Website API Document</a></p>
        </center>        
    '''
    return HTMLResponse(content=html, status_code=200)

from core.api.register import *
from modules.register import *
from modules.website.register import *


@app.on_event("startup")
def check_duplicate_routes():
    route_map = defaultdict(list)

    for route in app.routes:
        if isinstance(route, Route):
            for method in route.methods or []:
                key = (method, route.path)
                route_map[key].append(route.name)

    duplicates = {k: v for k, v in route_map.items() if len(v) > 1}
    
    if duplicates:
        print("Duplicate routes found:")
        for (method, path), handlers in duplicates.items():
            print(f"  {method} {path} -> {handlers}")
    # else:
    #     print("No duplicate routes found.")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
