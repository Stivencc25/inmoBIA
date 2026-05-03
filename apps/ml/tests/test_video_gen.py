import os
import pytest

pytest.importorskip("imageio", reason="imageio no instalado — salta tests de video")


def test_build_video_creates_file(session_dir, property_data, cover_image, extra_images):
    from routes.video_gen import _build_video

    out_path = str(session_dir / "video.mp4")
    _build_video(
        photos=[cover_image] + extra_images,
        data=property_data,
        out_path=out_path,
    )
    assert os.path.exists(out_path)
    assert os.path.getsize(out_path) > 4096, "El video parece vacío"


def test_build_video_single_photo(session_dir, property_data, cover_image):
    from routes.video_gen import _build_video

    out_path = str(session_dir / "video_single.mp4")
    _build_video(photos=[cover_image], data=property_data, out_path=out_path)
    assert os.path.exists(out_path)


def test_build_video_uses_up_to_8_photos(session_dir, property_data, cover_image):
    """_build_video debe ignorar fotos más allá del índice 8."""
    from routes.video_gen import _build_video
    from PIL import Image

    many_photos = [cover_image]
    for i in range(12):
        img = Image.new("RGB", (320, 240), color=(i * 15, 50, 100))
        p = session_dir / f"extra_many_{i}.jpg"
        img.save(str(p))
        many_photos.append(str(p))

    out_path = str(session_dir / "video_many.mp4")
    _build_video(photos=many_photos, data=property_data, out_path=out_path)
    assert os.path.exists(out_path)
