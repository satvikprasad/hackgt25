import pyautogui
import pytesseract
from PIL import Image

def click_text_percent(target_text, quadrant=0, debug=False):
    """
    Find `target_text` on screen using OCR and click it.
    Uses percent-based coordinates (relative to OCR image), 
    then maps back to full screen size.
    
    Args:
        target_text (str): Text to find and click.
        quadrant (int): 1-9 (3x3 grid) or 0 for full screen.
        debug (bool): Show OCR boxes with percentages.
    """
    # Screenshot
    image = pyautogui.screenshot()
    screen_w, screen_h = pyautogui.size()  # actual screen size

    # Determine quadrant
    if quadrant == 0:
        left, top, width, height = 0, 0, image.width, image.height
    else:
        left = ((quadrant - 1) % 3) * image.width / 3
        top = ((quadrant - 1) // 3) * image.height / 3
        width = image.width / 3
        height = image.height / 3

    quad_im = image.crop((left, top, left + width, top + height))

    # OCR
    text_data = pytesseract.image_to_data(quad_im, output_type=pytesseract.Output.DICT)

    for i, word in enumerate(text_data['text']):
        if word.strip() != "" and target_text.lower() in word.lower():
            # Center coordinates (relative to cropped image)
            cx = text_data['left'][i] + text_data['width'][i] / 2
            cy = text_data['top'][i] + text_data['height'][i] / 2

            # Convert to percentage of OCR image
            cx_pct = cx / width
            cy_pct = cy / height

            # Map back to full screen coordinates
            screen_x = int((left / image.width + cx_pct * (width / image.width)) * screen_w)
            screen_y = int((top / image.height + cy_pct * (height / image.height)) * screen_h)

            pyautogui.moveTo(screen_x, screen_y, 0.3)
            return

