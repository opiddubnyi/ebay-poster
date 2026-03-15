from pathlib import Path

import httpx

from poster.exceptions import MediaError


def upload_photos(
    photos: list[Path],
    access_token: str,
    media_base: str,
) -> list[str]:
    urls = []
    for photo in photos:
        if not photo.exists():
            raise MediaError(f"Photo not found: {photo}")
        url = _upload_single(photo, access_token, media_base)
        urls.append(url)
    return urls


def _upload_single(photo: Path, access_token: str, media_base: str) -> str:
    upload_url = f"{media_base}/commerce/media/v1_beta/image"
    with open(photo, "rb") as f:
        response = httpx.post(
            upload_url,
            headers={"Authorization": f"Bearer {access_token}"},
            files={"image": (photo.name, f, "image/jpeg")},
        )
    if response.status_code != 201:
        raise MediaError(f"Failed to upload {photo.name}: {response.text}")
    return response.json()["imageUrl"]
