#!/usr/bin/env python3
"""
Image Upscaler for Print / Billboard Output
============================================
Upscales an image to a target physical print size and exports as PDF or high-res image.

Usage:
    python image_upscaler.py input.jpg --width 3 --height 2 --unit ft --dpi 150
    python image_upscaler.py input.png --width 90 --height 60 --unit cm --dpi 100 --output my_banner.pdf
    python image_upscaler.py input.jpeg --width 24 --height 16 --unit in --dpi 300 --format jpg

Requirements:
    pip install Pillow reportlab opencv-python-headless
"""

import argparse
import os
import sys
import cv2
import numpy as np
from PIL import Image


# ── Unit conversion to inches ──────────────────────────────────────────────────
UNIT_TO_INCHES = {
    "in":  1.0,
    "ft":  12.0,
    "cm":  1 / 2.54,
    "mm":  1 / 25.4,
    "m":   100 / 2.54,
}

SUPPORTED_INPUT_FORMATS = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif", ".webp"}


def parse_args():
    parser = argparse.ArgumentParser(
        description="Upscale an image to a target print size and export as PDF or image."
    )
    parser.add_argument("input", help="Path to the input image (jpg, png, etc.)")
    parser.add_argument("--width",  type=float, required=True, help="Target print width")
    parser.add_argument("--height", type=float, required=True, help="Target print height")
    parser.add_argument(
        "--unit", default="in",
        choices=["in", "ft", "cm", "mm", "m"],
        help="Unit for width/height (default: in)"
    )
    parser.add_argument(
        "--dpi", type=int, default=150,
        help="Print DPI — 100-150 for large format/billboards, 300 for close-up print (default: 150)"
    )
    parser.add_argument(
        "--format", default="pdf",
        choices=["pdf", "jpg", "jpeg", "png", "tiff"],
        help="Output format (default: pdf)"
    )
    parser.add_argument(
        "--output", default=None,
        help="Output file path (default: auto-named next to input file)"
    )
    parser.add_argument(
        "--sharpen", type=float, default=1.5,
        help="Sharpening strength after upscale: 1.0 = none, 1.5 = moderate, 2.0 = strong (default: 1.5)"
    )
    parser.add_argument(
        "--quality", type=int, default=95,
        help="JPEG output quality 1-100 (default: 95, only applies to jpg/jpeg output)"
    )
    return parser.parse_args()


def validate_input(path: str) -> None:
    if not os.path.exists(path):
        sys.exit(f"Error: Input file not found: '{path}'")
    ext = os.path.splitext(path)[1].lower()
    if ext not in SUPPORTED_INPUT_FORMATS:
        sys.exit(
            f"Error: Unsupported input format '{ext}'.\n"
            f"Supported: {', '.join(sorted(SUPPORTED_INPUT_FORMATS))}"
        )


def compute_target_pixels(width: float, height: float, unit: str, dpi: int) -> tuple[int, int]:
    """Convert physical dimensions + DPI to pixel dimensions."""
    inches_per_unit = UNIT_TO_INCHES[unit]
    width_in  = width  * inches_per_unit
    height_in = height * inches_per_unit
    px_w = int(round(width_in  * dpi))
    px_h = int(round(height_in * dpi))
    return px_w, px_h


def upscale_image(img: Image.Image, target_w: int, target_h: int) -> Image.Image:
    """Upscale using Lanczos (best for print: sharp text, clean edges)."""
    return img.resize((target_w, target_h), Image.LANCZOS)


def sharpen_image(img: Image.Image, strength: float) -> Image.Image:
    """Apply unsharp mask to restore crispness after upscaling."""
    if strength <= 1.0:
        return img

    arr = np.array(img)
    # Handle both RGB and RGBA
    if arr.shape[2] == 4:
        rgb, alpha = arr[:, :, :3], arr[:, :, 3]
        bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
    else:
        alpha = None
        bgr = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)

    blurred   = cv2.GaussianBlur(bgr, (0, 0), 3)
    sharpened = cv2.addWeighted(bgr, strength, blurred, -(strength - 1), 0)

    result_rgb = cv2.cvtColor(sharpened, cv2.COLOR_BGR2RGB)

    if alpha is not None:
        result_rgba = np.dstack((result_rgb, alpha))
        return Image.fromarray(result_rgba.astype(np.uint8))
    return Image.fromarray(result_rgb.astype(np.uint8))


def default_output_path(input_path: str, fmt: str) -> str:
    base = os.path.splitext(input_path)[0]
    ext  = "jpg" if fmt == "jpeg" else fmt
    return f"{base}_upscaled.{ext}"


def save_as_pdf(img: Image.Image, output_path: str,
                width_in: float, height_in: float, dpi: int) -> None:
    """Embed the upscaled image in a PDF sized to the exact print dimensions."""
    try:
        from reportlab.pdfgen import canvas as rl_canvas
    except ImportError:
        sys.exit(
            "Error: reportlab is required for PDF output.\n"
            "Install with:  pip install reportlab"
        )

    # Save a temp high-quality JPEG for embedding
    tmp_jpg = output_path.replace(".pdf", "_tmp_embed.jpg")
    # Convert RGBA → RGB if needed before saving JPEG
    if img.mode == "RGBA":
        background = Image.new("RGB", img.size, (255, 255, 255))
        background.paste(img, mask=img.split()[3])
        img = background
    elif img.mode != "RGB":
        img = img.convert("RGB")

    img.save(tmp_jpg, format="JPEG", quality=97, dpi=(dpi, dpi))

    # 1 inch = 72 PDF points
    page_w_pts = width_in  * 72
    page_h_pts = height_in * 72

    c = rl_canvas.Canvas(output_path, pagesize=(page_w_pts, page_h_pts))
    c.setTitle(os.path.basename(output_path))
    c.drawImage(tmp_jpg, 0, 0, width=page_w_pts, height=page_h_pts, preserveAspectRatio=False)
    c.save()

    os.remove(tmp_jpg)


def save_as_image(img: Image.Image, output_path: str,
                  fmt: str, dpi: int, quality: int) -> None:
    save_kwargs = {"dpi": (dpi, dpi)}

    if fmt in ("jpg", "jpeg"):
        if img.mode == "RGBA":
            bg = Image.new("RGB", img.size, (255, 255, 255))
            bg.paste(img, mask=img.split()[3])
            img = bg
        elif img.mode != "RGB":
            img = img.convert("RGB")
        save_kwargs["quality"]  = quality
        save_kwargs["optimize"] = True
        img.save(output_path, format="JPEG", **save_kwargs)

    elif fmt == "png":
        save_kwargs["compress_level"] = 6
        img.save(output_path, format="PNG", **save_kwargs)

    elif fmt in ("tiff", "tif"):
        save_kwargs["compression"] = "tiff_lzw"
        img.save(output_path, format="TIFF", **save_kwargs)

    else:
        img.save(output_path, **save_kwargs)


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    args = parse_args()

    validate_input(args.input)

    # Compute target pixel dimensions
    target_px_w, target_px_h = compute_target_pixels(
        args.width, args.height, args.unit, args.dpi
    )

    width_in  = args.width  * UNIT_TO_INCHES[args.unit]
    height_in = args.height * UNIT_TO_INCHES[args.unit]

    # Determine output path
    output_path = args.output or default_output_path(args.input, args.format)
    if not output_path.lower().endswith(f".{args.format}"):
        output_path += f".{args.format}"

    # Load image
    print(f"\n📂  Input : {args.input}")
    img = Image.open(args.input)
    orig_w, orig_h = img.size
    print(f"    Size  : {orig_w} × {orig_h} px  |  mode: {img.mode}")

    # Print summary
    print(f"\n🎯  Target : {args.width}{args.unit} × {args.height}{args.unit}"
          f"  ({width_in:.2f}\" × {height_in:.2f}\")")
    print(f"    DPI    : {args.dpi}")
    print(f"    Pixels : {target_px_w} × {target_px_h} px"
          f"  (scale: {target_px_w / orig_w:.2f}×)")
    print(f"    Format : {args.format.upper()}")
    print(f"    Sharpen: {args.sharpen}×")

    if target_px_w < orig_w or target_px_h < orig_h:
        print("\n⚠️  Warning: target size is SMALLER than the original. "
              "Image will be downscaled, not upscaled.")

    # Process
    print("\n⏳  Upscaling...")
    img = upscale_image(img, target_px_w, target_px_h)

    if args.sharpen > 1.0:
        print("✨  Sharpening...")
        img = sharpen_image(img, args.sharpen)

    # Save
    print(f"💾  Saving → {output_path}")
    if args.format == "pdf":
        save_as_pdf(img, output_path, width_in, height_in, args.dpi)
    else:
        save_as_image(img, output_path, args.format, args.dpi, args.quality)

    size_mb = os.path.getsize(output_path) / (1024 * 1024)
    print(f"\n✅  Done!  Output: {output_path}  ({size_mb:.1f} MB)\n")


if __name__ == "__main__":
    main()