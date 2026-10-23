import io
import requests
from PIL import Image, ImageFont, ImageDraw

def get_material_icon_url(material_id):
    url = f"https://api.encore.moe/zh-Hant/item/{material_id}"
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    data = response.json()
    return data["Icon"]

def download_material_icon(icon_url):
    response = requests.get(icon_url, timeout=10)
    response.raise_for_status()

    image = Image.open(io.BytesIO(response.content))
    return image.convert("RGBA")

def create_material_image(materials):
    columns = 4
    cell_width = 180
    cell_height = 200
    rows = (len(materials)+columns - 1) // columns
    width = min(len(materials), columns) * cell_width
    height = rows * cell_height
    canvas = Image.new("RGBA", (width, height), (35,40,50,255))
    draw = ImageDraw.Draw(canvas)
    font = ImageFont.truetype("C:/Windows/Fonts/msjh.ttc", 16)
    for index, material in enumerate(materials):
        name = material["material_name"]
        quantity = material["quantity"]
        column = index % columns
        row = index // columns

        x = column * cell_width
        y = row * cell_height
        draw.rounded_rectangle(
            (x+10, y+10, x+170, y+190),
            radius=12,
            fill=(55,65,80,255)
        )
        icon_url = get_material_icon_url(material["material_id"])
        icon = download_material_icon(icon_url)
        bbox = icon.getbbox()
        if bbox is not None:
            icon = icon.crop(bbox)
        icon = icon.resize((100,100))
        canvas.paste(icon, (x+40, y+20), icon)

        draw.text(
            (x+90, y+135),
            name,
            font= font,
            fill=(255,255,255,255),
            anchor = "mm"
        )

        draw.text(
            (x+90, y+165),
            f"× {quantity:,}",
            font= font,
            fill=(255,220,120,255),
            anchor= "mm"
        )
    return canvas

