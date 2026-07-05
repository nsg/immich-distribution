from __future__ import annotations

import re
from pathlib import Path
from urllib.request import urlopen


APTLY_REPO = "https://nsg.github.io/aptly/"
REPO_ROOT = Path(__file__).resolve().parents[1]
SNAPCRAFT_YAML = REPO_ROOT / "snap" / "snapcraft.yaml"


def snapcraft_layout_version(pattern: str, name: str) -> str:
    snapcraft_yaml = SNAPCRAFT_YAML.read_text()
    matches = re.findall(pattern, snapcraft_yaml)
    assert matches, f"could not find {name} layout in {SNAPCRAFT_YAML}"

    unique_versions = set(matches)
    assert len(unique_versions) == 1, f"expected one {name} version, found: {sorted(unique_versions)}"
    return matches[0]


def packaged_version(package: str) -> str:
    with urlopen(APTLY_REPO, timeout=30) as response:
        aptly_index = response.read().decode()

    versions = re.findall(rf"{package}-(\d+\.\d+\.\d+)", aptly_index)
    assert versions, f"could not find {package} package version at {APTLY_REPO}"
    return versions[0]


def test_vips_modules_layout_matches_packaged_libvips() -> None:
    configured_version = snapcraft_layout_version(r"/usr/lib/vips-modules-(\d+\.\d+):", "vips module")

    major, minor, _patch = packaged_version("nsg-libvips").split(".")
    packaged = f"{major}.{minor}"

    assert configured_version == packaged, (
        "vips module layout does not match packaged libvips version\n"
        f"snapcraft.yaml points to: /usr/lib/vips-modules-{configured_version}\n"
        f"nsg-libvips package expects: /usr/lib/vips-modules-{packaged}\n"
        "Update snap/snapcraft.yaml to use:\n"
        f"  /usr/lib/vips-modules-{packaged}:\n"
        f"    symlink: $SNAP/usr/lib/vips-modules-{packaged}"
    )


def test_imagemagick_layout_matches_packaged_imagemagick() -> None:
    configured_version = snapcraft_layout_version(r"/usr/lib/ImageMagick-(\d+\.\d+\.\d+):", "ImageMagick")

    packaged = packaged_version("nsg-imagemagick")

    assert configured_version == packaged, (
        "ImageMagick layout does not match packaged ImageMagick version\n"
        "A mismatch silently breaks thumbnails for formats that need the\n"
        "ImageMagick fallback loader, like RAW\n"
        f"snapcraft.yaml points to: /usr/lib/ImageMagick-{configured_version}\n"
        f"nsg-imagemagick package expects: /usr/lib/ImageMagick-{packaged}\n"
        "Update snap/snapcraft.yaml to use:\n"
        f"  /usr/lib/ImageMagick-{packaged}:\n"
        f"    symlink: $SNAP/usr/lib/ImageMagick-{packaged}"
    )
