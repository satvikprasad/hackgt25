import os
import io
import json
import base64
import subprocess
from threading import Event
from dotenv import load_dotenv
import gevent
import pyautogui
import time
from enum import Enum
import sys

load_dotenv("../../.env")

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))

import omni
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("OPEN_API_KEY")
)

from tesseractclient import click_text_percent, image_embeddings, normalize_data

from PIL import ImageDraw, ImageFont
from PIL.Image import Image
from PIL import Image

# from io import BytesIO
# import base64

def draw_grid_with_ids(im):
    w, h = im.size
    draw = ImageDraw.Draw(im)

    font = ImageFont.load_default(100.0)

    cols, rows = 3, 3
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

'''
def fetch_grid(image, object: str, desc: str):
    image = image.convert("RGB")

    buffered = BytesIO()
    image.save(buffered, format="JPEG")

    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")

    prompt = f"""
By looking at the image, respond in one line with an array of numbers that correspond to the numbered boxes I should check for the {object}, that is situated {desc}. Each number in the array should correspond to a box with the appropriate number. Return this in the form \"[1, 2, 3, ....]\". Don't guess, actually analyse the image. Your response should only contain an array, no words, no paragraphs.

                        For example, if I tell you to search for the 'Google new tab button', don't assume that the button will be in the top right because fullscreen windows have it in the top right. I want you to actually SEARCH for the button and ensure that the button is in the box you select.
"""

    print(prompt)

    response = client.responses.create(
            model="gpt-5",
            input=[{
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": prompt,
                    },
                    {
                        "type": "input_image",
                        "image_url": f"data:image/jpeg;base64,{img_str}"
                    }
                ]
            }]
        )

    for msg in response.output:
        if msg.type == "message":
            list_str = str(msg.content[0].to_dict()['text'])

            print(list_str[1:len(list_str) - 1])
'''

def code_please(prompt: str, reassess_text : str = ""):

    content = ""
    try:
        with open("./src/parser/prompt.txt", 'r', encoding='utf-8') as file:
            content = file.read()
    except Exception as e:
        pass

    content = content.replace("[instruction]", prompt)
    if reassess_text != "":
        content += """
        IF THIS INSTRUCTION HAS ALREADY BEEN SATISFIED, COMPLETE RIGHT NOW.

        Your reassessment from last time is as follows:
        """

    img = pyautogui.screenshot()

    pil_image = draw_grid_with_ids(img)

    #pil_image.show()

    # 2. FIX: Convert the image from RGBA to RGB (dropping the transparency).
    #    This is REQUIRED before saving as a JPEG.
    if pil_image.mode == 'RGBA':
        # Create a white background image
        background = Image.new('RGB', pil_image.size, (255, 255, 255))
        # Paste the RGBA image onto the white background
        background.paste(pil_image, (0, 0), pil_image)
        # Use the new RGB image for saving
        pil_image = background

    # If a simple conversion is preferred (which just removes the alpha channel):
    # pil_image = pil_image.convert('RGB')

    # 3. Create an in-memory binary stream (buffer)
    buffer = io.BytesIO()

    # 4. Save the RGB Image to the buffer as a JPEG file.
    pil_image.save(buffer, format='jpeg') # This will now work as pil_image is RGB

    # 5. Get the bytes from the buffer
    image_bytes = buffer.getvalue()

    # 6. Encode the bytes to Base64
    base64_encoded_image = base64.b64encode(image_bytes).decode('utf-8')

    # 7. Construct the final data URL string
    print("Starting programming")

    text_embeddings = normalize_data()

    image_url = f"data:image/jpeg;base64,{base64_encoded_image}"
    response = client.responses.create(
        model="gpt-5",
        input = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": content
                    },
                    {
                        "type": "input_text",
                        "text": text_embeddings
                    },
                    {
                        "type": "input_image",
                        "image_url": image_url
                    }
                ]
            }
        ]
    )

    print("Programming complete")
    print(response.output[1].content[0].text)
    return response.output[1].content[0].text

def omni_parse(screen: Image, quadrant: int, object: str, position_desc: str):
    left = ((quadrant - 1) % 3) * screen.width / 3
    top = ((quadrant - 1) // 3) * screen.height / 3

    screen.crop((left, top, left + screen.width / 3, top + screen.height / 3))

def parse_response(text : str):
    lines = text.split("\n")
    commands = []
    for line in lines:
        line = line.strip(" #")
        if line.split(" ")[0] == "WAIT":
            commands.append((Actions.WAIT, float(line.split(" ")[1])))
        elif line.split(" ")[0] == "REQUEST_MOVE":
            parts = line.split(" ")
            commands.append((Actions.REQUEST_MOVE, (int(line.split(" ")[1]), " ".join(line.split(" ")[2:]))))
        elif line.split(" ")[0] == "MOUSE_DOWN":
            commands.append((Actions.MOUSE_DOWN, line.split(" ")[1]))
        elif line.split(" ")[0] == "MOUSE_UP":
            commands.append((Actions.MOUSE_UP, line.split(" ")[1]))
        elif line.split(" ")[0] == "TYPE":
            commands.append((Actions.TYPE, " ".join(line.split(" ")[1:])))
        elif line.split(" ")[0] == "KEY_DOWN":
            commands.append((Actions.KEY_DOWN, line.split(" ")[1]))
        elif line.split(" ")[0] == "KEY_UP":
            commands.append((Actions.KEY_UP, line.split(" ")[1]))
        elif line.split(" ")[0] == "SCROLL_UP":
            commands.append((Actions.SCROLL_UP, int(line.split(" ")[1])))
        elif line.split(" ")[0] == "SCROLL_DOWN":
            commands.append((Actions.SCROLL_DOWN, int(line.split(" ")[1])))
        elif line.split(" ")[0] == "REASSESS":
            commands.append((Actions.REASSESS, " ".join(line.split(" ")[1:])))
        elif line.split(" ")[0] == "COMPLETE":
            commands.append((Actions.COMPLETE, " ".join(line.split(" ")[1:])))
        elif line.split(" ")[0] == "STOP":
            commands.append((Actions.STOP, " ".join(line.split(" ")[1:])))
        elif line.split(" ")[0] == "TEXT_MOVE":
            commands.append((Actions.TEXT_MOVE, (int(line.split(" ")[1]), int(line.split(" ")[2]))))
        elif line.split(" ")[0] == "EMAIL":
            commands.append((Actions.EMAIL, (line.split(" ")[1], " ".join(line.split(" ")[2:]))))

    return commands

class Actions(Enum):
    WAIT = 0
    REQUEST_MOVE = 1
    MOUSE_DOWN = 2
    MOUSE_UP = 3
    TYPE = 4
    KEY_DOWN = 5
    KEY_UP = 6
    SCROLL_UP = 7
    SCROLL_DOWN = 8
    REASSESS = 9
    COMPLETE = 10
    STOP = 11

    TEXT_MOVE = 12

    EMAIL = 13

class GUIClient:
    def __init__(self, socketio, commands : list[tuple[Actions, any]], content : str):
        self.socketio = socketio
        self.commands = commands
        self.content = content
        self.mastra_process = None

        for i in range(len(self.commands)):
            if not self.verify(i):
                raise ValueError(f"Invalid command at index {i}: {self.commands[i]}")

        self.index = 0
        self.repeat_count = 0

    def append_commands(self, new_commands : list[tuple[Actions, any]]):
        self.repeat_count += 1
        for cmd in new_commands:
            self.commands.append(cmd)
            if not self.verify(len(self.commands) - 1):
                raise ValueError(f"Invalid command at index {len(self.commands) - 1}: {cmd}")

    def verify(self, index : int):
        if index < 0 or index >= len(self.commands):
            raise IndexError("Index out of range")

        action, value = self.commands[index]

        if action == Actions.MOUSE_DOWN: #value = [(LEFT or RIGHT), (time)]
            if not (isinstance(value, str)):
                return False
        elif action == Actions.MOUSE_UP:
            if not isinstance(value, str):
                return False
        elif action == Actions.TYPE:
            if not isinstance(value, str):
                return False
        elif action in [Actions.KEY_DOWN, Actions.KEY_UP]:
            if not isinstance(value, str):
                return False
        elif action in [Actions.SCROLL_UP, Actions.SCROLL_DOWN]:
            if not isinstance(value, int):
                return False
        elif action == Actions.STOP:
            if not isinstance(value, str):
                return False
        elif action == Actions.COMPLETE:
            if not isinstance(value, str):
                return False
        elif action == Actions.REQUEST_MOVE:
            if not (isinstance(value, tuple) and len(value) == 2 and isinstance(value[0], int) and isinstance(value[1], str)):
                return False
        elif action == Actions.REASSESS:
            if not isinstance(value, str):
                return False
        elif action == Actions.WAIT:
            if not (isinstance(value, (int, float)) and value >= 0):
                return False
        elif action == Actions.TEXT_MOVE:
            if not (isinstance(value, tuple) and len(value) == 2 and isinstance(value[0], int) and isinstance(value[1], int)):
                return False
        elif action == Actions.EMAIL:
            if not (isinstance(value, tuple) and len(value) == 2 and isinstance(value[0], str) and isinstance(value[1], str)):
                return False

        return True

    def step(self) -> int:
        if self.index >= len(self.commands):
            raise IndexError("No more commands to execute")

        action, value = self.commands[self.index]

        if action == Actions.MOUSE_DOWN:
            if value.lower() == "left":
                print("Mouse was clicked")
                pyautogui.mouseDown(button='left')
            elif value.lower() == "right":
                pyautogui.mouseDown(button='right')
        elif action == Actions.MOUSE_UP:
            if value.lower() == "left":
                print("Mouse was released")
                pyautogui.mouseUp(button='left')
            elif value.lower() == "right":
                pyautogui.mouseUp(button='right')
        elif action == Actions.TYPE:
            pyautogui.typewrite(value, 0.1)
        elif action == Actions.KEY_DOWN:
            pyautogui.keyDown(value)
        elif action == Actions.KEY_UP:
            pyautogui.keyUp(value)
        elif action == Actions.SCROLL_UP:
            pyautogui.scroll(value)
        elif action == Actions.SCROLL_DOWN:
            pyautogui.scroll(-value)
        elif action == Actions.WAIT:
            pyautogui.sleep(value)
        elif action == Actions.REQUEST_MOVE:
            print("Requesting move....")
            coords = omni.omni.infer_coords(pyautogui.screenshot(), quadrant=value[0], entity=value[1])

            print(f"Moving to {coords}")

            pyautogui.moveTo(coords[0], coords[1], 0.3)

            time.sleep(0.5)
        elif action == Actions.STOP:
            self.socketio.emit("error", { "error": value })
            gevent.sleep(0)

            return -1
        elif action == Actions.COMPLETE:
            self.socketio.emit("complete", { "message": value })
            gevent.sleep(0)

            return 1
        elif action == Actions.REASSESS:
            self.socketio.emit('reassess', { 'response': value })
            gevent.sleep(0)

            cmds = parse_response(code_please(self.content, value))
            print("New commands:", cmds)
            self.append_commands(cmds)
        elif action == Actions.TEXT_MOVE:
            pyautogui.moveTo(value[0], value[1], 0.3)
        elif action == Actions.EMAIL:
            mastra_wd = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../../../mastra")
            cmd = f"cd {mastra_wd} && npx tsx ./manualEmail.ts \"email {value[0]} about {value[1]}\" &"
            print(cmd)
            os.system(cmd)

        self.index += 1
        return 0

