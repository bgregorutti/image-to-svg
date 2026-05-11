from argparse import ArgumentParser
from pathlib import Path
import sys

import numpy as np
from PIL import Image


def get_arguments():
    parser = ArgumentParser()
    parser.add_argument("--input", required=True, help="Image file path. Accepted format: JPEG, JPG, PNG")
    parser.add_argument("--output", required=True, help="Output SVG file path")
    parser.add_argument("--colors", type=int, default=256, help="Number of colors for quantization (default: 256)")
    args = parser.parse_args()

    if Path(args.input).suffix.lower() not in (".png", ".jpeg", ".jpg"):
        parser.print_help()
        sys.exit(0)

    return args


def _rle_row(row):
    """Yield (x_start, run_length, color) for each horizontal run in a pixel row."""
    x = 0
    n = len(row)
    while x < n:
        color = tuple(row[x])
        start = x
        while x < n and tuple(row[x]) == color:
            x += 1
        yield start, x - start, color


def image_to_svg(image_path, output_path, num_colors=256):
    img = Image.open(image_path)

    if img.mode != 'RGB':
        img = img.convert('RGB')

    img = img.quantize(colors=num_colors).convert('RGB')

    width, height = img.size
    arr = np.array(img)  # shape (H, W, 3)

    # Single-pass: build color → list of (x, y, run_length) using RLE per row
    color_runs: dict[tuple, list] = {}
    for y in range(height):
        for x_start, run_len, color in _rle_row(arr[y]):
            color_runs.setdefault(color, []).append((x_start, y, run_len))

    parts = [
        f'<svg version="1.1" xmlns="http://www.w3.org/2000/svg" '
        f'xmlns:xlink="http://www.w3.org/1999/xlink" '
        f'width="{width}" height="{height}" viewBox="0 0 {width} {height}">\n'
    ]

    for color, runs in color_runs.items():
        r, g, b = color
        parts.append(f'  <g fill="rgb({r},{g},{b})">\n')
        for x, y, run_len in runs:
            parts.append(f'    <rect x="{x}" y="{y}" width="{run_len}" height="1"/>\n')
        parts.append('  </g>\n')

    parts.append('</svg>')

    Path("outputs").mkdir(exist_ok=True)
    with open(Path("outputs", output_path), 'w') as f:
        f.write("".join(parts))


def cli():
    args = get_arguments()
    image_to_svg(image_path=args.input, output_path=args.output, num_colors=args.colors)

