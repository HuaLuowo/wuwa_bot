from PIL import Image, ImageDraw, ImageFont

def create_sonata_image(cost_groups):
    columns = 6
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
        current_y += section_header_height
        current_y += rows_per_cost[cost] * cell_height
        current_y += section_gap