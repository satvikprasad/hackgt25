import sys

import pyautogui

import os

from util.utils import get_som_labeled_img, check_ocr_box, get_caption_model_processor, get_yolo_model
import torch
from ultralytics import YOLO
from PIL import Image
from PIL.Image import Image

class Omni:
    def __init__(self):
        device = 'cpu'
        model_path=f'{os.path.dirname(os.path.realpath(__file__))}/../../OmniParser/weights/icon_detect/model.pt'

        self.som_model = get_yolo_model(model_path)
        self.som_model.to(device)

    def gen_boxes(self, image: Image, quadrant: int):
        left = ((quadrant - 1) % 3) * image.width/3
        top = ((quadrant - 1) // 3) * image.height/3

        quad_im = image.crop((left, top, left + image.width/3, top + image.height/3)).convert("RGB")

        quad_im.show()

        box_overlay_ratio = max(image.size) / 3200
        draw_bbox_config = {
            'text_scale': 1.5 * box_overlay_ratio,
            'text_thickness': max(int(2 * box_overlay_ratio), 1),
            'text_padding': max(int(3 * box_overlay_ratio), 1),
            'thickness': max(int(3 * box_overlay_ratio), 1),
            }
        BOX_TRESHOLD = 0.05

        ocr_bbox_rslt, is_goal_filtered = check_ocr_box(quad_im, display_img = False, output_bb_format='xyxy', goal_filtering=None, easyocr_args={'paragraph': False, 'text_threshold':0.9}, use_paddleocr=True)
        text, ocr_bbox = ocr_bbox_rslt

        dino_labled_img, label_coordinates, parsed_content_list = get_som_labeled_img(quad_im, self.som_model, BOX_TRESHOLD = BOX_TRESHOLD, output_coord_in_ratio=True, ocr_bbox=ocr_bbox,draw_bbox_config=draw_bbox_config, ocr_text=text,use_local_semantics=False, iou_threshold=0.7, scale_img=False, batch_size=128)

omni = Omni()
omni.gen_boxes(pyautogui.screenshot(), 3)
