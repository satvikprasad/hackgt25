import pyautogui
import requests

from openai import OpenAI

client = OpenAI(
        api_key=""
        )

from PIL import ImageDraw, ImageFont

from io import BytesIO
import base64

def draw_grid_with_ids(im):
    w, h = im.size
    draw = ImageDraw.Draw(im)

    font = ImageFont.load_default(100.0)

    cols, rows = 4, 4
    line_color = "red"
    line_width = 2

    # Draw the grid lines
    for i in range(1, cols):
        x = i * w / cols
        draw.line([(x, 0), (x, h)], fill=line_color, width=line_width)
    for j in range(1, rows):
        y = j * h / rows
        draw.line([(0, y), (w, y)], fill=line_color, width=line_width)

    cell_w = w / cols
    cell_h = h / rows
    counter = 1
    for row in range(rows):
        for col in range(cols):
            # approximate center of each cell
            x0 = col * cell_w
            y0 = row * cell_h
            cx = x0 + cell_w / 2
            cy = y0 + cell_h / 2

            text = str(counter)

            # Use textbbox to get bounding box of text
            left, top, right, bottom = draw.textbbox((0, 0), text, font=font)
            text_w = right - left
            text_h = bottom - top

            # Calculate where to place text so it's centered
            text_x = cx - text_w / 2
            text_y = cy - text_h / 2

            draw.text((text_x, text_y), text, fill=(255, 0, 0, 128), font=font)

            counter += 1

    return im

def fetch_grid(image):
    image = image.convert("RGB")

    buffered = BytesIO()
    image.save(buffered, format="JPEG")

    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")

    response = client.responses.create(
            model="gpt-5",
            input=[{
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": """
                        By looking at the image, respond in one line with an array of numbers that correspond to the numbered boxes I should check for the 'page refresh' button. Each number in the array should correspond to a box with the appropriate number. Return this in the form \"[1, 2, 3, ....]\". Don't guess, actually analyse the image. Your response should only contain an array, no words, no paragraphs.
                        """,
                    },
                    {
                        "type": "input_image",
                        "image_url": f"data:image/jpeg;base64,{img_str}"
                    }
                ]
            }]
        )

    print(response)

capture = pyautogui.screenshot()

gridded_capture = draw_grid_with_ids(capture)

gridded_capture.show()

fetch_grid(gridded_capture)
