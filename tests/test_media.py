import httpx
import respx
import pytest
from pathlib import Path
from poster.media import upload_photos
from poster.exceptions import MediaError


SANDBOX_MEDIA_URL = "https://apim.sandbox.ebay.com/commerce/media/v1_beta/image"


@respx.mock
def test_upload_single_photo(tmp_path):
    photo = tmp_path / "jersey.jpg"
    photo.write_bytes(b"\xff\xd8\xff\xe0" + b"\x00" * 100)  # minimal JPEG header

    respx.post(SANDBOX_MEDIA_URL).mock(
        return_value=httpx.Response(201, json={
            "imageUrl": "https://i.ebayimg.com/images/g/test/s-l1600.jpg",
        })
    )

    urls = upload_photos(
        photos=[photo],
        access_token="test_token",
        media_base="https://apim.sandbox.ebay.com",
    )
    assert urls == ["https://i.ebayimg.com/images/g/test/s-l1600.jpg"]


@respx.mock
def test_upload_multiple_photos(tmp_path):
    photos = []
    for i in range(3):
        p = tmp_path / f"photo_{i}.jpg"
        p.write_bytes(b"\xff\xd8\xff\xe0" + b"\x00" * 100)
        photos.append(p)

    respx.post(SANDBOX_MEDIA_URL).mock(side_effect=[
        httpx.Response(201, json={"imageUrl": f"https://i.ebayimg.com/{i}.jpg"})
        for i in range(3)
    ])

    urls = upload_photos(
        photos=photos,
        access_token="test_token",
        media_base="https://apim.sandbox.ebay.com",
    )
    assert len(urls) == 3


@respx.mock
def test_upload_failure(tmp_path):
    photo = tmp_path / "bad.jpg"
    photo.write_bytes(b"\x00" * 10)

    respx.post(SANDBOX_MEDIA_URL).mock(
        return_value=httpx.Response(400, json={"errors": [{"message": "Invalid image"}]})
    )

    with pytest.raises(MediaError, match="Failed to upload"):
        upload_photos(
            photos=[photo],
            access_token="test_token",
            media_base="https://apim.sandbox.ebay.com",
        )


def test_upload_nonexistent_file():
    with pytest.raises(MediaError, match="not found"):
        upload_photos(
            photos=[Path("/nonexistent/photo.jpg")],
            access_token="test_token",
            media_base="https://apim.sandbox.ebay.com",
        )
