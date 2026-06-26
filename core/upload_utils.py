import os
import shutil
import uuid
from pathlib import Path, PurePosixPath
from urllib.parse import unquote, urlparse
import cloudinary
import cloudinary.uploader
from fastapi import HTTPException, UploadFile

BASE_DIR = Path(__file__).resolve().parents[1]


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


def get_cloudinary_public_id(image_url: str | None) -> str | None:
    if not image_url:
        return None

    path_parts = urlparse(image_url).path.split("/")
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


def delete_cloudinary_image(image_url: str | None) -> None:
    public_id = get_cloudinary_public_id(image_url)
    if not public_id:
        return

    try:
        cloudinary.uploader.destroy(public_id, resource_type="image", invalidate=True)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Cloudinary delete failed: {exc}") from exc


def delete_cloudinary_icon(icon_url: str | None) -> None:
    public_id = get_cloudinary_public_id(icon_url)
    if not public_id:
        return

    try:
        cloudinary.uploader.destroy(public_id, resource_type="icon", invalidate=True)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Cloudinary delete failed: {exc}") from exc


def upload_image_to_cloudinary(upload: UploadFile, folder: str) -> str:
    if not upload.filename:
        raise HTTPException(status_code=400, detail="Uploaded file has no filename")

    cloudinary_url            = os.getenv("CLOUDINARY_URL")
    cloudinary_cloud_key_name = os.getenv("CLOUDINARY_CLOUD_KEY_NAME")
    cloud_name                = os.getenv("CLOUDINARY_CLOUD_NAME")
    api_key                   = os.getenv("CLOUDINARY_API_KEY")
    api_secret                = os.getenv("CLOUDINARY_API_SECRET")

    if not cloudinary_url and (not cloud_name or not api_key or not api_secret):
        raise HTTPException(status_code=500, detail="Cloudinary is not configured")

    if cloudinary_url:
        cloudinary.config(secure=True)
    else:
        cloudinary.config(
            cloud_name = cloud_name,
            api_key    = api_key,
            api_secret = api_secret,
            secure     = True,
        )

    source_name  = Path(upload.filename).name
    public_id    = f"{Path(source_name).stem or 'upload'}-{uuid.uuid4().hex}"
    prefix       = os.getenv("CLOUDINARY_FOLDER_PREFIX", cloudinary_cloud_key_name or "").strip("/")
    cloud_folder = f"{prefix}/{folder.strip('/')}" if prefix else folder.strip("/")

    try:
        upload.file.seek(0)
        result = cloudinary.uploader.upload(
            upload.file,
            folder        = cloud_folder,
            public_id     = public_id,
            resource_type = "image",
            overwrite     = False,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Cloudinary upload failed: {exc}") from exc

    secure_url = result.get("secure_url")
    if not secure_url:
        raise HTTPException(status_code=500, detail="Cloudinary upload did not return a secure URL")

    return secure_url


def upload_icon_to_cloudinary(upload: UploadFile, folder: str) -> str:
    if not upload.filename:
        raise HTTPException(status_code=400, detail="Uploaded file has no filename")

    cloudinary_url            = os.getenv("CLOUDINARY_URL")
    cloudinary_cloud_key_name = os.getenv("CLOUDINARY_CLOUD_KEY_NAME")
    cloud_name                = os.getenv("CLOUDINARY_CLOUD_NAME")
    api_key                   = os.getenv("CLOUDINARY_API_KEY")
    api_secret                = os.getenv("CLOUDINARY_API_SECRET")

    if not cloudinary_url and (not cloud_name or not api_key or not api_secret):
        raise HTTPException(status_code=500, detail="Cloudinary is not configured")

    if cloudinary_url:
        cloudinary.config(secure=True)
    else:
        cloudinary.config(
            cloud_name = cloud_name,
            api_key    = api_key,
            api_secret = api_secret,
            secure     = True,
        )

    source_name  = Path(upload.filename).name
    public_id    = f"{Path(source_name).stem or 'upload'}-{uuid.uuid4().hex}"
    prefix       = os.getenv("CLOUDINARY_FOLDER_PREFIX", cloudinary_cloud_key_name or "").strip("/")
    cloud_folder = f"{prefix}/{folder.strip('/')}" if prefix else folder.strip("/")

    try:
        upload.file.seek(0)
        result = cloudinary.uploader.upload(
            upload.file,
            folder        = cloud_folder,
            public_id     = public_id,
            resource_type = "image",
            overwrite     = False,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Cloudinary upload failed: {exc}") from exc

    secure_url = result.get("secure_url")
    if not secure_url:
        raise HTTPException(status_code=500, detail="Cloudinary upload did not return a secure URL")

    return secure_url
