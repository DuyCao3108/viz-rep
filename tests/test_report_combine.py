"""combine.py: vstack_images() stitches already-rendered PNGs into one review image."""

from PIL import Image

from src.report.combine import vstack_images


def test_vstack_images_dimensions(tmp_path):
    sizes = [(100, 50), (80, 30), (120, 60)]
    paths = []
    for i, (w, h) in enumerate(sizes):
        p = tmp_path / f"img{i}.png"
        Image.new("RGB", (w, h), (255, 0, 0)).save(p)
        paths.append(p)

    out_path = tmp_path / "combined.png"
    result = vstack_images(paths, out_path, gap_px=10)

    assert result == out_path
    assert out_path.exists()
    with Image.open(out_path) as combined:
        assert combined.width == max(w for w, h in sizes)
        assert combined.height == sum(h for w, h in sizes) + 10 * (len(sizes) - 1)


def test_vstack_images_centers_narrower_images(tmp_path):
    wide = tmp_path / "wide.png"
    narrow = tmp_path / "narrow.png"
    Image.new("RGB", (200, 40), (0, 255, 0)).save(wide)
    Image.new("RGB", (100, 40), (0, 0, 255)).save(narrow)

    out_path = tmp_path / "combined.png"
    vstack_images([wide, narrow], out_path, gap_px=0)

    with Image.open(out_path) as combined:
        assert combined.width == 200
        assert combined.getpixel((0, 40)) == (255, 255, 255)  # left of centered narrow image = bg
        assert combined.getpixel((100, 60)) == (0, 0, 255)  # inside centered narrow image


def test_vstack_images_handles_rgba_source(tmp_path):
    p = tmp_path / "a.png"
    Image.new("RGBA", (50, 50), (255, 0, 0, 128)).save(p)

    out_path = tmp_path / "out.png"
    vstack_images([p], out_path)

    with Image.open(out_path) as combined:
        assert combined.mode == "RGB"
        assert combined.size == (50, 50)
