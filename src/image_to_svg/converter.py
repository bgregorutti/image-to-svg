from argparse import ArgumentParser
from pathlib import Path
import sys

from PIL import Image
from tqdm import tqdm

def get_arguments():
    parser = ArgumentParser()
    parser.add_argument("--input", required=True, help="Image file path. Accepted format: JPEG, JPG, PNG")
    parser.add_argument("--output", required=True, help="Output SVG file path")
    args = parser.parse_args()

    if Path(args.input).suffix.lower() not in (".png", ".jpeg", ".jpg"):
        parser.print_help()
        sys.exit(0)

    return args

def image_to_svg(image_path, output_path):
    img = Image.open(image_path)
    img = img.resize((32, 32))
    width, height = img.size
    print(width, height)

    # Convert image to RGB if it's not already
    if img.mode != 'RGB':
        img = img.convert('RGB')

    colors = img.getcolors(width * height)
    color_map = {}
    for count, color in colors:
        if color not in color_map:
            color_map[color] = []
        color_map[color].append(count)

    svg_content = f'''<svg version="1.1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{width}" height="{height}" viewBox="0 0 {width} {height}">'''
    for color, _ in tqdm(color_map.items()):
            svg_content += f'  <g fill="rgb{color}">\n'
            for y in range(height):
                for x in range(width):
                    if img.getpixel((x, y)) == color:
                        svg_content += f'    <rect x="{x}" y="{y}" width="1" height="1" />\n'
            svg_content += '  </g>\n'
    
    svg_content += "</svg>"
    
    Path("outputs").mkdir(exist_ok=True)
    with open(Path("outputs", output_path), 'w') as f:
        f.write(svg_content)

def cli():
    args = get_arguments()
    image_to_svg(image_path=args.input, output_path=args.output)
