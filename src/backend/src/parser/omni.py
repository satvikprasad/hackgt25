from typing import Dict
import pyautogui

import os
import io
import base64

from dotenv import load_dotenv

from io import BytesIO

load_dotenv(f'{os.path.dirname(os.path.realpath(__file__))}/../../../../.env')

from util.utils import get_som_labeled_img, check_ocr_box, get_caption_model_processor, get_yolo_model
from ultralytics import YOLO
from PIL import Image, ImageOps
from PIL.Image import Image as TImage

import matplotlib.pyplot as plt

from openai import OpenAI

class Omni:
    def __init__(self):
        omniparser_dir = f'{os.path.dirname(os.path.realpath(__file__))}/../../OmniParser'

        self.openai_client = OpenAI(
            api_key=os.getenv("OPEN_API_KEY")
        )

        device = 'cpu'
        model_path=f'{omniparser_dir}/weights/icon_detect/model.pt'
        self.som_model = get_yolo_model(model_path)
        self.som_model.to(device)
        self.caption_model_processor = get_caption_model_processor(model_name="florence2", model_name_or_path=f"{omniparser_dir}/weights/icon_caption_florence", device=device)


    def gen_boxes(self, image: TImage, quadrant: int) -> tuple[TImage, dict[str, tuple[float, float, float, float]], tuple[int, int], tuple[int, int]]:
        print(image.size)

        left = ((quadrant - 1) % 3) * image.width/3
        top = ((quadrant - 1) // 3) * image.height/3

        quad_im = image.crop((left, top, left + image.width/3, top + image.height/3)).convert("RGB")
        quad_im = ImageOps.expand(quad_im, border=50, fill=(0, 0, 0))

        box_overlay_ratio = max(image.size) / 3200
        draw_bbox_config = {
            'text_scale': 1.3 * box_overlay_ratio,
            'text_thickness': max(int(2 * box_overlay_ratio), 1),
            'text_padding': max(int(3 * box_overlay_ratio), 1),
            'thickness': max(int(3 * box_overlay_ratio), 1),
            }
        BOX_TRESHOLD = 0.05

        ocr_bbox_rslt, is_goal_filtered = check_ocr_box(quad_im, display_img = False, output_bb_format='xyxy', goal_filtering=None, easyocr_args={'paragraph': False, 'text_threshold':0.9}, use_paddleocr=True)
        text, ocr_bbox = ocr_bbox_rslt

        dino_labled_img, label_coordinates, parsed_content_list = get_som_labeled_img(quad_im, self.som_model, BOX_TRESHOLD = BOX_TRESHOLD, output_coord_in_ratio=True, ocr_bbox=ocr_bbox,draw_bbox_config=draw_bbox_config, caption_model_processor=self.caption_model_processor, ocr_text=text,use_local_semantics=False, iou_threshold=0.7, scale_img=False, batch_size=128)

        plt.figure(figsize=(15,15))

        image_boxed = Image.open(io.BytesIO(base64.b64decode(dino_labled_img)))
        plt.axis('off')

        plt.imshow(image_boxed)

        image_boxed.show()

        return image_boxed, label_coordinates, (int(left), int(top)), (image.width, image.height)

    def detect_box(self, image: TImage, label_coordinates, offset: tuple[int, int], original_dim: tuple[int, int], object: str) -> tuple[int, int]:
        prompt = f"""
        This is an image showing a portion of the user's desktop, with relevant interactable buttons outlined and labelled with their ids. The label for a bounding box is located above the bounding box, in the same color as the border. Your job is to identify which one of these bounding boxes contains {object}. Respond with a single number, which should be the correct bounding box's id. Your response should only be a single number. You are not allowed to fail.
        """

        print(prompt)

        buffered = BytesIO()
        image.save(buffered, format="JPEG")

        imgb64 = base64.b64encode(buffered.getvalue()).decode("utf-8")

        response = self.openai_client.responses.create(
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
                        "image_url": f"data:image/jpeg;base64,{imgb64}"
                    }
                ]
            }]
        )

        print(response.output)

        box = '1'

        for elem in response.output:
            if (elem.type == "message"):
                box = elem.content[0].text
                break

        print(box)

        x, y, width, height = label_coordinates[box]
        screen_width, screen_height = pyautogui.size()

        screen_coord = ((x + width/2)*image.width - 50 + offset[0], (y + height/2)*image.height - 50 + offset[1])
        screen_coord = (screen_coord[0]/original_dim[0] * screen_width, screen_coord[1]/original_dim[1] * screen_height)

        pyautogui.moveTo(screen_coord[0], screen_coord[1], 3)

        return screen_coord

    def infer_coords(self, image: TImage, quadrant: int, entity: str) -> tuple[int, int]:
        image, labels, offset, dims = omni.gen_boxes(image, quadrant)
        return omni.detect_box(image, labels, offset, dims, entity)

omni = Omni()
print(omni.infer_coords(pyautogui.screenshot(), 3, "Control center icon, positioned to the left of the dates, looks like two stacked toggles."))
