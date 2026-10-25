from PIL import Image, ImageDraw, ImageFont
from PIL import UnidentifiedImageError
import requests
from io import BytesIO

def create_sonata_image(cost_groups):
    columns = min(
        6,
        max(1, *(len(cost_groups[cost]) for cost in [4,3,1]))
    )
    icon_size = 80
    cell_width = 120
    cell_height = 120
    padding = 20
    image_width = columns * cell_width + padding*2
    rows_per_cost = {}

    for cost in [4,3,1]:
        count = len(cost_groups[cost])
        rows_per_cost[cost] = max(1, (count+ columns -1) // columns)

    section_header_height = 40
    section_gap = 20
    image_height = padding * 2

    for cost in [4,3,1]:
        image_height += section_header_height
        image_height += rows_per_cost[cost] * cell_height
        image_height += section_gap

    image = Image.new(
        "RGB",
        (image_width, image_height),
        (30,30,35)
    )
    draw = ImageDraw.Draw(image)
    font_path = "C:/Windows/Fonts/msjh.ttc"
    title_font = ImageFont.truetype(font_path, 24)
    name_font = ImageFont.truetype(font_path, 16)

    current_y = padding
    for cost in [4,3,1]:
        draw.text(
            (padding, current_y),
            f"COST {cost}",
            font= title_font,
            fill=(255,255,255)
        )
        for index, echo in enumerate(cost_groups[cost]):
            row = index // columns
            col = index % columns
            x = padding + col * cell_width
            y = current_y + section_header_height + row * cell_height
            image_url = echo.get("image")
            if image_url:
                try:
                    response = requests.get(image_url , timeout=10)
                    response.raise_for_status()

                    echo_image = Image.open(BytesIO(response.content)).convert("RGBA")
                    echo_image.thumbnail(
                        (icon_size, icon_size),
                        Image.Resampling.LANCZOS
                    )

                    image_x = x +(cell_width - echo_image.width) // 2
                    image.paste(
                        echo_image,
                        (image_x,y),
                        echo_image
                    )
                except (requests.RequestException, UnidentifiedImageError, OSError) as error:
                    print(f"聲骸圖片處理失敗:{echo.get('name')}， 原因: {error}")

            echo_name = echo.get("name", "未知聲骸")
            text_width = draw.textlength(echo_name, font=name_font)
            max_text_width = cell_width - 10
            if text_width > max_text_width:
                while echo_name and draw.textlength(echo_name + "...", font=name_font) > max_text_width:
                    echo_name = echo_name[:-1]
                echo_name += "..."
            text_width = draw.textlength(echo_name, font=name_font)
            text_x = x + (cell_width - text_width) / 2
            draw.text((text_x,y + icon_size + 5), echo_name, font=name_font, fill=(255,255,255))
        current_y += section_header_height
        current_y += rows_per_cost[cost] * cell_height
        current_y += section_gap

    output = BytesIO()
    image.save(output, format = "PNG")
    output.seek(0)
    return output