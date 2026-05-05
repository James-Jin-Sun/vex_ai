from __future__ import annotations

from pathlib import Path

from PIL import Image

try:
    from pillow_heif import register_heif_opener
except ImportError as exc:
    raise SystemExit(
        "Missing dependency 'pillow-heif'. Install it with: pip install pillow pillow-heif"
    ) from exc


register_heif_opener()


SOURCE_DIR = Path(r"C:\Users\14zj2\OneDrive\VEX AI Dataset")
OUTPUT_DIR = Path(r"D:\VEX_AI\oppo_robot_dataset")
OUTPUT_PREFIX = "opponent_"
JPEG_QUALITY = 95


def iter_heic_files(source_dir: Path) -> list[Path]:
    patterns = ("*.heic", "*.HEIC", "*.heif", "*.HEIF")
    files: list[Path] = []
    for pattern in patterns:
        files.extend(source_dir.rglob(pattern))
    return sorted(set(files), key=lambda path: str(path).lower())


def convert_image(source_path: Path, destination_path: Path) -> None:
    with Image.open(source_path) as image:
        converted = image.convert("RGB")
        converted = converted.resize((640, 640), Image.LANCZOS)
        converted.save(destination_path, "JPEG", quality=JPEG_QUALITY)


def main() -> None:
    if not SOURCE_DIR.exists():
        raise SystemExit(f"Source folder not found: {SOURCE_DIR}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    source_files = iter_heic_files(SOURCE_DIR)

    if not source_files:
        raise SystemExit(f"No HEIC/HEIF files found in: {SOURCE_DIR}")

    for index, source_path in enumerate(source_files, start=1):
        destination_name = f"{OUTPUT_PREFIX}{index:04d}.jpg"
        destination_path = OUTPUT_DIR / destination_name
        convert_image(source_path, destination_path)
        print(f"Converted {source_path.name} -> {destination_name}")

    print(f"Converted {len(source_files)} files into: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()