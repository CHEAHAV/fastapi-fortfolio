import os
import shutil
import uuid
from pathlib import Path, PurePosixPath
from urllib.parse import unquote, urlparse
import cloudinary
import cloudinary.exceptions
import cloudinary.uploader
from dotenv import load_dotenv
from fastapi import HTTPException, UploadFile

BASE_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BASE_DIR / ".env")
ALLOWED_IMAGE_CONTENT_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
    "image/gif",
    "image/svg+xml",
    "image/x-icon",
    "image/vnd.microsoft.icon",
}


def resolve_upload_dir(directory: str) -> Path: 
    path = Path(directory)
    return path if path.is_absolute() else BASE_DIR / path


def save_upload_with_unique_name(upload: UploadFile, directory: str) -> str:
    if not upload.filename:
        raise HTTPException(status_code=400, detail="Uploaded file has no filename")

    upload_dir = resolve_upload_dir(directory)
    os.makedirs(upload_dir, exist_ok=True)
    source_name = Path(upload.filename).name
    suffix      = Path(source_name).suffix.lower()
    stem        = Path(source_name).stem or "upload"
    filename    = source_name
    dest        = upload_dir / filename

    if dest.exists(): 
        filename = f"{stem}-{uuid.uuid4().hex}{suffix}"
        dest     = upload_dir / filename

    with open(dest, "wb") as f:
        shutil.copyfileobj(upload.file, f)

    return filename


def is_remote_url(value: str | None) -> bool:
    return bool(value and value.startswith(("http://", "https://")))


def media_url(value: str | None) -> str:
    if not value:
        return ""
    return value if is_remote_url(value) else ""


def media_name(value: str | None) -> str:
    if not value:
        return ""

    path = urlparse(value).path if is_remote_url(value) else value
    return unquote(Path(path).name)


def _env_value(name: str) -> str:
    return os.getenv(name, "").strip()


def _sanitize_cloudinary_folder(folder: str) -> str:
    parts = [
        part.strip().replace("\\", "/").strip("/")
        for part in folder.split("/")
        if part.strip().strip("/")
    ]
    return "/".join(parts)


def _cloudinary_key_label() -> str:
    key_name = _env_value("CLOUDINARY_CLOUD_KEY_NAME")
    api_key  = _env_value("CLOUDINARY_API_KEY")
    if key_name and api_key:
        return f"{key_name} ({api_key[:4]}...{api_key[-4:]})"
    if api_key:
        return f"{api_key[:4]}...{api_key[-4:]}"
    return "configured API key"


def configure_cloudinary(require_secret: bool = True) -> None:
    cloudinary_url = _env_value("CLOUDINARY_URL")

    if cloudinary_url:
        parsed     = urlparse(cloudinary_url)
        cloud_name = parsed.hostname or ""
        api_key    = unquote(parsed.username or "")
        api_secret = unquote(parsed.password or "")
    else:
        cloud_name = _env_value("CLOUDINARY_CLOUD_NAME")
        api_key    = _env_value("CLOUDINARY_API_KEY")
        api_secret = _env_value("CLOUDINARY_API_SECRET")

    required_values = {"CLOUDINARY_CLOUD_NAME": cloud_name}
    if require_secret:
        required_values.update(
            {
                "CLOUDINARY_API_KEY": api_key,
                "CLOUDINARY_API_SECRET": api_secret,
            }
        )

    missing = [name for name, value in required_values.items() if not value]
    if missing:
        raise HTTPException(
            status_code=500,
            detail=f"Cloudinary is not configured. Missing: {', '.join(missing)}",
        )

    cloudinary.config(
        cloud_name = cloud_name,
        api_key    = api_key,
        api_secret = api_secret,
        secure     = True,
    )


def _validate_image_upload(upload: UploadFile) -> None:
    if not upload.filename:
        raise HTTPException(status_code=400, detail="Uploaded file has no filename")

    if upload.content_type and upload.content_type not in ALLOWED_IMAGE_CONTENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported image type: {upload.content_type}",
        )


def _cloudinary_folder(folder: str) -> str:
    prefix      = _env_value("CLOUDINARY_FOLDER_PREFIX") or _env_value("CLOUDINARY_CLOUD_KEY_NAME")
    folder_name = _sanitize_cloudinary_folder(folder)
    prefix_name = _sanitize_cloudinary_folder(prefix)
    return f"{prefix_name}/{folder_name}" if prefix_name else folder_name


def _upload_to_cloudinary(upload: UploadFile, folder: str) -> str:
    _validate_image_upload(upload)
    upload_preset = _env_value("CLOUDINARY_UPLOAD_PRESET")
    configure_cloudinary(require_secret=not upload_preset)

    source_name = Path(upload.filename or "upload").name
    public_id   = f"{Path(source_name).stem or 'upload'}-{uuid.uuid4().hex}"
    upload_options = {
        "folder": _cloudinary_folder(folder),
        "public_id": public_id,
        "resource_type": "image",
        "overwrite": False,
        "unique_filename": False,
    }

    if upload_preset:
        upload_options["upload_preset"] = upload_preset

    try:
        upload.file.seek(0)
        result = cloudinary.uploader.upload(upload.file, **upload_options)
    except HTTPException:
        raise
    except (cloudinary.exceptions.AuthorizationRequired, cloudinary.exceptions.NotAllowed) as exc:
        raise HTTPException(
            status_code=403,
            detail=(
                f"Cloudinary rejected API key {_cloudinary_key_label()}: {exc}. "
                "Use an API key with upload/create permission, or configure "
                "CLOUDINARY_UPLOAD_PRESET with an enabled unsigned upload preset."
            ),
        ) from exc
    except cloudinary.exceptions.BadRequest as exc:
        raise HTTPException(status_code=400, detail=f"Cloudinary upload rejected the file: {exc}") from exc
    except cloudinary.exceptions.RateLimited as exc:
        raise HTTPException(status_code=429, detail=f"Cloudinary rate limit reached: {exc}") from exc
    except Exception as exc:
        message = str(exc) or exc.__class__.__name__
        raise HTTPException(status_code=502, detail=f"Cloudinary upload failed: {message}") from exc

    secure_url = result.get("secure_url")
    if not secure_url:
        raise HTTPException(status_code=502, detail="Cloudinary upload did not return a secure URL")

    return secure_url


def get_cloudinary_public_id(image_url: str | None) -> str | None:
    value = (image_url or "").strip()
    if not value:
        return None

    if not is_remote_url(value):
        return str(PurePosixPath(unquote(value)).with_suffix(""))

    path_parts = urlparse(value).path.split("/")
    if "upload" not in path_parts:
        return None

    upload_index    = path_parts.index("upload")
    public_id_parts = path_parts[upload_index + 1:]
    if public_id_parts and public_id_parts[0].startswith("v") and public_id_parts[0][1:].isdigit(): 
        public_id_parts = public_id_parts[1:]

    if not public_id_parts:
        return None

    public_id_path = unquote("/".join(public_id_parts))
    return str(PurePosixPath(public_id_path).with_suffix(""))


def _delete_cloudinary_asset(image_url: str | None) -> None:
    public_id = get_cloudinary_public_id(image_url)
    if not public_id:
        return

    try:
        configure_cloudinary()
        result = cloudinary.uploader.destroy(public_id, resource_type="image", invalidate=True)
    except (cloudinary.exceptions.AuthorizationRequired, cloudinary.exceptions.NotAllowed) as exc:
        raise HTTPException(
            status_code=403,
            detail=f"Cloudinary rejected API key {_cloudinary_key_label()}: {exc}",
        ) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Cloudinary delete failed: {exc}") from exc

    delete_result = result.get("result") if isinstance(result, dict) else None
    if delete_result != "ok":
        raise HTTPException(
            status_code=502,
            detail=f"Cloudinary did not delete {public_id}: {result}",
        )


def delete_cloudinary_image(image_url: str | None) -> None:
    _delete_cloudinary_asset(image_url)


def delete_cloudinary_icon(icon_url: str | None) -> None:
    _delete_cloudinary_asset(icon_url)


def upload_image_to_cloudinary(upload: UploadFile, folder: str) -> str:
    return _upload_to_cloudinary(upload, folder)


def upload_icon_to_cloudinary(upload: UploadFile, folder: str) -> str:
    return _upload_to_cloudinary(upload, folder)
